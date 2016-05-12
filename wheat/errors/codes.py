# -*- coding:utf-8 -*-

########################################################
# 通用
########################################################

OK = 0
OK_MSG = "OK"

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

NOT_EXIST = 40008
NOT_EXIST_MSG = "不存在请求的资源"

LACK_REQUIRED_PARAM = 40009
LACK_REQUIRED_PARAM_MSG = 'Lacks required param when post or put'


########################################################
# 账户相关
########################################################

CAPTCHA_SEND_FAILED = 41000
CAPTCHA_SEND_FAILED_MSG = 'captcha send is faild'

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

PHONE_ALREAD_EXIST = 41007
PHONE_ALREAD_EXIST_MSG = 'this phone number has been registered already'

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

LACK_USER_ID_MSG = 'request信息未包含user_id字段'
LACK_USER_ID = 41020

INVALID_USER_ID_MSG = '该user_id与系统正在登录的user_id不符'
INVALID_USER_ID = 41021

INVALID_REG_INFO_MSG = 'This phone number or password is invalid'
INVALID_REG_INFO = 41022

PHONE_NUMBER_NOT_EXIST_MSG = 'This phone number not exist in system'
PHONE_NUMBER_NOT_EXIST = 41023

OPERATION_FORBIDDEN_MSG = 'this operation is invalid for this user(check if you had logined)'
OPERATION_FORBIDDEN = 41030
########################################################
# 群组相关
########################################################
UNKNOWN_GROUP = 42001
UNKNOWN_GROUP_MSG = "群不存在"

messages = {}
for name in dir():
    if not name.startswith('__') and name != 'messages' and not name.endswith('_MSG'):
        messages[globals()[name]] = globals()[name + '_MSG']


def errors(code):
    if code in messages:
        return {
            "message": messages.get(code, ""),
            "code": code,
        }
    else:
        raise TypeError('unsupport error code, must be define in codes.error')
