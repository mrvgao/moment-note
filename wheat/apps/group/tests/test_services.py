'''
Test cases for group services.
'''

from django.test import TestCase
from apps.user.models import User
from apps.user.services import FriendshipService
from apps.user.services import UserService
from apps.group.services import GroupService
from apps.group.services import GroupMemberService
from apps.group.services import InvitationService
from apps.group.models import Group
from apps.group.models import GroupMember
from apps.group.models import Invitation
from information.utils import RedisPubsub


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
        self.assertTrue(group_service.valid_role_name(valid_role))
        
        valid_role = 'n-father'
        self.assertFalse(group_service.valid_role_name(valid_role))

        valid_role = 'r-father'
        self.assertTrue(group_service.valid_role_name(valid_role))

    def test_create_group_member(self):
        user = self.users[0]
        group = Group.objects.create(creator_id=user.id)

        gmember_service.create(group, user.id, 'admins', 'self')

        self.assertIsNotNone(GroupMember.objects.get(member_id=user.id))

    def test_create_group(self):
        user = self.users[0]
        creator_role = 'self'
        group = group_service.create(user.id, 'all_home_member', creator_role, 'all_home_member')

        self.assertTrue(str(user.id) in group.admins)
        self.assertTrue(str(user.id) in group.members)

        self.assertIsNotNone(group)

        self.assertIsNotNone(Group.objects.get(creator_id=user.id))
        self.assertIsNotNone(GroupMember.objects.get(member_id=user.id))

    def test_get_group(self):
        user = self.users[0]
        creator_role = 'self'
        group = group_service.create(user.id, 'all_home_member', creator_role, 'all_home_member')
        
        target_group = group_service.get(creator_id=user.id, group_type='all_home_member')
        self.assertEqual(target_group.id, group.id)
        self.assertIsNotNone(target_group)
    
    def test_create_default_home(self):
        user = self.users[0]
        group = group_service.create_default_home(user.id)
        self.assertIsNotNone(group)

        self.assertIsNotNone(Group.objects.get(id=group.id))

    def __member_is_empty(self, member):
        return bool(member) is False  # bool({}) is false but bool({..}) is not false

    def test_add_person_to_group(self):
        user = self.users[0]
        group = Group.objects.create(creator_id=user.id)

        self.assertTrue(self.__member_is_empty(group.members))
        group_service._add_group_person(group, 'members', user.id)
        self.assertFalse(self.__member_is_empty(group.members))

        self.assertTrue(self.__member_is_empty(group.admins))
        group_service._add_group_person(group, 'admins', user.id)
        self.assertFalse(self.__member_is_empty(group.admins))

    def test_add_admin(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)

        self.assertIsNone(group.admins.get(user2.id, None))
        group_service.add_group_admin(group, user2.id)
        group = group_service.get_home(user.id)
        self.assertIsNotNone(group.admins.get(str(user2.id), None))

    def test_add_member(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)

        self.assertIsNone(group.members.get(user2.id, None))
        group_service.add_group_member(group, user2.id)
        group = group_service.get_home(user.id)
        self.assertIsNotNone(group.members.get(str(user2.id), None))

    def test_consist_member(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)
        self.assertIsNone(group.members.get(user2.id, None))
        
        consist = group_service.consist_member(group.id, id=user2.id)
        self.assertFalse(consist)
        group_service.add_group_member(group, user2.id)
        consist = group_service.consist_member(group.id, id=user2.id)
        self.assertTrue(consist)

    def test_delete_member(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)
        group_service.add_group_member(group, user2.id)
        consist = group_service.consist_member(group.id, id=user2.id)
        self.assertTrue(consist)
        group_service.delete_member(group, user2.id)
        consist = group_service.consist_member(group.id, id=user2.id)
        self.assertFalse(consist)

    def test_get_user_home_member(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)
        group_service.add_group_member(group, user2.id)

        members = group_service.get_user_home_member(user.id)

        self.assertEqual(len(members), 2)

        self.assertTrue(str(user.id) in members)
        self.assertTrue(str(user2.id) in members)

    def test_user_group(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)
        group_service.add_group_member(group, user2.id)

        new_group = group_service.create_default_home(user2.id)

        groups = group_service.get_user_groups(user2.id)
        self.assertEqual(len(groups), 2)

        self.assertTrue(str(group.id), groups)
        self.assertTrue(str(new_group.id), groups)

    def test_delete_person_relation(self):
        user = self.users[0]
        user2 = self.users[1]
        group = group_service.create_default_home(user.id)
        group_service.add_group_member(group, user2.id)

        result = group_service.delete_person_relation(user.id, user2.id)
        self.assertIsNotNone(result)

        consist = group_service.consist_member(group.id, id=user2.id)
        self.assertFalse(consist)

        new_group = group_service.create_default_home(user2.id)
        group_service.add_group_member(group, user2.id)
        group_service.add_group_member(new_group, user.id)
        result = group_service.delete_person_relation(user.id, user2.id)
        consist = group_service.consist_member(group.id, id=user2.id)
        self.assertFalse(consist)
        consist = group_service.consist_member(new_group.id, id=user.id)
        self.assertFalse(consist)

    def test_role_acceptable(self):
        user = self.users[0]
        group = group_service.create_default_home(user.id)
        accptable = group_service.role_acceptable(group, 'self')
        self.assertFalse(accptable)

        accptable = group_service.role_acceptable(group, 'father')
        self.assertTrue(accptable)


