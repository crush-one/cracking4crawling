"""
小红书滑块（数美）破解
"""

import base64
import json
import random
import re
import time
from io import BytesIO

import cv2
import numpy as np
import requests
from pyDes import des, ECB


class ShumeiSlideCaptchaSolver(object):

    def __init__(self, organization, os_type='android', captcha_width=310, captcha_height=155):
        self.organization = organization
        self.os_type = os_type

        self.captcha_width = captcha_width
        self.captcha_height = captcha_height

        # 版本号不同，接口字段也不同
        self.protocol_no = None
        self.params_map = {}

    @staticmethod
    def request(url, params):
        """
        发送请求
        """
        params['callback'] = 'sm_{}'.format(int(time.time() * 1000))
        r = requests.get(url, params=params)
        resp = json.loads(re.search(r'{}\((.*)\)'.format(params['callback']), r.text).group(1))
        return resp

    @staticmethod
    def padding(b):
        """
        块填充
        """
        block_size = 8
        while len(b) % block_size:
            b += b'\0'
        return b
    
    @staticmethod
    def split_args(s):
        """
        分割参数
        """
        r = []
        a = ''
        for i, c in enumerate(s):
            if c == ',' and (not a.startswith('\'') or (len(a) >= 2 and a.endswith('\''))):
                r.append(a)
                a = ''
            elif c:
                a += c
        r.append(a)
        return r

    @staticmethod
    def hex2int(t):
        """
        十六进制字符串转int
        """
        return int(t, base=16)

    @staticmethod
    def get_distance(fg, bg):
        """
        计算滑动距离
        """
        target = cv2.imdecode(np.asarray(bytearray(fg.read()), dtype=np.uint8), 0)
        template = cv2.imdecode(np.asarray(bytearray(bg.read()), dtype=np.uint8), 0)
        result = cv2.matchTemplate(target, template, cv2.TM_CCORR_NORMED)
        _, distance = np.unravel_index(result.argmax(), result.shape)
        return distance

    @staticmethod
    def get_tracks(distance):
        """
        生成随机的轨迹
        """
        tracks = []

        y = 0
        v = 0
        t = 1
        current = 0
        mid = distance * 3 / 4
        exceed = 20
        z = t

        tracks.append([0, 0, 1])

        while current < (distance + exceed):
            if current < mid / 2:
                a = 15
            elif current < mid:
                a = 20
            else:
                a = -30
            a /= 2
            v0 = v
            s = v0 * t + 0.5 * a * (t * t)
            current += int(s)
            v = v0 + a * t

            y += random.randint(-5, 5)
            z += 100 + random.randint(0, 10)

            tracks.append([min(current, (distance + exceed)), y, z])

        while exceed > 0:
            exceed -= random.randint(0, 5)
            y += random.randint(-5, 5)
            z += 100 + random.randint(0, 10)
            tracks.append([min(current, (distance + exceed)), y, z])

        return tracks

    def parser_captcha_sdk_js(self, content):
        """
        解析验证码的js，确定字段名
        """
        params_map = {}

        # 取主函数的参数名
        g_names = []
        for r in re.findall(r'function\((.*?)\)', content):
            if len(r.split(',')) > 100:
                g_names = self.split_args(r)
                break

        # 取主函数调用传值
        r = re.search(r';\)\)(.*?)\(}', content[::-1]).group(1)[::-1]
        g_values = self.split_args(r)

        n = 0
        for v in g_values:
            try:
                v = self.hex2int(v)
                if abs(len(g_values) - v) < abs(len(g_values) - n):
                    n = v
            except ValueError:
                pass

        for i in range(n // 2):
            g_values[i], g_values[n - 1 - i] = g_values[n - 1 - i], g_values[i]

        # 取接口字段名（k1-k15）对应的参数
        keys = []
        p = r'{%s}' % ''.join([((',' if i else '') + '\'k{}\':([_x0-9a-z]*)'.format(i + 1)) for i in range(15)])
        r = re.search(p, content)
        for i in range(15):
            keys.append(r.group(i + 1))

        # 对接口字段的值进行对应
        for i, b in enumerate(keys):
            t = g_values[g_names.index(b)].strip('\'')
            params_map['k{}'.format(i + 1)] = t if len(t) > 2 else t[::-1]

        return params_map

    def get_encrypt_content(self, message, key, is_encrypt):
        """
        接口参数的加密、解密
        """
        des_obj = des(key.encode(), mode=ECB)
        if not is_encrypt:
            return des_obj.decrypt(base64.b64decode(message)).decode('utf-8')
        content = self.padding(str(message).replace(' ', '').encode())
        return base64.b64encode(des_obj.encrypt(content)).decode('utf-8')

    def get_mouse_action_params(self, distance):
        """
        生成鼠标行为相关的参数
        """
        tracks = self.get_tracks(distance)
        params = {
            self.params_map['k5']: round(distance / self.captcha_width, 2),
            self.params_map['k6']: tracks,
            self.params_map['k7']: tracks[-1][-1] + random.randint(0, 100),
            self.params_map['k8']: self.captcha_width,
            self.params_map['k9']: self.captcha_height,
            self.params_map['k11']: 1,
            self.params_map['k12']: 0,
            self.params_map['k13']: -1,
            'act.os': self.os_type
        }
        return params

    def conf_captcha(self):
        """
        获取验证码设置
        """
        url = 'https://captcha.fengkongcloud.com/ca/v1/conf'

        params = {
            'organization': self.organization,
            'model': 'slide',
            'sdkver': '1.1.3',
            'rversion': '1.0.3',
            'appId': 'default',
            'lang': 'zh-cn',
            'channel': 'DEFAULT'
        }

        resp = self.request(url, params)
        return resp

    def register_captcha(self):
        """
        注册验证码
        """
        url = 'https://captcha.fengkongcloud.com/ca/v1/register'

        params = {
            'organization': self.organization,
            'channel': 'DEFAULT',
            'lang': 'zh-cn',
            'model': 'slide',
            'appId': 'default',
            'sdkver': '1.1.3',
            'data': '{}',
            'rversion': '1.0.3'
        }

        resp = self.request(url, params)
        return resp

    def verify_captcha(self, rid, key, distance):
        """
        提交验证
        """
        url = 'https://captcha.fengkongcloud.com/ca/v2/fverify'

        params = {
            'organization': self.organization,
            self.params_map['k1']: 'default',
            self.params_map['k2']: 'DEFAULT',
            self.params_map['k3']: 'zh-cn',
            'rid': rid,
            'rversion': '1.0.3',
            'sdkver': '1.1.3',
            'protocol': self.protocol_no,
            'ostype': 'web'
        }

        params.update(self.get_mouse_action_params(distance))

        key = self.get_encrypt_content(key, 'sshummei', 0)

        # 字段名长度为2的都是需要加密的
        for k, v in params.items():
            if len(k) == 2:
                params[k] = self.get_encrypt_content(v, key, 1)

        resp = self.request(url, params)
        return resp

    def get_verify(self):
        """
        进行验证
        """
        resp = self.conf_captcha()

        protocol_no = re.search(r'build/v1.0.\d*-(.*?)/captcha-sdk.min.js', resp['detail']['js']).group(1)

        # 如果版本号更新，则根据js更新接口字段名
        if protocol_no != self.protocol_no:
            # 获取验证码的js
            captcha_sdk_js_uri = ''.join(['https://', resp['detail']['domains'][0], resp['detail']['js']])
            r = requests.get(captcha_sdk_js_uri)

            captcha_sdk_js_content = r.text

            self.protocol_no = protocol_no
            self.params_map = self.parser_captcha_sdk_js(captcha_sdk_js_content)

        resp = self.register_captcha()

        # 验证id，加解密的key
        rid = resp['detail']['rid']
        key = resp['detail']['k']

        # 获取滑块图片
        domain = resp['detail']['domains'][0]
        fg_uri = resp['detail']['fg']
        bg_uri = resp['detail']['bg']

        fg_url = ''.join(['http://', domain, fg_uri])
        bg_url = ''.join(['http://', domain, bg_uri])

        r = requests.get(fg_url)
        fg = BytesIO(r.content)

        r = requests.get(bg_url)
        bg = BytesIO(r.content)

        # 计算滑动距离
        distance = self.get_distance(fg, bg)

        resp = self.verify_captcha(rid, key, int(distance / 600 * 310))
        risk_level = resp['riskLevel']

        return rid, risk_level
