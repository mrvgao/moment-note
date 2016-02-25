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
Url: {API_URL}/moments/?receiver={id}&sender={id}&number={int}&begin-id={id}&compare={previous/after}
Auth: Login required

获取和家信息

##### Query 参数说明

receiver -- 接收者的id, 为保证信息的安全，接收者的id必须与当前session的user_id一致，否则请求错误
        
sender -- 发送者的id， 可以为空，为空则返回所有好友的和家信息
        
number -- 获得的信息数量， 可以为空，为空则至多返回10条

begin-id -- 起始信息的id，可以为空，为空则返回系统中该用户可见的最新的信息（该信息有可能意见阅读或尚未阅读过）
        
compare -- 在begin－id之前发送的（previous）还是之后发送的（after），可以为空，

##### Example Request:
       
        e.g 01.
        /moment/?receiver=b231asd&begin=ajkdajkwld123&step=15&compare=previous

        表示，获取与begin最接近的15条数据，会获得包括自己在内的所有好友发送的和家信息

        e.g 02.
        /moment?receiver=b123dwad&sender=dakwdjlka21231&compare=previous

        表示，获取sender发送的且receiver能够看到的和家信息

        e.g 03
        /moment?receiver=alskjdajkls12&compare=previous

        表示，获取receiver能接受到的最近的10条信息

        e.g 04

        /moment?receiver=b123asd128hjkasdhjk&begin=ajkhsd1234hkjasdhjk&step＝15compare=after
        表示，获取比begin更新的15条数据
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
