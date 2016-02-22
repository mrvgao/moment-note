'''
Tests case for user app.
Author: Minchiuan 2016-2-22
'''

from django.test import TestCase
from apps.user.services import MessageService

class MessageServiceTestCase(TestCase):
	def test_send_message(self):
		phone = '18857453090'
		return_status = MessageService.send_message(phone)
		self.assertIsNotNone(return_status)
		self.assertEqual(return_status[0], True)


	def test_match_captcha(self):
		phone = '18857453090'
		captcha = '259070'
		captcha_2 = '123452'

		match = MessageService.check_captcha(phone, captcha)
		self.assertTrue(match)

		match = MessageService.check_captcha(phone, captcha_2)
		self.assertFalse(match)

