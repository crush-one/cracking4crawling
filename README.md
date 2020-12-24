# 小红书sign
一些爬虫相关的签名、验证码破解，目前已有脚本：

- [小红书App接口签名（shield）](#小红书App接口签名shield)（2020.12.02）
- [小红书滑块（数美）验证破解](#小红书滑块数美验证破解)（2020.12.02）

## 说明：

脚本按目标网站、App命名归档，每个脚本一般都是可以单独引入使用（除非调用了额外的用于加解密的js文件），使用方法可参考文档或demos目录下的样例代码。

## 使用方法：

### 小红书

#### 小红书App接口签名（shield）

shield是小红书App接口主要的签名，由path、params、xy_common_params、xy_platform_info、data拼接并加密生成。原始加密在libshield.so中，已用python还原。

```python
from urllib import parse

from xiaohongshu.shield import get_sign

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
```

#### 小红书滑块（数美）验证破解

小红书使用数美滑块验证码，验证过程为：获取验证码配置、获取验证码、提交验证，数美通过organization区分来源，完成后将通过的rid提交到小红书的接口。

具体实现细节：

- 协议更新：数美会定期自动更新js和接口参数字段（接口里所有“两个字母组成”的字段名都会在更新后变化），通过"/ca/v1/conf"接口返回的js路径可以判断协议版本（如"/pr/auto-build/v1.0.1-33/captcha-sdk.min.js"，表示协议版本号为33），脚本会加载js，并通过匹配js内容自动确认字段名，用于后续的接口请求。
- 验证参数：验证主要需要三个参数：位移比例、时间、轨迹，使用opencv中的matchTemplate函数计算距离，并随机生成相应的轨迹。
- 加密算法：提交验证的主要参数都需要加密，使用DES加密。
- 加密过程："/ca/v1/register"接口会返回一个参数k，使用"sshummei"作为key对它解密，解密后得到一个新key，再用这个key对接口参数进行加密。

注：~~当前的验证参数全部按照小红书App调整，用于其他验证（如小红书Web或其他网站、App），可能需要调整其中参数。~~（测试过数美官网首页的滑块验证，可通过）

```python
from xiaohongshu.shumei_slide_captcha import ShumeiSlideCaptchaSolver

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
```

