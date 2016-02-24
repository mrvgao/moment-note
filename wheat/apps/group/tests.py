# -*- coding:utf-8 -*-

'''
Test cases for group app.
Author: Minchiuan 2016-2-23
'''

from django.test import TestCase
from apps.group.services import GroupService
from apps.user.services import UserService
from customs.services import MessageService


class GroupServiceTestCase(TestCase):
	phone_number = '12345678910'
	user_id = None
	def setUp(self):
		user = UserService.create_user(phone=GroupServiceTestCase.phone_number)
		GroupServiceTestCase.user_id = user.id

	def test_get_all_group_message(self):
		owner_id = 'not exist'
		first_result = GroupService.get_group(creator=owner_id)
		self.assertIsNone(first_result)
		results = GroupService.get_all_friend_group(owner_id)
		self.assertIsNone(first_result)

		owner_id = GroupServiceTestCase.user_id
		first_result = GroupService.get_group(creator=owner_id)
		self.assertIsNone(first_result)
		results = GroupService.get_all_friend_group(owner_id)
		self.assertIsNotNone(results)


	def test_give_invitation_message(self):
		phone = '18857453090'
		message_param = '老爸,小明,www.mailicn.com'
		succeed, code = MessageService.send_message(phone=phone, template_id='20721', message_param=message_param)
		self.assertEqual(succeed, True)