inv_service = InvitationService()


class InvitationServiceTest(TestCase):
    def setUp(self):
        PRE = '1881234000'
        TOTAL = 10
        self.phone_numbers = [PRE + str(i) for i in range(TOTAL)]
        self.users = [User.objects.create(phone=p, password=p) for p in self.phone_numbers]
        self.users[-1].phone = '15705116597'  # myself phone for test.
        self.users[-1].save()
        self.homes = [group_service.create_default_home(self.users[i].id) for i in range(TOTAL)]

    def test_create(self):
        user = self.users[0]
        group = self.homes[0]
        inv_service.create(user.id, '18857453090', group.id, 'self', {})
        invitation = Invitation.objects.get(inviter=user.id, group_id=group.id)
        self.assertIsNotNone(invitation)

    def _test_send_invitation(self):
        inviter = self.users[0]
        invitee_phone = self.phone_numbers[-1]
        role = 'father'
        append_msg = 'hi'

        send = inv_service.invite_person(inviter, self.homes[0], invitee_phone, role, append_msg)
        self.assertTrue(send)
        # message send succceed.

        self.assertEqual(Invitation.objects.get(inviter=inviter.id).role, role)
        self.assertFalse(Invitation.objects.get(inviter=inviter.id).accepted)
        # invitation is created.

        # redis has received msg.
        redis_tool = RedisPubsub()
        r_msg = redis_tool.get()
        self.assertIsNotNone(r_msg)
        r_msg = redis_tool.get()
        self.assertTrue(role in str(r_msg['data']))

    def test_accept_one_user_register_one_not_registert(self):
        inviter = self.users[0]
        phone = '13362133816'

        invitation = inv_service.invite_person(inviter, self.homes[0], phone, 'father', 'where are you')

        # receiver message and registed.

        new_user = UserService().create(phone=phone, password=phone)
        new_user_id = new_user.id

        self.assertFalse(invitation.accepted)
        invitation = inv_service.accept(invitation.id)

        # inviter's home contains new_user
        inviter_home = group_service.get_home(inviter.id)
        consist = group_service.consist_member(inviter_home.id, id=new_user_id)
        self.assertTrue(consist)
                                   
        # new_user's home contains inviter
        new_user_home = group_service.get_home(new_user_id)
        consist = group_service.consist_member(new_user_home.id, id=inviter.id)
        self.assertTrue(consist)

        # new_user is friend.
        is_friend = FriendshipService().is_friend(inviter.id, new_user_id)
        self.assertTrue(is_friend)

        is_friend = FriendshipService().is_friend(new_user_id, inviter.id)
        self.assertTrue(is_friend)

    def test_accept_both_register(self):
        inviter = self.users[0]
        invitee_phone = self.users[-1].phone
        
        invitation = inv_service.invite_person(inviter, self.homes[0], invitee_phone, 'father', 'where are you')

        invitation = inv_service.accept(invitation.id)

        new_user_id = self.users[-1].id
        # inviter's home contains new_user
        inviter_home = group_service.get_home(inviter.id)
        consist = group_service.consist_member(inviter_home.id, id=new_user_id)
        self.assertTrue(consist)
                                   
        # new_user's home contains inviter
        new_user_home = group_service.get_home(new_user_id)
        consist = group_service.consist_member(new_user_home.id, id=inviter.id)
        self.assertTrue(consist)

        # new_user is friend.
        is_friend = FriendshipService().is_friend(inviter.id, new_user_id)
        self.assertTrue(is_friend)

        is_friend = FriendshipService().is_friend(new_user_id, inviter.id)
        self.assertTrue(is_friend)

    def test_reject(self):
        inviter = self.users[0]
        invitee_phone = self.users[-1].phone
        
        invitation = inv_service.invite_person(inviter, self.homes[0], invitee_phone, 'father', 'where are you')

        invitation = inv_service.reject(invitation.id)
        self.assertTrue(invitation.deleted)
