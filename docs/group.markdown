### 获得群的ID

**获得某个用户的群的id

为了方便诸如家庭状态等信息的统一管理，我们把全部好友视为一个“大群”。 邀请一个好友，就类似于把一个人加入自己的一个群中。 所以当某个用户A邀请某人的时候，需要首先获得该用户A的全部“群”， 然后找到叫做“friend”的这个群的id，然后利用“发送邀请的id”， 把新好友加入进来。

Method: `POST`
URL: {API_URL}/groups/{owner_id}&type=all_friends
```
/* 
owner_id 为该群所有者的id
type == all_friends时候，获取该用户全部好友所属的群号，若无type，则返回所有群组
Auth: Login required
*/
```

#### Example Request:

/groups/b35024e4280b4a7ba9baf9c1a80a1c05&type=all_friends 获得关于b35*用户的，
包含所有朋友的“大群”。

Response:

{
    'owner_id': 'b35024e4280b4a7ba9baf9c1a80a1c05',
    'type': 'all_friends',
    'group_id': '4a7ba9baf9c1a80a1c05b35024e4280b'
}
