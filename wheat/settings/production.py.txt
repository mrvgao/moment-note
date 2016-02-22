# -*- coding: utf-8 -*-
'''
Production Configurations

- Runs in Debug mode
- Uses console backend for emails
- Use Django Debug Toolbar
'''
from configurations import values
from .common import Common


class Production(Common):

    SECRET_KEY = "r2=_vzt7(8dcl+yyo*4dmef&jp&iwxb=6*4f59r)Production"

    # DEBUG
    DEBUG = values.BooleanValue(False)
    TEMPLATE_DEBUG = DEBUG
    # END DEBUG
