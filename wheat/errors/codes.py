# -*- coding:utf-8 -*-

########################################################
# 通用
########################################################

DEFAULT_ERROR_MSG = 'A server error occurred.'

OPERATION_NOT_ALLOWED = 40000
OPERATION_NOT_ALLOWED_MSG = "Method not allowed"

BAD_REQUEST = 40001
BAD_REQUEST_MSG = "BAD_REQUEST"

HAS_NO_PERMISSION = 40002
HAS_NO_PERMISSION_MSG = "无权限"

UNAUTHORIZED = 40003
UNAUTHORIZED_MSG = "未授权错误"

LOGIN_REQUIRED = 40004
LOGIN_REQUIRED_MSG = "未登录错误"

ADMIN_REQUIRED = 40005
ADMIN_REQUIRED_MSG = "要求管理员权限"

EXPIRED_TOKEN = 40006
EXPIRED_TOKEN_MSG = "过期的token"

UNKNOWN_ACTION = 40007
UNKNOWN_ACTION_MSG = "未知操作"


########################################################
# 账户相关
########################################################

INACTIVE_ACCOUNT = 41001
INACTIVE_ACCOUNT_MSG = "账号未激活"

INCORRECT_CREDENTIAL = 41002
INCORRECT_CREDENTIAL_MSG = "用户名或密码错误"

USER_NOT_EXIST = 41003
USER_NOT_EXIST_MSG = "用户不存在或已删除"

INVALID_TOKEN = 41004
INVALID_TOKEN_MSG = "无效TOKEN"

EMAIL_ALREADY_EXIST = 41005
EMAIL_ALREADY_EXIST_MSG = "邮箱已经被注册"

USERNAME_ALREADY_EXIST = 41006
USERNAME_ALREADY_EXIST_MSG = "用户名已经被注册"

INVALID_CODE = 41007
INVALID_CODE_MSG = "无效的激活码"

CODE_ALREADY_USED = 41008
CODE_ALREADY_USED_MSG = "激活码已失效"

CODE_NOT_FOUND = 41009
CODE_NOT_FOUND_MSG = "激活码不存在"

USERNAME_NOT_EXIST = 41010
USERNAME_NOT_EXIST_MSG = "用户名不存在"

INVALID_PASSWORD = 41011
INVALID_PASSWORD_MSG = "无效密码"

INVALID_FOLLOWEE = 41012
INVALID_FOLLOWEE_MSG = "不能关注该用户"

INVALID_UNFOLLOWEE = 41013
INVALID_UNFOLLOWEE_MSG = "未关注该用户"

INVALID_EMAIL = 41014
INVALID_EMAIL_MSG = "无效的EMAIL或EMAIL已经注册"

INVALID_AVATAR = 41015
INVALID_AVATAR_MSG = "无效的头像"

UNKNOWN_MESSAGE = 41016
UNKNOWN_MESSAGE_MSG = "邮件不存在"

QQ_LOGIN_FAIL = 41017
QQ_LOGIN_FAIL_MSG = "qq验证码登录失败"

INVALID_INVITATION = 41018
INVALID_INVITATION_MSG = "无效的邀请"

INVITATION_ALREADY_USED = 41019
INVITATION_ALREADY_USED_MSG = "邀请已失效"


messages = {}
for name in dir():
    if not name.startswith('__') and name != 'messages' and not name.endswith('_MSG'):
        messages[globals()[name]] = globals()[name + '_MSG']


def errors(code):
    return {
        "message": messages.get(code, ""),
        "code": code,
    }
