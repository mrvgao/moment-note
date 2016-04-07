'''
Tests case for user app.
Author: Minchiuan 2016-2-22
'''

from django.test import TestCase
from customs.services import MessageService
from .services import UserService

class MessageServiceTestCase(TestCase):

	'''
	def test_send_message(self):
		phone = '18857453090'
		return_status = MessageService.send_message(phone)
		self.assertIsNotNone(return_status)
		self.assertEqual(return_status[0], True)
	'''

	def test_match_captcha(self):
		phone = '18857453090'
		captcha = '259070'
		captcha_2 = '123452'

		match = MessageService.check_captcha(phone, captcha)
		self.assertTrue(match)

		match = MessageService.check_captcha(phone, captcha_2)
		self.assertFalse(match)


class UserServiceTestCase(TestCase):
	def test_check_is_friend(self):
		user1_list = ['91c45a0a44df426f82023b476381f9a4', '91c45a0a44df426f82023b476381f9a4', None]
		user2_list = ['b35024e4280b4a7ba9baf9c1a80a1c05', None, 'b35024e4280b4a7ba9baf9c1a80a1c05']

		for user1, user2 in zip(user1_list, user2_list):
			friend = UserService.is_friend(user1, user2)
			self.assertTrue(friend)

		user1 = 'b35024e4280b4a7ba9baf9c1a80a1c05'
		user2 = 'b35024e4280b4a7ba9baf9c1a80a1c'

		friend = MessageService.is_friend(user1, user2)
		self.assertFalse(user1, user2)