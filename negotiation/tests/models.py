# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from ..decorators import negotiable


@negotiable
class Offer(models.Model):
    amount = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User)

    def __unicode__(self):
        return "Offer %s" % self.created

    def freeze(self):
        return {"value": self.amount}


@negotiable
class OfferWithoutFreeze(models.Model):
    amount = models.IntegerField()