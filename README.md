# cracking4crawling
一些爬虫相关的签名、验证码破解，目前已有脚本：

- [小红书App接口签名（shield）](#小红书App接口签名（shield）)（2020.12.02）
- [小红书滑块（数美）验证破解](#小红书滑块（数美）验证破解)（2020.12.02）

## 说明：

脚本按目标网站、App命名归档，每个脚本一般都是可以单独导入使用（除非调用了额外的用于加解密的js文件），使用方法可阅读文档或参考其中的test函数。

## 使用方法：

### 小红书

#### 小红书App接口签名（shield）

shield是小红书App接口主要的签名，由path、params、data、xy_common_params、xy_platform_info拼接并加密生成。原始加密在`libshield.so`中，已用python复现。

```python
from xiaohongshu.shield import get_sign

# 待签名内容
content = '/api/sns/v4/note/user/posteduser_id=5eeb209d000000000101d84a&sub_tag_id=&cursor=5fa0c1730000000001008b0e&num=10&use_cursor=true&pin_note_id=&pin_note_ids=fid=1605335236101e0d28eb076dacfe290f2edc95ed7d21&device_fingerprint=202011141057245b5a8f26510e7fd80a6a846eb03732900192dede8e36bb58&device_fingerprint1=202011141057245b5a8f26510e7fd80a6a846eb03732900192dede8e36bb58&launch_id=1606097486&tz=Asia%2FShanghai&channel=YingYongBao&versionName=6.68.1&deviceId=10cf4b49-52d7-344d-887c-1ddcc9698557&platform=android&sid=session.1605335582221986643580&identifier_flag=2&t=1606097965&x_trace_page_current=user_page&lang=zh-Hans&uis=lightplatform=android&build=6681005&deviceId=10cf4b49-52d7-344d-887c-1ddcc9698557'

# content的拼接规则可参考get_sign内部代码
# get_sign也支持传入各个参数（path、params、data、xy_common_params、xy_platform_info）
# 注意，dict类型的参数传入之前需要进行url编码，可使用urllib.parse.urlencode

sign = get_sign(content=content)
print(sign)
```

#### 小红书滑块（数美）验证破解

小红书使用数美滑块验证码，验证过程（获取验证码配置>获取验证码>提交验证）在数美的服务器（数美使用`organization`来识别被验证的网站、App）上进行，完成后将通过的`rid`提交到小红书的接口。

具体实现细节：

- 协议更新：数美会定期自动更新js和接口参数字段（接口里所有两个字母组成的字段名都会在更新修改），通过`/ca/v1/conf`接口返回的js路径可以判断协议版本（如/pr/auto-build/v1.0.1-33/captcha-sdk.min.js，表示协议版本号为33），脚本会加载js，并通过匹配确认字段名，用于后续的接口请求。
- 验证参数：验证主要需要三个参数：位移比率、时间、轨迹，使用`opencv`中的`matchTemplate`函数计算距离，并随机生成相应的轨迹。
- 调用加密：提交验证的主要参数都需要加密，使用DES加密。
- 加密过程：`/ca/v1/register`接口会返回一个参数k，使用'sshummei'作为key对它解密，结果为加密参数所需的key，再对参数进行加密。

注：当前的验证参数全部按照小红书App调整，用于其他验证（如小红书Web或其他网站、App），可能需要调整其中参数。

```python
from xiaohongshu.shumei_slide_captcha import get_verify

# 表示小红书
organization = 'eR46sBuqF0fdw7KWFLYa'

# rid是验证过程中响应的标示，r是最后提交验证返回的响应
rid, r = get_verify(organization)

print(rid, r)

# riskLevel为PASS说明验证通过
if r['riskLevel'] == 'PASS':
    # 这里需要向小红书提交rid
    # 具体可抓包查看，接口：/api/sns/v1/system_service/slide_captcha_check
    pass
```

