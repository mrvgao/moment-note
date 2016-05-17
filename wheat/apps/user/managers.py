# -*- coding:utf-8 -*-

from django.db import models
from datetime import datetime
from django.contrib.auth.models import BaseUserManager

from customs.models import CacheableManager


class ActivatedUserManager(models.Manager):

    def get_queryset(self):
        return super(ActivatedUserManager, self).get_queryset().filter(activated=True)


class UserManager(BaseUserManager, CacheableManager):

    def create_user(self, phone, password, **kwargs):
        user = self.model(
            phone=phone,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **kwargs):
        user = self.create_user(phone, password, **kwargs)
        user.is_admin = True
        user.activated = True
        user.activated_at = datetime.now()
        user.save()


class AuthTokenManager(CacheableManager):

    def refresh_token(self, token):
        if token:
            token.key = token.generate_key()
            token.save()
        return token
