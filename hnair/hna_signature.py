"""
海南航空App签名
"""

import hmac
from hashlib import sha1

APK_VERSION = '8.5.1'


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


def test():
    # 对请求的data进行签名
    data = {
        'common': {
            # common的内容
        },
        'data': {
            'adultCount': 1,
            'cabins': ['*'],
            'childCount': 0,
            'depDate': '2020-12-09',
            'dstCode': 'PEK',
            'infantCount': 0,
            'orgCode': 'YYZ',
            'tripType': 1,
            'type': 3
        }
    }

    # /user/ 路径下的接口需要登录，同时加签要传入token、secret（都由服务器返回）
    # token = ''
    # secret = ''

    # 生成签名
    sign = get_sign(data=data)

    print(sign)


if __name__ == '__main__':
    test()
