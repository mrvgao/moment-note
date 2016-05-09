'''
Test cases for group services.
'''

from django.test import TestCase
from apps.user.models import User
from apps.group.services import GroupService
from apps.group.services import GroupMemberService
from apps.group.models import Group
from apps.group.models import GroupMember


group_service = GroupService()
gmember_service = GroupMemberService()


class GroupServiceTest(TestCase):
    def setUp(self):
        PRE = '1881234000'
        TOTAL = 10
        self.phone_numbers = [PRE + str(i) for i in range(TOTAL)]
        self.users = [User.objects.create(phone=p, password=p) for p in self.phone_numbers]

    def test_group_type_valid(self):
        valid_type = 'all_home_member'
        self.assertTrue(group_service.group_type_valid(valid_type))
        invalid_type = 'in-all_home_member'
        self.assertFalse(group_service.group_type_valid(invalid_type))

    def test_creator_valid_role(self):
        valid_role = 'father'
        self.assertTrue(group_service.valid_role(valid_role))
        
        valid_role = 'n-father'
        self.assertFalse(group_service.valid_role(valid_role))

    def test_create_group_member(self):
        user = self.users[0]
        group_id = user.id

        gmember_service.create(user.id, group_id, 'test', 'remark', user.avatar, 'nickname', 'role')

        self.assertIsNotNone(GroupMember.objects.get(member_id=user.id))

    def test_create_group(self):
        user = self.users[0]
        creator_role = 'self'
        group = group_service.create(user.id, 'all_home_member', creator_role, 'all_home_member')

        self.assertIsNotNone(group)

        self.assertIsNotNone(Group.objects.get(creator_id=user.id))
        self.assertIsNotNone(GroupMember.objects.get(member_id=user.id))

    def test_get_group(self):
        user = self.users[0]
        creator_role = 'self'
        group = group_service.create(user.id, 'all_home_member', creator_role, 'all_home_member')
        
        target_group = group_service.get(user.id, 'all_home_member')
        self.assertEqual(target_group.id, group.id)
        self.assertIsNotNone(target_group)
    
    def test_create_default_home(self):
        user = self.users[0]
        group = group_service.create_default_home(user.id)
        self.assertIsNotNone(group)

        self.assertIsNotNone(Group.objects.get(id=group.id))

