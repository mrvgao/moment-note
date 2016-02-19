### 和家

#### 发布和家

`visible`表示哪些人可见，可选参数：`private`,`public`,`friends`,`group_id`;

`private`只有自己可见，`public`所有的麦粒用户可见，`friends`所有好友可见，`group_id`只有在指定group内的用户可见

Method: `POST`
URL: {API_URL}/moments/
Auth: Login Required
Request:
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

#### 获取某人的和家页面的moments（不限制非得本人发的）

Method: `GET`
Url: {API_URL}/moments/?user_id={id}
Auth: Login required
Response:
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

* 获取某人自己发的和家moments

Method: `GET`
Url: {API_URL}/moments/?from_user={id}
Auth: Login Required
Response:
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
