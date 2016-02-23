# -*- coding: utf-8 -*-
'''
TEST Configurations

- Runs in Debug mode
- Uses console backend for emails
- Use Django Debug Toolbar
'''
from .local import Local


class Test(Local):
    pass
