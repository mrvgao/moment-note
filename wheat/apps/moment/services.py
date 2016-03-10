# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.db.models import Q

from customs.services import BaseService
from apps.user.services import UserService
from apps.group.services import GroupService
from .models import Moment
from .serializers import MomentSerializer
from django.db.models import Min
from apps.book.services import AuthorService
from itertools import chain


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
        friend_ids = UserService.get_user_friend_ids(user_id)
        group_ids = GroupService.get_user_group_ids(user_id)
        moments = Moment.objects.filter(
            Q(Q(user_id__in=friend_ids) & Q(visible__in=['public', 'friends'])) |
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
    GREATER_THAN, LESS_THAN, MIN = '__gt', '__lt', '__min'  # will be used in django query

    query = GREATER_THAN if compare == AFTER else LESS_THAN  # if needs AFTER explicitly, need greather than, default is less than
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
