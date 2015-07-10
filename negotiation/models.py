# coding=utf-8
import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _
from permissions.models import Role, Permission
from permissions.utils import grant_permission, remove_permission, get_local_roles
from workflows.decorators import workflow_enabled
from workflows.models import WorkflowHistorical

logger = logging.getLogger(__name__)


def counterpart_permission():
    counterpart = cache.get('NEGOTIATION_COUNTERPART_PERMISSION')
    if counterpart is not None:
        return counterpart
    try:
        counterpart = Permission.objects.get(codename="COUNTERPART")
        cache.set('NEGOTIATION_COUNTERPART_PERMISSION', counterpart)
        return counterpart
    except ObjectDoesNotExist as e:
        logger.exception(e)


def last_updater_permission():
    last_updater = cache.get('NEGOTIATION_LAST_UPDATER_PERMISSION')
    if last_updater is not None:
        return last_updater
    try:
        last_updater = Permission.objects.get(codename="LAST_UPDATER")
        cache.set('NEGOTIATION_LAST_UPDATER_PERMISSION', last_updater)
        return last_updater
    except ObjectDoesNotExist as e:
        logger.exception(e)


def client_role():
    client = cache.get('NEGOTIATION_CLIENT_ROLE')
    if client is not None:
        return client
    try:
        client = Role.objects.get(name="Client")
        cache.set('NEGOTIATION_CLIENT_ROLE', client)
        return client
    except ObjectDoesNotExist as e:
        logger.exception(e)


def seller_role():
    seller = cache.get('NEGOTIATION_SELLER_ROLE')
    if seller is not None:
        return seller
    try:
        seller = Role.objects.get(name="Seller")
        cache.set('NEGOTIATION_SELLER_ROLE', seller)
        return seller
    except ObjectDoesNotExist as e:
        logger.exception(e)


class NegotiationManager(models.Manager):

    def client_for_model(self, user, model):
        ctype = ContentType.objects.get_for_model(model)
        negotiation_parts_ids = NegotiationPart.objects.filter(pk__in=user.groups.all())
        return self.get_queryset().filter(content_type=ctype).filter(client__in=negotiation_parts_ids)

    def seller_for_model(self, user, model):
        ctype = ContentType.objects.get_for_model(model)
        negotiation_parts_ids = NegotiationPart.objects.filter(pk__in=user.groups.all())
        return self.get_queryset().filter(content_type=ctype).filter(seller__in=negotiation_parts_ids)


class NegotiationPart(Group):

    class Meta:
        proxy = True

    @property
    def users(self):
        return set(self.user_set.all())

    def make_last_updater(self, negotiation):
        role = (local_rol for local_rol in get_local_roles(negotiation, self)
                if local_rol in {client_role(), seller_role()}).next()
        remove_permission(negotiation, role, counterpart_permission())
        grant_permission(negotiation, role, last_updater_permission())

    def make_counterpart(self, negotiation):
        role = (local_rol for local_rol in get_local_roles(negotiation, self)
                if local_rol in {client_role(), seller_role()}).next()
        remove_permission(negotiation, role, last_updater_permission())
        grant_permission(negotiation, role, counterpart_permission())


