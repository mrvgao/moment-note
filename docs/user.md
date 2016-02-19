### 账户系统

#### 注册

* 检查手机号是否已注册

Method: `GET`
URL: {API_URL}/users/?phone=18582227569
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
URL: {API_URL}/users/captcha/?action=send
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
URL: {API_URL}/users/captcha/?action=check
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
URL: {API_URL}/users/
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
URL: {API_URL}/users/login/
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
URL: {API_URL}/users/
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


#### 邀请家庭成员

* 发送邀请

与本人的关系：爷爷/奶奶/外公/外婆/爸爸/妈妈/公公(岳父)/婆婆(岳母)/儿子/女儿/老公/老婆/女婿/媳妇/亲家公/亲家母/孙子/孙女/外孙/外孙女/亲兄弟/亲姐妹
分别对应：f-grandfather/f-grandmother/m-grandfather/m-grandmother/father/mother/father-in-law/mother-in-law/son/daughter/husband/wife/son-in-law/daughter-in-law/co-father-in-law/co-mother-in-law/s-grandson/s-granddaughter/d-grandson/d-granddaughter/brother/sister

Method: `POST`
URL: {API_URL}/users/invitations/
Auth: Loign required
Request:
```
{
    "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "invitee": "0787ac6ad30b4bdeafc654a225eb96ba",
    "relation": "mother",
    "message": "欢迎来到麦粒家庭"
}
```

Response:
```
{
  "data": {
    "id": "bb77386007cf47749f5b59c0b1924d05",
    "inviter": "a2b7c193f5df42a69942d0bc848c0467",
    "invitee": "0787ac6ad30b4bdeafc654a225eb96ba",
    "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "relation": "mother",
    "message": {
      "group_avatar": "",
      "relation": "mother",
      "inviter_avatar": "",
      "inviter_nickname": "whitefoxx",
      "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
      "inviter": "a2b7c193f5df42a69942d0bc848c0467",
      "message": "欢迎来到麦粒家庭",
      "invitee": "0787ac6ad30b4bdeafc654a225eb96ba",
      "group_name": ""
    },
    "invite_time": "2016-02-16T17:11:48.041705",
    "accepted": false,
    "accept_time": null,
    "deleted": false,
    "notified": false
  },
  "request": "success"
}
```

* 接受邀请

Method: `PUT`
URL: {API_URL}/users/invitations/{id}/
Auth: Login required
Request:
```
{
    "accepted": true
}
```

Response:
```
{
    "request": "success"
}
```
