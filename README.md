# cracking4crawling
一些爬虫相关的签名、验证码破解，目前已有脚本：

- [小红书App接口签名（shield）](#小红书App接口签名shield)（2020.12.02）
- [小红书滑块（数美）验证破解](#小红书滑块数美验证破解)（2020.12.02）
- [小红书h5接口签名（X-Sign）](#小红书h5接口签名X-Sign)（2020.12.15）
- [海南航空App接口签名（hnairSign）](#海南航空App接口签名hnairSign)（2020.12.05）

## 说明：

脚本按目标网站、App命名归档，每个脚本一般都是可以单独导入使用（除非调用了额外的用于加解密的js文件），使用方法可参考文档或demos目录下的样例代码。

## 使用方法：

### 小红书

#### 小红书App接口签名（shield）

shield是小红书App接口主要的签名，由path、params、xy_common_params、xy_platform_info、data拼接并加密生成。原始加密在libshield.so中，已用python复现。

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
sign = get_sign(path=path, 
                params=params, 
                xy_common_params=xy_common_params, 
                xy_platform_info=xy_platform_info,
                data=data)
print(sign)
```

#### 小红书滑块（数美）验证破解

小红书使用数美滑块验证码，验证过程（获取验证码配置>获取验证码>提交验证）在数美的服务器（数美使用organization来识别被验证的网站、App）上进行，完成后将通过的rid提交到小红书的接口。

具体实现细节：

- 协议更新：数美会定期自动更新js和接口参数字段（接口里所有形似"ab"的字段名都会在更新中修改），通过"/ca/v1/conf"接口返回的js路径可以判断协议版本（如"/pr/auto-build/v1.0.1-33/captcha-sdk.min.js"，表示协议版本号为33），脚本会加载js，并通过解析js内容自动确认字段名，用于后续的接口请求。
- 验证参数：验证主要需要三个参数：位移比率、时间、轨迹，使用opencv中的matchTemplate函数计算距离，并随机生成相应的轨迹。
- 调用加密：提交验证的主要参数都需要加密，使用DES加密。
- 加密过程："/ca/v1/register"接口会返回一个参数k，使用"sshummei"作为key对它解密，结果为加密参数所需的key，再对参数进行加密。

注：当前的验证参数全部按照小红书App调整，用于其他验证（如小红书Web或其他网站、App），可能需要调整其中参数。

```python
from xiaohongshu.shumei_slide_captcha import get_verify

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

#### 小红书h5接口签名（X-Sign）

小红书App中的一些页面使用h5实现，相关接口请求头需要带上X-Sign，X-Sign生成规则为：对接口路径、url参数进行拼接，在结尾加上字符串“WSUDD”，对组合之后的字符串进行md5加密，最后在结果开头加上“X”。

```python
from xiaohongshu.x_sign import get_sign

# 对接口路径、url参数进行签名
path = '/fe_api/burdock/v2/page/5a43849c8000862471d1625e/media'

params = {
    'page': 1,
    'pageSize': 20
}

# 生成签名
sign = get_sign(path, params)
print(sign)
```

### 海南航空

#### 海南航空App接口签名（hnairSign）

签名对象主要是请求的data，取common、data下的全部参数，按字典序排序进行拼接（list、dict类型不参与拼接），结尾加上slat，进行HMAC_SHA1加密生成。

注："/user/"下的接口加签时，会在拼接的内容前加上token，同时HMAC_SHA1加密会使用服务器返回的secret

```python
from hnair.hna_signature

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
```

