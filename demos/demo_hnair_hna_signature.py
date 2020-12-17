from hnair.hna_signature import get_sign


def main():
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
    main()
