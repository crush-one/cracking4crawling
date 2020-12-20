from urllib import parse

from xiaohongshu.shield import get_sign


def main():
    # 对接口路径、url参数、header中的xy-common-params、xy-platform-info、请求的data进行签名
    path = '/api/sns/v4/note/user/posted'
    params = parse.urlencode({'user_id': '5eeb209d000000000101d84a'})
    xy_common_params = parse.urlencode({})
    xy_platform_info = parse.urlencode({})
    data = parse.urlencode({})

    # 生成签名
    sign = get_sign(
        path=path,
        params=params,
        xy_common_params=xy_common_params,
        xy_platform_info=xy_platform_info,
        data=data
    )
    print(sign)


if __name__ == '__main__':
    main()