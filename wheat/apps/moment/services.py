# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.db.models import Q

from customs.services import BaseService
from apps.user.services import UserService
from .models import Moment
from .serializers import MomentSerializer
from django.db.models import Min
from apps.book.services import AuthorService
from itertools import chain
from utils.redis_utils import publish_redis_message
from .models import Comment
from .models import Mark
import abc
import functools
from information import redis_tools


class MomentService(BaseService):

    @classmethod
    def _get_model(cls, name='Moment'):
        if name == 'Moment':
            return Moment

    @classmethod
    def get_serializer(cls, model='Moment'):
        if model == 'Moment':
            return MomentSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, Moment):
            return MomentSerializer(obj, context=context).data

    @classmethod
    def get_moment(cls, **kwargs):
        return Moment.objects.get_or_none(**kwargs)

    @classmethod
    def get_moments(cls, **kwargs):
        return Moment.objects.filter(**kwargs)

    @staticmethod
    def _fix_content(content):
        PICS, TEXT = 'pics', 'text'
        fix_list = [PICS, TEXT]
        for f in fix_list:
            if f not in content:
                content.setdefault(f, [])
        return content

    @classmethod
    @transaction.atomic
    def create_moment(cls, **kwargs):
        user_id = kwargs.get('user_id')
        content_type = kwargs.get('content_type')
        content = kwargs.get('content')
        moment_date = kwargs.get('moment_date', datetime.now())
        visible = kwargs.get('visible')
        tags = kwargs.get('tags')

        if user_id and Moment.valid_content_type(content_type, content) \
                and Moment.valid_visible_field(visible):

            content = MomentService._fix_content(content)
            moment = Moment.objects.create(
                user_id=user_id,
                content_type=content_type,
                content=content,
                moment_date=moment_date,
                visible=visible,
                tags=tags)

            _notify_moment_to_firends(visible, user_id, moment.id)
            return moment

        return None

    @classmethod
    @transaction.atomic
    def delete_moment(cls, moment):
        if not moment.deleted:
            moment.deleted = True
            moment.save()
        return True

    @classmethod
    def get_user_moments(cls, user_id):
        from apps.group.services import GroupService
        # friend_ids = UserService.get_user_friend_ids(user_id)
        group_ids = GroupService.get_user_group_ids(user_id)
        home_members = GroupService.get_home_member(user_id)

        condition = Q(Q(user_id__in=home_members) & Q(visible__in=['public', 'friends']))
      #  condition = Q(user_id__in=home_members)
        moment = Moment.objects.filter(condition).filter(deleted=False).order_by('post_date')

        return moment

    @classmethod
    def filter_public_moments(cls, moments):
        return moments.filter(Q(visible__in=['public', 'friends']))

    @classmethod
    def get_moments_from_user(cls, user_id):
        moments = Moment.objects.filter(
            user_id=user_id,
            deleted=False).order_by('post_date').filter(deleted=False)
        return moments

    @staticmethod
    def get_recent_moment(user_id):
        try:
            moment = MomentService.get_moment(user_id=user_id)
            return moment.id, moment.post_date
        except Exception as e:
            print e
            return None, None


def _notify_moment_to_firends(visible, user_id, moment_id):
    from apps.group.services import get_friend_from_group_id
    from apps.group.services import get_all_home_member_list

    PUBLIC, FRIENDS = 'public', 'friends'
    if visible == PUBLIC or visible == FRIENDS:
        friend_list = get_all_home_member_list(user_id)
    else:
        friend_list = get_friend_from_group_id(visible, user_id)
    print 'friend list:', friend_list

    _send_msg = functools.partial(redis_tools.publish_moment_message, moment_id, user_id)
    map(_send_msg(user_id, moment_id), friend_list)


def get_moment_from_author_list(receiver, group_id):
    author_list = AuthorService.get_author_list_by_author_group(group_id)

    moments_list = []
    for author in author_list:
        temp_moment = get_moment_by_receiver_and_sender_id(receiver, author)
        moments_list.append(temp_moment)

    moments = reduce(lambda m1, m2: m1 | m2, moments_list)

    return moments


