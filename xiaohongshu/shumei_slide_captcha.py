"""
数美滑块验证码破解验证
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
from requests.packages.urllib3 import disable_warnings

requests.packages.urllib3.disable_warnings()

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
from requests.packages.urllib3 import disable_warnings

requests.packages.urllib3.disable_warnings()

param_names = {}


def padding(b):
    """
    块填充
    """
    block_size = 8
    while len(b) % block_size:
        b += b'\0'
    return b


def split_args(s):
    """
    分割js参数
    """
    r = []
    a = ''
    i = 0
    while i < len(s):
        c = s[i]
        if c == ',' and (a[0] != '\'' or len(a) >= 2 and a[-1] == '\''):
            r.append(a)
            a = ''
        elif c:
            a += c
        i += 1
    r.append(a)
    return r


def hex2int(t):
    """
    十六进制字符串转int
    """
    return int(t, base=16)


def parser_param_names(script):
    """
    通过js解析出参数字段名
    """
    names = {}

    # 取所有参数名
    a = []
    for r in re.findall(r'function\((.*?)\)', script):
        if len(r.split(',')) > 100:
            a = split_args(r)
            break

    # 取所有传入的参数
    r = re.search(r';\)\)(.*?)\(}', script[::-1]).group(1)
    v = split_args(r[::-1])

    # 取接口字段名对应的参数变量
    d = r'{%s}' % ''.join([((',' if i else '') + '\'k{}\':([_x0-9a-z]*)'.format(i + 1)) for i in range(15)])

    k = []
    r = re.search(d, script)
    for i in range(15):
        k.append(r.group(i + 1))

    try:
        n = hex2int(v[a.index(re.search(r'arguments;.*?,(.*?)\);', script).group(1))]) // 2
    except ValueError:
        m = re.search(r'arguments;.*?,.*?,.*?]\((.*?),(.*?)\)', script)
        n = hex2int(v[a.index(m.group(1))]) // hex2int(v[a.index(m.group(2))])

    for i in range(n):
        v[i], v[n - 1 - i] = v[n - 1 - i], v[i]

    # 对接口字段的值进行对应
    for i, b in enumerate(k):
        t = v[a.index(b)].strip('\'')
        names['k{}'.format(i + 1)] = t if len(t) > 2 else t[::-1]

    return names


def get_encrypt_content(message, key, flag):
    """
    接口参数的加密、解密
    """
    des_obj = des(key.encode(), mode=ECB)
    if flag:
        content = padding(str(message).replace(' ', '').encode())
        return base64.b64encode(des_obj.encrypt(content)).decode('utf-8')
    return des_obj.decrypt(base64.b64decode(message)).decode('utf-8')


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


def get_mouse_action_params(distance, captcha_width, captcha_height):
    """
    生成鼠标行为相关的参数
    """
    tracks = get_tracks(distance)
    params = {
        param_names['k5']: round(distance / captcha_width, 2),
        param_names['k6']: get_tracks(distance),
        param_names['k7']: tracks[-1][-1] + random.randint(0, 100),
        param_names['k8']: captcha_width,
        param_names['k9']: captcha_height,
        param_names['k11']: 1,
        param_names['k12']: 0,
        param_names['k13']: -1,
        'act.os': 'android'
    }
    return params


def get_distance(fg, bg):
    """
    计算滑动距离
    """
    target = cv2.imdecode(np.asarray(bytearray(fg.read()), dtype=np.uint8), 0)
    template = cv2.imdecode(np.asarray(bytearray(bg.read()), dtype=np.uint8), 0)
    result = cv2.matchTemplate(target, template, cv2.TM_CCORR_NORMED)
    _, distance = np.unravel_index(result.argmax(), result.shape)
    return distance


def update_param_names(protocol_num, js_uri):
    """
    更新接口字段名
    """
    global param_names
    r = requests.get(js_uri, verify=False)
    names = parser_param_names(r.text)
    param_names = {
        'i': protocol_num,
        **names
    }


def conf_captcha(organization):
    """
    获取验证码设置
    """
    url = 'https://captcha.fengkongcloud.com/ca/v1/conf'

    params = {
        'organization': organization,
        'model': 'slide',
        'sdkver': '1.1.3',
        'rversion': '1.0.3',
        'appId': 'default',
        'lang': 'zh-cn',
        'channel': 'YingYongBao',
        'callback': 'sm_{}'.format(int(time.time() * 1000))
    }

    r = requests.get(url, params=params, verify=False)
    resp = json.loads(re.search(r'{}\((.*)\)'.format(params['callback']), r.text).group(1))

    return resp


def register_captcha(organization):
    """
    注册验证码
    """
    url = 'https://captcha.fengkongcloud.com/ca/v1/register'

    params = {
        'organization': organization,
        'channel': 'YingYongBao',
        'lang': 'zh-cn',
        'model': 'slide',
        'appId': 'default',
        'sdkver': '1.1.3',
        'data': '{}',
        'rversion': '1.0.3',
        'callback': 'sm_{}'.format(int(time.time() * 1000))
    }

    r = requests.get(url, params=params, verify=False)
    resp = json.loads(re.search(r'{}\((.*)\)'.format(params['callback']), r.text).group(1))

    return resp


def verify_captcha(organization, rid, key, distance, captcha_width, captcha_height):
    """
    提交验证
    """
    url = 'https://captcha.fengkongcloud.com/ca/v2/fverify'

    params = {
        'organization': organization,
        param_names['k1']: 'default',
        param_names['k2']: 'YingYongBao',
        param_names['k3']: 'zh-cn',
        'rid': rid,
        'rversion': '1.0.3',
        'sdkver': '1.1.3',
        'protocol': param_names['i'],
        'ostype': 'web',
        'callback': 'sm_{}'.format(int(time.time() * 1000))
    }

    params.update(get_mouse_action_params(distance, captcha_width, captcha_height))

    key = get_encrypt_content(key, 'sshummei', 0)

    for k, v in params.items():
        if len(k) == 2:
            params[k] = get_encrypt_content(v, key, 1)

    r = requests.get(url, params=params, verify=False)
    resp = json.loads(re.search(r'{}\((.*)\)'.format(params['callback']), r.text).group(1))

    return resp


def get_verify(organization, captcha_width=310, captcha_height=155):
    """
    进行验证
    """
    resp = conf_captcha(organization)
    protocol_num = re.search(r'build/v1.0.\d*-(.*?)/captcha-sdk.min.js', resp['detail']['js']).group(1)

    if not param_names.get('id') or protocol_num != param_names['i']:
        update_param_names(protocol_num, ''.join(['https://', resp['detail']['domains'][0], resp['detail']['js']]))

    resp = register_captcha(organization)

    rid = resp['detail']['rid']
    key = resp['detail']

    domain = resp['detail']['domains'][0]
    fg_uri = resp['detail']['fg']
    bg_uri = resp['detail']['bg']

    fg_url = ''.join(['http://', domain, fg_uri])
    bg_url = ''.join(['http://', domain, bg_uri])

    r = requests.get(fg_url, verify=False)
    fg = BytesIO(r.content)

    r = requests.get(bg_url, verify=False)
    bg = BytesIO(r.content)

    distance = get_distance(fg, bg)

    r = verify_captcha(organization, rid, key, int(distance / 600 * 310), captcha_width, captcha_height)

    return rid, r


def test():
    # 表示小红书
    organization = 'eR46sBuqF0fdw7KWFLYa'

    # rid是验证过程中响应的标示，r是最后提交验证返回的响应
    rid, r = get_verify(organization)

    print(rid, r)

    # riskLevel为PASS说明验证通过
    if r['riskLevel'] == 'PASS':
        # 这里需要向小红书提交rid
        # 具体可抓包查看，接口：/api/sns/v1/system_service/slide_captcha_check
        pass


if __name__ == '__main__':
    test()
