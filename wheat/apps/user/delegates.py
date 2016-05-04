'''
Delegates services for api call.
'''

from services import UserService

@change_value
class Delegate(object):
    def __init__(self, source):
        self.source = source

    

