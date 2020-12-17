from xiaohongshu.x_sign import get_sign


def main():
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
    main()
