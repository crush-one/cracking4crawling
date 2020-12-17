"""
海南航空App签名
"""

import hmac
from hashlib import sha1

__apk_version__ = '8.5.1'


def get_sign(data=None, token='', secret='21047C596EAD45209346AE29F0350491'):
    """
    生成签名
    """
    slat = 'F6B15ABD66F91951036C955CB25B069F'

    # 取common、data下面全部value，排序后拼接，list类型不参与拼接
    d = {**data['common'], **data['data']}
    for k, v in d.items():
        if isinstance(v, bool):
            d[k] = 'true' if v else 'false'
        elif isinstance(v, list) or isinstance(v, dict):
            d[k] = ''
    content = ''.join([token, ''.join([str(d[k]) for k in sorted(d.keys())]), slat])

    h = hmac.new(secret.encode(), content.encode(), sha1)
    return h.hexdigest().upper()
