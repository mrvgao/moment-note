### Setup Environment

* install mysql
* install redis
* install pip + virtualenv + virtualenvwrapper
* install packages in requirements/base.txt
* create mysql database `wheat` with Default Collation `utf8mb4-utf8mb4_general_ci`
* create folder `migrations` and file `migrations/__init__.py` under every app
* create tables with two steps: python manage.py makemigrations, python manage.py migrate
* create superuser: python manage.py createsuperuser, and set his auth_token key as '80a93e3c435775c0dec28f6a2ebafa49' and expired_at long enough
* login swagger document: /api/0.1/auth/login, and then open /api/0.1/docs/

### Example users

father
```
{
    "event": "login",
    "user_id": "a2b7c193f5df42a69942d0bc848c0467",
    "token": "80a93e3c435775c0dec28f6a2ebafa49"
}
```

mother
```
{
    "event": "login",
    "user_id": "0787ac6ad30b4bdeafc654a225eb96ba",
    "token": "798f085bb39f69ca11889dde77050a0d"
}
```

p-grandfather
```
{
    "event": "login",
    "user_id": "a76b6e59c2c7470e93fb06abe97f9633",
    "token": "bc47eeae0a5112469514821e8409ba43"
}
```

### 创建group

* request

```
{
  "group_type": "family",
  "name": "B&J的小家",
  "role": "father"
}
```

* response

```
{
  "data": {
    "id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "group_type": "family",
    "name": "B&J的小家",
    "avatar": "",
    "creator_id": "a2b7c193f5df42a69942d0bc848c0467",
    "admins": {
      "a2b7c193f5df42a69942d0bc848c0467": {
        "joined_at": "2016-02-16T17:00:42.430",
        "name": "whitefoxx"
      }
    },
    "members": {
      "a2b7c193f5df42a69942d0bc848c0467": {
        "role": "father",
        "joined_at": "2016-02-16T17:00:42.431",
        "name": "whitefoxx"
      }
    },
    "max_members": 15,
    "settings": {},
    "created_at": "2016-02-16T17:00:42.433591",
    "updated_at": "2016-02-16T17:00:42.433622"
  },
  "request": "success"
}
```


### 邀请

* 邀请某人以某种身份到某个group中

```
{
  "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
  "invitee": "0787ac6ad30b4bdeafc654a225eb96ba",
  "role": "mother",
  "message": "welcome mother"
}
```

```
{
  "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
  "invitee": "a76b6e59c2c7470e93fb06abe97f9633",
  "role": "p-grandfather",
  "message": "welcome p-grandfather"
}
```

response

```
{
  "data": {
    "id": "bb77386007cf47749f5b59c0b1924d05",
    "inviter": "a2b7c193f5df42a69942d0bc848c0467",
    "invitee": "0787ac6ad30b4bdeafc654a225eb96ba",
    "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "role": "mother",
    "message": "{'group_avatar': '', 'role': u'mother', 'inviter_avatar': '', 'inviter_nickname': u'whitefoxx', 'group_id': UUID('34f3ba7121d348b29f17fa0dd1678a3a'), 'inviter': UUID('a2b7c193f5df42a69942d0bc848c0467'), 'message': u'welcome mother', 'invitee': u'0787ac6ad30b4bdeafc654a225eb96ba', 'group_name': u'B&J\\u7684\\u5c0f\\u5bb6'}",
    "invite_time": "2016-02-16T17:11:48.041705",
    "accepted": false,
    "accept_time": null,
    "deleted": false,
    "notified": false
  },
  "request": "success"
}
```

如果invitee在线会接收到一条推送

```
{
  "receiver_id": "0787ac6ad30b4bdeafc654a225eb96ba",
  "invitation_id": "bb77386007cf47749f5b59c0b1924d05",
  "message": {
    "group_avatar": "",
    "role": "mother",
    "inviter_avatar": "",
    "inviter_nickname": "whitefoxx",
    "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "inviter": "a2b7c193f5df42a69942d0bc848c0467",
    "message": "welcome mother",
    "invitee": "0787ac6ad30b4bdeafc654a225eb96ba",
    "group_name": "B&J的小家"
  },
  "event": "invitation",
  "sub_event": "sd_inv"
}
```

* invitee接收邀请

```
{
    "accepted": true/false
}
```

inviter会接收到如下的notification

```
{
  "receiver_id": "a2b7c193f5df42a69942d0bc848c0467",
  "invitation_id": "bb77386007cf47749f5b59c0b1924d05",
  "event": "invitation",
  "sub_event": "acc_inv_ntf"
}
```


### 聊天

* private chat message