def get_moment_compare_with_begin_id(moment, compare, begin_id):
    '''
    if compare is None, give the neariest moments
    if begin_id is None, give the neariest moments
    '''
    PREVIOUS, AFTER = 'previous', 'after'
    POST_DATE = 'post_date'
    GREATER_THAN, LESS_THAN, MIN = '__gt', '__lt', '__min'
    # will be used in django query

    query = GREATER_THAN if compare == AFTER else LESS_THAN
    # if needs AFTER explicitly, need greather than, default is less than
    query_str = POST_DATE+query

    get_eariest_time = lambda: Moment.objects.aggregate(Min(POST_DATE)).get(POST_DATE + MIN, datetime.now())

    forget_give_less_than_begin = lambda query, moment: query == LESS_THAN and moment is None

    temp_moment = MomentService.get_moment(id=begin_id)

    if forget_give_less_than_begin(query, temp_moment):  # need less than query but not gave the begin id
        moment_date = datetime.now()
    else:
        moment_date = temp_moment.post_date if temp_moment else get_eariest_time()

    condition = {query_str: moment_date}         # get condition by compare key word
    # if compare said it need after, mean needs get new message, otherwish, get history message

    sort_order = '-' + POST_DATE  # sort message by time order from newer to older

   # if compare == AFTER:
    #    sort_order = POST_DATE  # if get unread message, order from older to newer

    return moment.filter(**condition).order_by(sort_order)  # ordered by post date reversed order


def confine_moment_number(moment, number):
    return moment[:number]


def get_moment_by_receiver_and_sender_id(receiver_id, sender_id):
    '''
    Author: Minchiuan 2016-2-24
    '''
    moments = None
    if receiver_id == sender_id:  # means get self's moments
        moments = MomentService.get_moments_from_user(receiver_id)
    elif sender_id is None:
        moments = MomentService.get_user_moments(user_id=receiver_id)
    else:
        sender_all_moment = MomentService.get_moments_from_user(user_id=sender_id)
        moments = MomentService.filter_public_moments(sender_all_moment)

    return moments


def have_same_elements(list_1):
    def contains(list_2):
        if list_2:
            return len(filter(lambda e: e in list_1, list_2)) > 0
        else:
            return False
    return contains


def get_moment_by_tags(moments, _TAGS):
    if len(_TAGS) > 0:
        contain_user_ask_tags = have_same_elements(_TAGS)
        return filter(lambda m: contain_user_ask_tags(m.tags), moments)
    else:
        return moments


def get_user_all_personal_tags(user_id):
    from collections import Counter

    tags = []
    moments = Moment.objects.filter(user_id=user_id)

    for m in moments:
        if m.tags and len(m.tags) > 0:
            tags += m.tags

    tags = Counter(tags).keys()

    return tags


def get_user_recommend_tags(user_id):
    return ['美食', '旅行', '悄悄话', '只对你说', '难忘的一天']


def get_user_all_tags(user_id):
    personsal = get_user_all_personal_tags(user_id)
    recommend = get_user_recommend_tags(user_id)

    return personsal, recommend

'''
Visible Service
Caculate if a person could see the momment or mark.
Author: Minchiuan Gao 2016-4-26
'''


def is_visible(moment_owver, message_sender, message_receiver):
    '''
    Message_sender sends a message(comment or mark) to one moment,
    Judge if message_receiver could see this message.
    '''
    return True


'''
Commemt Service Functions
Author: Minchiuan Gao 2016-4-26
'''


