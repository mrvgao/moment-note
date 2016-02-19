### 账户系统

#### 注册

* 检查手机号是否已注册

Method: `GET`
URL: {{API_URL}}/users/?phone=18582227569
Response:
```
{
    "data": {
        "phone": "18582227569",
        "registered": false
    },
    "request": "success"
}
```

* 发送验证码

Method: `POST`
URL: {{API_URL}}/users/captcha/?action=send
Request:
```
{
    "phone": "18582227569"
}
```

Respone:
```
{
    "data": {
        "phone": "18582227569",
        "captcha": "123456"
    },
    "request": "success"
}
```

* 检查验证码与手机号是否匹配

Method: `POST`
URL: {{API_URL}}/users/captcha/?action=check
Request:
```
{
    "phone": "18582227569",
    "captcha": "123456"
}
```

Respone:
```
{
    "data": {
        "phone": "18582227569",
        "captcha": "123456",
        "matched": true
    },
    "request": "success"
}
```

* 创建用户

Method: `POST`
URL: {{API_URL}}/users/
Request:
```
{
    "phone": "18582227569",
    "password": "123456",
    "nickname": "麦宝宝"
}
```

Response:
```
{
    "data": {
      "id": "0787ac6ad30b4bdeafc654a225eb96ba",
      "phone": "18582227560",
      "nickname": "麦宝宝",
      "token": {
        "token": "798f085bb39f69ca11889dde77050a0d",
        "expired_at": 1460282633
      },
      "first_name": "",
      "last_name": "",
      "full_name": "",
      "avatar": "",
      "tagline": "",
      "marital_status": false,
      "gender": "N",
      "birthday": null,
      "city": "",
      "province": "",
      "country": "",
      "role": "normal",
      "is_admin": false,
      "activated": true,
      "activated_at": "2016-02-01T12:14:37",
      "created_at": "2016-02-01T12:14:37",
      "updated_at": "2016-02-01T12:14:37",
      "last_login": "2016-02-03T17:48:14"
    },
    "request": "success"
}
```

#### 登录

* 手机号登录

Method: `POST`
URL: {{API_URL}}/users/login/
Request:
```
{
    "phone": "18582227569",
    "password": "123456"
}
```

Response:
```
{
    "data": {
      "id": "0787ac6ad30b4bdeafc654a225eb96ba",
      "phone": "18582227560",
      "nickname": "麦宝宝",
      "token": {
        "token": "798f085bb39f69ca11889dde77050a0d",
        "expired_at": 1460282633
      },
      "first_name": "",
      "last_name": "",
      "full_name": "",
      "avatar": "",
      "tagline": "",
      "marital_status": false,
      "gender": "N",
      "birthday": null,
      "city": "",
      "province": "",
      "country": "",
      "role": "normal",
      "is_admin": false,
      "activated": true,
      "activated_at": "2016-02-01T12:14:37",
      "created_at": "2016-02-01T12:14:37",
      "updated_at": "2016-02-01T12:14:37",
      "last_login": "2016-02-19T11:08:52"
    },
    "request": "success"
}
```

#### 忘记密码

忘记密码的操作步骤跟注册非常类似，都需要`检查手机号是否已注册`以及`检查验证码与手机号是否匹配`这两个APIs，只是多一个`修改密码`的API：

* 修改密码

Method: `PUT`
URL: {{API_URL}}/users/
Request:
```
{
    "phone": "18582227569",
    "password": "12345678"
}
```

Response:
```
{
    "data": {
      "id": "0787ac6ad30b4bdeafc654a225eb96ba",
      "phone": "18582227560",
      "nickname": "麦宝宝",
      "token": {
        "token": "798f085bb39f69ca11889dde77050a0d",
        "expired_at": 1460282633
      },
      "first_name": "",
      "last_name": "",
      "full_name": "",
      "avatar": "",
      "tagline": "",
      "marital_status": false,
      "gender": "N",
      "birthday": null,
      "city": "",
      "province": "",
      "country": "",
      "role": "normal",
      "is_admin": false,
      "activated": true,
      "activated_at": "2016-02-01T12:14:37",
      "created_at": "2016-02-01T12:14:37",
      "updated_at": "2016-02-01T12:14:37",
      "last_login": "2016-02-19T11:08:52"
    },
    "request": "success"
}
```
