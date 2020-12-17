"""
生成小红书h5请求头中的X-Sign
"""

import hashlib
from urllib import parse


def hash_md5(s):
    """
    md5加密
    """
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def get_sign(path, params):
    """
    生成签名
    """
    content = path + '?' + parse.urlencode(params) + 'WSUDD'
    sign = 'X' + hash_md5(content)
    return sign