class BaseCommentService(object):

    factory_model = None

    @classmethod
    def add(cls, moment_id, sender_id, body):
        if cls.is_visible(moment_id, sender_id):
            target = cls.set_moment_and_sender(moment_id, sender_id)
            target = cls.set_target_content(target, body)
            return target
        else:
            raise ReferenceError

    @classmethod
    def set_moment_and_sender(cls, moment_id, sender_id):
        target = cls.factory_model()
        target.moment_id = moment_id
        target.sender_id = sender_id
        return target

    @classmethod
    def set_target_content(cls, model_target, body):
        '''
        Set model target content by request body.
        '''
        return

    @classmethod
    def cancle(cls, mid, user_id, body=None):
        '''
        Cancle a moment or mark.
            if the sender of the moment_id is the same as argument,
            set delete to true
        Raises:
            ReferenceError:
                when cannot find a moment_id's user_id is arg's user_id
        '''
        target = cls.factory_model.objects.filter(
             moment_id=mid, sender_id=user_id, deleted=False).first()
        if target:
            target.deleted = True
            target.save()
        else:
            raise ReferenceError

    @classmethod
    def is_visible(cls, user_id, moment_id):
        '''
        Test if this moment is visible to this user.
        '''
        return True

    @classmethod
    def get_visible_models(cls, moment_id, user_id, friends_visible_func):
        '''
        Gets mark, comment infomation.
        '''
        targets = cls.factory_model.objects \
            .filter(moment_id=moment_id) \
            .filter(deleted=False).order_by('created_at')

        targets = filter(friends_visible_func, targets)

        return targets

    @classmethod
    def get_content(cls, moment_id, user_id):
        '''
        Gets one person's moment activity info
        '''
        test_friends = cls.friends_visible_func(user_id)
        targets = cls.get_visible_models(
            moment_id, user_id, test_friends
        )

        return cls.produce_content(targets)

    @classmethod
    def friends_visible_func(cls, *args):
        '''
        Recognize if person is friends.
        '''
        return

    @classmethod
    def produce_content(cls, target_models):
        '''
        Take the target model and give the right information format.
        '''
        return

'''
Mark Service
Author: Minchiuan Gao 2016-4-26
'''


class MarkService(BaseCommentService):

    factory_model = Mark

    @classmethod
    def set_target_content(cls, model_target, body):
        MARK = 'mark'
        mark_type = body.get(MARK, None)
        try:
            model_target.mark_type = mark_type
            success = model_target.save()
            if success:
                return model_target.id
            else:
                return 'already marked'
        except Exception as e:
            raise e

    @classmethod
    def friends_visible_func(cls, user_id):  # m is a moment
        return lambda m: UserService.all_is_friend([user_id, m.sender_id])

    @classmethod
    def produce_content(cls, target_models):
        info = {}

        TOTAL, DETAIL = 'total', 'detail'

        for emotion, _ in Mark.TYPES:
            info[emotion] = {}
            this_emotion = filter(
                lambda m: m.mark_type == emotion, target_models)
            total_num = len(this_emotion)
            info[emotion][TOTAL] = total_num
            info[emotion][DETAIL] = []
            map(lambda m: info[emotion][DETAIL].append(str(m.sender_id)),
                this_emotion)

        return info

'''
Comment Service
Author: Minchiuan Gao 2016-4-5
'''


class CommentService(BaseCommentService):

    factory_model = Comment

    @classmethod
    def set_target_content(cls, model_target, body):
        MSG = 'msg'
        AT = 'at'

        msg = body.get(MSG, None)
        at = body.get(AT, None)

        model_target.specific_person = at
        model_target.content = msg
        model_target.save()
        return model_target.id

    @classmethod
    def friends_visible_func(cls, user_id):
        return lambda m: UserService.all_is_friend([
            user_id,
            m.sender_id,
            m.specific_person
        ])

    @classmethod
    def produce_content(cls, target_models):
        info = {}

        TOTAL, DETAIL = 'total', 'detail'

        SENDER, AT = 'sender', '@'
        info[TOTAL] = len(target_models)
        info[DETAIL] = []
        for m in target_models:
            info[DETAIL].append({
                SENDER: str(m.sender_id),
                AT: m.specific_person
            })

        return info