father -> mother
```
{
    "event": "chat",
    "sub_event": "p2p",
    "sender_id": "a2b7c193f5df42a69942d0bc848c0467",
    "receiver_id": "0787ac6ad30b4bdeafc654a225eb96ba",
    "content_type": "text",
    "content": {
        "text": "hello mother"
    }
}
```

mother -> father
```
{
    "event": "chat",
    "sub_event": "p2p",
    "sender_id": "0787ac6ad30b4bdeafc654a225eb96ba",
    "receiver_id": "a2b7c193f5df42a69942d0bc848c0467",
    "content_type": "text",
    "content": {
        "text": "hello father"
    }
}
```

* group chat message

group_id 34f3ba7121d348b29f17fa0dd1678a3a

father -> group

```
{
    "event": "chat",
    "sub_event": "p2g",
    "sender_id": "a2b7c193f5df42a69942d0bc848c0467",
    "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "content_type": "text",
    "content": {
        "text": "group message from father"
    }
}
```

mother -> group
```
{
    "event": "chat",
    "sub_event": "p2g",
    "sender_id": "0787ac6ad30b4bdeafc654a225eb96ba",
    "group_id": "34f3ba7121d348b29f17fa0dd1678a3a",
    "content_type": "text",
    "content": {
        "text": "group message from mother"
    }
}
```


### 和家

* 发布和家

```
{
    "user_id": "a2b7c193f5df42a69942d0bc848c0467",
    "content_type": "text",
    "content": {
        "text": "first family moment"
    },
    "visible": "34f3ba7121d348b29f17fa0dd1678a3a"
}
```

response

```
{
  "data": {
    "id": "2d012b80350b4360a1e949cc7b82faa5",
    "user_id": "a2b7c193f5df42a69942d0bc848c0467",
    "content_type": "text",
    "content": {
      "text": "first family moment"
    },
    "post_date": "2016-02-16T17:26:21.094516",
    "moment_date": "2016-02-16T17:26:21.094554",
    "visible": "34f3ba7121d348b29f17fa0dd1678a3a",
    "deleted": false
  },
  "request": "success"
}
```

* 获取某人的和家页面的moments（不限制非得本人发的）

url: /api/0.1/moments/?user_id=0787ac6ad30b4bdeafc654a225eb96ba

```
{
  "data": [
    {
      "id": "2d012b80350b4360a1e949cc7b82faa5",
      "user_id": "a2b7c193f5df42a69942d0bc848c0467",
      "content_type": "text",
      "content": {
        "text": "first family moment"
      },
      "post_date": "2016-02-16T17:26:21",
      "moment_date": "2016-02-16T17:26:21",
      "visible": "34f3ba7121d348b29f17fa0dd1678a3a",
      "deleted": false
    },
    {
      "id": "d479d44c1e1943afb1fa6dac67207c1f",
      "user_id": "a2b7c193f5df42a69942d0bc848c0467",
      "content_type": "text",
      "content": {
        "text": "all my friends can see this moment"
      },
      "post_date": "2016-02-16T17:27:53",
      "moment_date": "2016-02-16T17:27:53",
      "visible": "friends",
      "deleted": false
    }
  ],
  "request": "success"
}
```

* 获取某人发的和家moments

url: /api/0.1/moments/?from_user=a2b7c193f5df42a69942d0bc848c0467

```
{
  "data": [
    {
      "id": "71b25dc984e04995bf7a336bc002b0b7",
      "user_id": "a2b7c193f5df42a69942d0bc848c0467",
      "content_type": "text",
      "content": {
        "text": "hello"
      },
      "post_date": "2016-02-16T15:35:53",
      "moment_date": "2016-02-16T15:35:53",
      "visible": "private",
      "deleted": false
    },
    {
      "id": "2d012b80350b4360a1e949cc7b82faa5",
      "user_id": "a2b7c193f5df42a69942d0bc848c0467",
      "content_type": "text",
      "content": {
        "text": "first family moment"
      },
      "post_date": "2016-02-16T17:26:21",
      "moment_date": "2016-02-16T17:26:21",
      "visible": "34f3ba7121d348b29f17fa0dd1678a3a",
      "deleted": false
    },
    {
      "id": "d479d44c1e1943afb1fa6dac67207c1f",
      "user_id": "a2b7c193f5df42a69942d0bc848c0467",
      "content_type": "text",
      "content": {
        "text": "all my friends can see this moment"
      },
      "post_date": "2016-02-16T17:27:53",
      "moment_date": "2016-02-16T17:27:53",
      "visible": "friends",
      "deleted": false
    }
  ],
  "request": "success"
}
```
