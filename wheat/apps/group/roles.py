# -*- coding:utf-8 -*-

# chinese: chinese title
# multiple: can we have multiple `father`? no, but we can have multiple `son`
# ctm: chinese_title_male, reverse role for male
# ctf: chinese_title_female, reverse role from female

# f-: from father's viewing angle
# m-: from mother's viewing angle
# s-: from son's viewing angle
# d-: from daughter's viewing angle
# h-: from husband's viewing angle
# w-: from wife's viewing angle

role_map = {
    'f-grandfather': {
        'chinese': u'爷爷',
        'multiple': False,
        'ctm': 's-grandson',
        'cmf': 's-granddaughter'
    },
    'f-grandmother': {
        'chinese': u'奶奶',
        'multiple': False,
        'ctm': 's-grandson',
        'ctf': 's-granddaughter'
    },
    'm-grandfather': {
        'chinese': u'外公',
        'multiple': False,
        'ctm': 'd-grandson',
        'ctf': 'd-granddaughter'
    },
    'm-grandmother': {
        'chinese': u'外婆',
        'multiple': False,
        'ctm': 'd-grandson',
        'ctf': 'd-granddaughter'
    },
    'co-father-in-law': {
        'chinese': u'亲家公',
        'multiple': True,
        'ctm': 'co-father-in-law',
        'ctf': 'co-mother-in-law'
    },
    'co-mother-in-law': {
        'chinese': u'亲家母',
        'multiple': True,
        'ctm': 'co-father-in-law',
        'ctf': 'co-mother-in-law',
    },
    'father': {
        'chinese': u'爸爸',
        'multiple': False,
        'ctm': 'son',
        'ctf': 'daughter'
    },
    'mother': {
        'chinese': u'妈妈',
        'multiple': False,
        'ctm': 'son',
        'ctf': 'daughter'
    },
    'h-father-in-law': {
        'chinese': u'岳父',
        'multiple': False,
        'ctm': 'son-in-law'
    },
    'h-mother-in-law': {
        'chinese': u'岳母',
        'multiple': False,
        'ctm': 'son-in-law'
    },
    'w-father-in-law': {
        'chinese': u'公公',
        'multiple': False,
        'ctf': 'daughter-in-law'
    },
    'w-mother-in-law': {
        'chinese': u'婆婆',
        'multiple': False,
        'ctf': 'daughter-in-law'
    },
    'husband': {
        'chinese': u'老公',
        'multiple': False,
        'ctf': 'wife'
    },
    'wife': {
        'chinese': u'老婆',
        'multiple': False,
        'ctm': 'husband'
    },
    'son': {
        'chinese': u'儿子',
        'multiple': True,
        'ctm': 'father',
        'ctf': 'mother'
    },
    'daughter': {
        'chinese': u'女儿',
        'multiple': True,
        'ctm': 'father',
        'ctf': 'mother'
    },
    'son-in-law': {
        'chinese': u'女婿',
        'multiple': True,
        'ctm': 'h-father-in-law',
        'ctf': 'h-mother-in-law'
    },
    'daughter-in-law': {
        'chinese': u'媳妇',
        'multiple': True,
        'ctm': 'w-father-in-law',
        'ctf': 'w-mother-in-law'
    },
    's-grandson': {
        'chinese': u'孙子',
        'multiple': True,
        'ctm': 'f-grandfather',
        'ctf': 'f-grandmother'
    },
    's-granddaugher': {
        'chinese': u'孙女',
        'multiple': True,
        'ctm': 'f-grandfather',
        'ctf': 'f-grandmother'
    },
    'd-grandson': {
        'chinese': u'外孙',
        'multiple': True,
        'ctm': 'm-grandfather',
        'ctf': 'm-grandmother'
    },
    'd-granddaugher': {
        'chinese': u'外孙女',
        'multiple': True,
        'ctm': 'm-grandfather',
        'ctf': 'm-grandmother'
    },
    'older-brother': {
        'chinese': u'哥哥',
        'multiple': True,
        'ctm': 'younger-brother',
        'ctf': 'younger-sister'
    },
    'younger-brother': {
        'chinese': u'弟弟',
        'multiple': True,
        'ctm': 'older-brother',
        'ctf': 'older-sister'
    },
    'older-sister': {
        'chinese': u'姐姐',
        'multiple': True,
        'ctm': 'younger-brother',
        'ctf': 'younger-sister'
    },
    'younger-sister': {
        'chinese': u'妹妹',
        'multiple': True,
        'ctm': 'older-brother',
        'ctf': 'older-sister'
    },
    'self': {
        'chinese': u'自己',
        'multiple': False
    }
}