@workflow_enabled
class Negotiation(models.Model):
    # Content-object field
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name="%(class)ss")
    content_pk = models.IntegerField(_('content ID'))
    content = GenericForeignKey(ct_field="content_type", fk_field="content_pk")

    # Starter
    starter = models.ForeignKey(User)

    # Client field
    client = models.ForeignKey(NegotiationPart, related_name="as_client")

    # Seller field
    seller = models.ForeignKey(NegotiationPart, related_name="as_seller")

    # Notes
    notes = models.TextField(max_length=1000, null=True)

    # Metadata
    updated = models.DateTimeField(auto_now=True)

    # Custom Manager
    objects = NegotiationManager()

    class Meta:
        unique_together = ('content_type', 'content_pk')  # only one negotiation for a content object
        ordering = ('current_state',)

    def init_permissions(self):
        # set initial permissions for each part
        acting_part, counter_part = (self.client, self.seller) if self.starter in self.client.users \
            else (self.seller, self.client)
        acting_part.make_last_updater(self)
        counter_part.make_counterpart(self)

    @property
    def history_comment(self):
        content_dict = self.content.freeze()
        return json.dumps({'content': content_dict,
                           'notes': self.notes})

    def _load_history_item(self, version):
        item = json.loads(version.comment)
        item.update({
            'updater': version.user,
            'updated': version.update_at
        })
        return item

    def history(self, recent_first=True):
        versions = WorkflowHistorical.objects.get_history_from_object_query_set(self)
        if recent_first:
            versions = versions.order_by('-update_at')
        else:
            versions = versions.order_by('update_at')
        return (self._load_history_item(version) for version in versions)

    def _initiator(self):
        role = client_role() if self.starter in self.client.users else seller_role()
        return self.starter, role

    @property
    def initiator(self):
        return self._initiator()

    def _last_updater(self):
        history_gen = (version for version in self.history())
        try:
            last_version = history_gen.next()
            updater = last_version['updater']
            role = client_role() if updater in self.client.users else seller_role()
        except StopIteration:
            return None
        return updater, role

    @property
    def last_updater(self):
        return self._last_updater()

    def is_last_updater(self, user):
        return user == self.last_updater[0]

    def has_last_updater_permissions(self, user):
        last_updater_role = self.last_updater[1]
        return (
            user in self.client.users and last_updater_role == client_role()
        ) or (
            user in self.seller.users and last_updater_role == seller_role()
        )

    def _last_client_proposal(self):
        client_versions_gen = (version for version in self.history() if version['updater'] in self.client.users)
        try:
            return client_versions_gen.next()
        except StopIteration:
            return None

    @property
    def last_client_proposal(self):
        return self._last_client_proposal()

    def _last_seller_proposal(self):
        seller_versions_gen = (version for version in self.history() if version['updater'] in self.seller.users)
        try:
            return seller_versions_gen.next()
        except StopIteration:
            return None

    @property
    def last_seller_proposal(self):
        return self._last_seller_proposal()

    def last_proposal_from(self, user):
        return self.last_client_proposal if self.is_client(user) else self.last_seller_proposal

    def last_counterpart_proposal_for(self, user):
        return self.last_seller_proposal if self.is_client(user) else self.last_client_proposal

    def is_client(self, user):
        return user in self.client.users

    def is_seller(self, user):
        return user in self.seller.users

    def _save_notes(self, notes):
        self.notes = notes
        self.save()

    def accept(self, user, notes="", **kwargs):
        self._save_notes(notes)
        return self.do_accept(user, self.history_comment)

    def cancel(self, user, notes="", **kwargs):
        self._save_notes(notes)
        return self.do_cancel(user, self.history_comment)

    def negotiate(self, user, notes="", **kwargs):
        self._save_notes(notes)
        result = self.do_negotiate(user, self.history_comment)
        # update permissions for each part
        acting_part, counter_part = (self.client, self.seller) if user in self.client.users else (self.seller, self.client)
        acting_part.make_last_updater(self)
        counter_part.make_counterpart(self)
        return result

    def modify(self, user, notes="", **kwargs):
        self._save_notes(notes)
        result = self.do_modify(user, self.history_comment)
        # update permissions for each part
        acting_part, counter_part = (self.client, self.seller) if user in self.client.users else (self.seller, self.client)
        acting_part.make_last_updater(self)
        counter_part.make_counterpart(self)
        return result

    def status_for(self, user):
        statuses = {
            'LAST_UPDATER': (_(u'WAITING FOR COUNTERPART'), 'waiting'),
            'COUNTERPART': (_(u'PENDING ACTION'), 'pending'),
            'ACCEPTED': (_(u'ACCEPTED'), 'accepted'),
            'CANCELLED': (_(u'CANCELLED'), 'cancelled'),
        }
        state_name = self.current_state.name.upper()
        if state_name == 'NEGOTIATING':
            state_name = 'LAST_UPDATER' if self.is_last_updater(user) else 'COUNTERPART'

        return statuses[state_name]