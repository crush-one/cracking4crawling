"""
生成小红书h5请求头中的X-Sign
"""

import hashlib
from urllib import parse


def hash_md5(s):
    """
    md5
    """
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def get_sign(path, params):
    """
    生成签名
    """
    content = path + '?' + parse.urlencode(params) + 'WSUDD'
    sign = 'X' + hash_md5(content)
    return sign


def test():
    # 对接口路径、url参数进行签名
    path = '/fe_api/burdock/v2/page/5a43849c8000862471d1625e/media'

    params = {
        'page': 1,
        'pageSize': 20
    }

    # 生成签名
    sign = get_sign(path, params)
    print(sign)


if __name__ == '__main__':
    test()
