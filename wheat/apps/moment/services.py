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
from settings import REDIS_PUBSUB_DB
from utils.redis_utils import publish_redis_message
from .models import Comment
from .models import Mark
import abc


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

        if user_id and Moment.valid_content_type(content_type, content) \
                and Moment.valid_visible_field(visible):

            content = MomentService._fix_content(content)
            moment = Moment.objects.create(
                user_id=user_id,
                content_type=content_type,
                content=content,
                moment_date=moment_date,
                visible=visible)

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
        #friend_ids = UserService.get_user_friend_ids(user_id)
        group_ids = GroupService.get_user_group_ids(user_id)
        moments = Moment.objects.filter(
            #Q(Q(user_id__in=friend_ids) & Q(visible__in=['public', 'friends'])) |
            Q(Q(visible__in=['public', 'friends'])) |
            Q(visible__in=group_ids) |
            Q(user_id=user_id),
            deleted=False).order_by('post_date')
        return moments

    @classmethod
    def filter_public_moments(cls, moments):
        return moments.filter(Q(visible__in=['public', 'friends']))

    @classmethod
    def get_moments_from_user(cls, user_id):
        moments = Moment.objects.filter(
            user_id=user_id,
            deleted=False).order_by('post_date')
        return moments

    @staticmethod
    def get_recent_moment(user_id):
        try:
            moment = MomentService.get_moment(user_id=user_id)
            return moment.id, moment.post_date
        except Exception as e:
            print e
            return None, None


def _send_msg(sender_id, moment_id):
    def send_redis(receiver_id):
        message = {
            'sender': sender_id,
            'moment_id': moment_id,
            'receiver_id': receiver_id,
            'event': 'moment'
        }

        publish_redis_message(REDIS_PUBSUB_DB, 'moment->', message)
        print('send msg to ' + receiver_id)

    return send_redis


def _notify_moment_to_firends(visible, user_id, moment_id):
    from apps.group.services import get_friend_from_group_id
    from apps.group.services import get_all_home_member_list

    PUBLIC, FRIENDS = 'public', 'friends'
    if visible == PUBLIC or visible == FRIENDS:
        friend_list = get_all_home_member_list(user_id)
    else:
        friend_list = get_friend_from_group_id(visible, user_id)
    print 'friend list:', friend_list

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


def create_comment_or_mark(Statement, moment_id, sender_id, receiver_id=None):
    new_statement = Statement()
    if receiver_id is not None:
        new_statement.if_to_specific_person = True
        new_statement.receiver_id = receiver_id
    new_statement.moment_id = moment_id
    new_statement.sender_id = sender_id
    new_statement.save()


def cancle_comment_or_mark(Statement, moment_id):
    pass

'''
Commemt Service Functions
Author: Minchiuan Gao 2016-4-26
'''


class BaseCommentService(object):
    __metaclass__ = abc.ABCMeta

    factory_model = None

    def add(self, moment_id, sender_id, body):
        if self.is_visible(moment_id, sender_id):
            target = self.set_moment_and_sender(moment_id, sender_id)
            target = self.set_target_content(target, body)
            return target
        else:
            raise ReferenceError

    def set_moment_and_sender(self, moment_id, sender_id, body):
        target = BaseCommentService.factory_model()
        target.moment_id = moment_id
        target.sender_id = sender_id
        target.save()
        return target

    @abc.abstractmethod
    def set_target_content(self, model_target, body):
        '''
        Set model target content by request body.
        '''
        return

    def cancle(self, moment_id, user_id, body=None):
        '''
        Cancle a moment or mark.
            if the sender of the moment_id is the same as argument,
            set delete to true
        Raises:
            ReferenceError:
                when cannot find a moment_id's user_id is arg's user_id
        '''
        target = self.get_or_none(moment_id=moment_id, sneder_id=user_id)
        if target:
            self.deleted = False
            self.save()
        else:
            raise ReferenceError

    def is_visible(self, user_id, moment_id):
        '''
        Test if this moment is visible to this user.
        '''
        return True

    def get_comment_info(moment_id, user_id):
        '''
        Gets mark info, marks total number and mark's person.
        Returns:
            (total_number, marked_person_id_list)
        '''


'''
Mark Service
Author: Minchiuan Gao 2016-4-26
'''


class MarkService(BaseCommentService):

    factory_model = Mark

    def set_target_content(self, model_target, body):
        MARK = 'mark'
        mark_type = body.get(MARK, None)
        try:
            model_target.mark_type = mark_type
            model_target.save()
            return model_target
        except Exception as e:
            raise e

'''
Comment Service
Author: Minchiuan Gao 2016-4-5
'''


class CommentService(BaseCommentService):

    factory_model = Comment

    def set_target_content(self, model_target, body):
        MSG = 'msg'
        AT = 'at'

        msg = body.get(MSG, None)
        at = body.get(AT, None)

        model_target.specific_person = at
        model_target.content = msg
        model_target.save()
        return model_target
