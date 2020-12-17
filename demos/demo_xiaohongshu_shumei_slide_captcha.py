from xiaohongshu.shumei_slide_captcha import ShumeiSlideCaptchaSolver


def main():
    # organization为验证来源，这里表示小红书
    captcha_solver = ShumeiSlideCaptchaSolver(organization='eR46sBuqF0fdw7KWFLYa')

    # rid是验证过程中响应的标示，r是最后提交验证返回的响应
    rid, risk_level = captcha_solver.get_verify()

    # riskLevel为PASS说明验证通过
    if risk_level == 'PASS':
        # 这里需要向小红书提交rid
        # 具体可抓包查看，接口：/api/sns/v1/system_service/slide_captcha_check
        pass

    print(rid, risk_level)


if __name__ == '__main__':
    main()
