'''
Test for invitation apis.
@Author Minchiuan Gao <2016-4-13>
'''

from customs import test_tools

from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from apps.user.services import UserService
from apps.group.services import GroupService


class TestInvitationAPI(APITestCase):
    def setUp(self):
        PRE = '1881234000'
        TOTAL = 10
        self.phone_numbers = [PRE + str(i) for i in range(TOTAL)]
        self.password = '123456'

        user_service = UserService()
        self.users = [user_service.create(phone=p, password=self.password) for p in self.phone_numbers]

        self.client = APIClient()
        self.client.credentials(enforce_csrf_checks=False)

        self.current_user = self.users[0]

        test_tools.refresh_token(self.client, self.current_user.phone, self.password)

    def test_invite_self_faild(self):
        father = 'father'

        user = self.users[0]
        group_id = GroupService().create_default_home(user.id).id

        post_data = {
            'group_id': group_id,
            'invitee': user.phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'

        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 409)

    def test_invite_group_not_exist(self):
        father = 'father'
        user = self.users[0]

        post_data = {
            'group_id': 'no-group',
            'invitee': user.phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'

        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 403)

    def test_invite_not_self_group(self):
        father = 'father'
        user = self.users[0]
        group_id = GroupService().create_default_home(self.users[-1].id).id

        post_data = {
            'group_id': group_id,
            'invitee': user.phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 403)

    def test_invite_already_consist_failed(self):
        father = 'father'
        user = self.users[0]
        group = GroupService().create_default_home(user.id)

        already_friend = self.users[1]
        GroupService().add_group_member(group, already_friend.id)

        post_data = {
            'group_id': group.id,
            'invitee': already_friend.phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 409)

    def test_invited_invlid_role(self):
        father = 'wrong-father'
        user = self.users[0]
        group = GroupService().create_default_home(user.id)

        post_data = {
            'group_id': group.id,
            'invitee': self.users[1].phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 406)

        pass

    def test_invite_success(self):
        father = 'father'
        user = self.users[0]
        group = GroupService().create_default_home(user.id)

        post_data = {
            'group_id': group.id,
            'invitee': self.users[1].phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 200)

    def test_accpet(self):
        father = 'father'
        user = self.users[0]
        group = GroupService().create_default_home(user.id)

        post_data = {
            'group_id': group.id,
            'invitee': self.users[1].phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'
        response = self.client.post(url, post_data)

        invitation_id = response.data['data']['id']

        self.assertIsNotNone(invitation_id)

        url = test_tools.URL_PREFIX + 'invitations/{0}/'.format(invitation_id)

        accept = {
            'accepted': True
        }

        response = self.client.put(url, accept)
        self.assertEqual(response.status_code, 200)

    def test_reject(self):
        father = 'father'
        user = self.users[0]
        group = GroupService().create_default_home(user.id)

        post_data = {
            'group_id': group.id,
            'invitee': self.users[1].phone,
            'role': father,
            'message': 'hi'
        }

        url = test_tools.URL_PREFIX + 'invitations/'
        response = self.client.post(url, post_data)

        invitation_id = response.data['data']['id']

        self.assertIsNotNone(invitation_id)

        invitation_id = response.data['data']['id']
        url = test_tools.URL_PREFIX + 'invitations/{0}/'.format(invitation_id)

        accept = {
            'accepted': False
        }

        response = self.client.put(url, accept)
        self.assertEqual(response.status_code, 200)
