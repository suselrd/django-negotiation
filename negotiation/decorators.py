# coding=utf-8
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.auth.models import Group
from models import Negotiation, NegotiationPart


class ExtendedNegotiableQuerysetMixin(object):

    def negotiating(self):
        return self.filter(negotiations__current_state__name='Negotiating')

    def accepted(self):
        return self.filter(negotiations__current_state__name='Accepted')

    def cancelled(self):
        return self.filter(negotiations__current_state__name='Cancelled')


class ExtendedNegotiableManagerMixin(object):

    def negotiating(self):
        return self.get_queryset().negotiating()

    def accepted(self):
        return self.get_queryset().accepted()

    def cancelled(self):
        return self.get_queryset().cancelled()


def negotiate(self, client, seller, notes):
    if self.negotiation is not None:
        return  # only one instance of negotiation allowed per negotiable object

    if not isinstance(client, Group):
        group = Group.objects.create(name="%s-%s" % (str(self), "client"))
        group.user_set.add(client)
        client = group
    if not isinstance(client, NegotiationPart):
        client = NegotiationPart(client.pk)

    if not isinstance(seller, Group):
        group = Group.objects.create(name="%s-%s" % (str(self), "seller"))
        group.user_set.add(seller)
        seller = group
    if not isinstance(seller, NegotiationPart):
        seller = NegotiationPart(seller.pk)

    new_negotiation = Negotiation(
        starter=self.creator,
        content=self,
        client=client,
        seller=seller,
        notes=notes
    )
    new_negotiation.save(user=self.creator, comment=new_negotiation.history_comment)
    new_negotiation.init_permissions()
    return True


def freeze(self):
    raise NotImplementedError("Negotiable classes must implement a freeze(self) method.")


@property
def creator(self):
    raise NotImplementedError("Negotiable classes must either have a creator property or a creator field.")


@property
def negotiation(self):
    try:
        return self.negotiations.all()[0]
    except IndexError:
        return None


@property
def is_negotiating(self):
    try:
        return self.negotiation.is_negotiating
    except AttributeError:
        return None


@property
def is_accepted(self):
    try:
        return self.negotiation.is_accepted
    except AttributeError:
        return None


@property
def is_cancelled(self):
    try:
        return self.negotiation.is_cancelled
    except AttributeError:
        return None


@property
def is_accepted(self):
    try:
        return self.negotiation.is_accepted
    except AttributeError:
        return None


def status_for(self, user):
    try:
        return self.negotiation.status_for(user)
    except AttributeError:
        return None


def accept(self, user, notes="", **kwargs):
    try:
        return self.negotiation.accept(user, notes, **kwargs)
    except AttributeError:
        return False


def cancel(self, user, notes="", **kwargs):
    try:
        return self.negotiation.cancel(user, notes, **kwargs)
    except AttributeError:
        return False


def counter_proposal(self, user, notes="", **kwargs):
    try:
        return self.negotiation.negotiate(user, notes, **kwargs)
    except AttributeError:
        return False


def modify_proposal(self, user, notes="", **kwargs):
    try:
        return self.negotiation.modify(user, notes, **kwargs)
    except AttributeError:
        return False


def is_client(self, user):
    try:
        return self.negotiation.is_client(user)
    except AttributeError:
        return False


def is_seller(self, user):
    try:
        return self.negotiation.is_seller(user)
    except AttributeError:
        return False


def last_proposal_from(self, user):
    try:
        return self.negotiation.last_proposal_from(user)
    except AttributeError:
        return None


def last_counterpart_proposal_for(self, user):
    try:
        return self.negotiation.last_counterpart_proposal_for(user)
    except AttributeError:
        return None


@property
def last_seller_proposal(self):
    try:
        return self.negotiation.last_seller_proposal
    except AttributeError:
        return None


@property
def last_client_proposal(self):
    try:
        return self.negotiation.last_client_proposal
    except AttributeError:
        return None


@property
def initiator(self):
    try:
        return self.negotiation.initiator
    except AttributeError:
        return None


@property
def last_updater(self):
    try:
        return self.negotiation.last_updater
    except AttributeError:
        return None


def is_last_updater(self, user):
    try:
        return self.negotiation.is_last_updater(user)
    except AttributeError:
        return False


def history(self, recent_first=True):
    try:
        return self.negotiation.history(recent_first)
    except AttributeError:
        return None


def negotiation_options(self, user):
    try:
        return self.negotiation.get_allowed_transitions(user)
    except AttributeError:
        return []


def negotiable(cls):
    # EXTEND NEGOTIABLE CLASS

    # add the default for mandatory method 'freeze'
    if not hasattr(cls, 'freeze') or not callable(getattr(cls, 'freeze')):
        setattr(cls, 'freeze', freeze)

    # add the mandatory 'creator' property
    if not hasattr(cls, 'creator'):
        setattr(cls, 'creator', creator)

    # add the generic relation field to negotiable class
    negotiations = GenericRelation(Negotiation, object_id_field='content_pk', content_type_field='content_type')
    negotiations.contribute_to_class(cls, 'negotiations')

    # add the negotiation property
    setattr(cls, 'negotiation', negotiation)

    # add the negotiate method
    setattr(cls, 'negotiate', negotiate)

    # add the status_for method
    setattr(cls, 'status_for', status_for)

    # add the accept method
    setattr(cls, 'accept', accept)

    # add the cancel method
    setattr(cls, 'cancel', cancel)

    # add the counter_proposal method
    setattr(cls, 'counter_proposal', counter_proposal)

    # add the modify_proposal method
    setattr(cls, 'modify_proposal', modify_proposal)

    # add the is_negotiating property
    setattr(cls, 'is_negotiating', is_negotiating)

    # add the is_accepted property
    setattr(cls, 'is_accepted', is_accepted)

    # add the is_cancelled property
    setattr(cls, 'is_cancelled', is_cancelled)

    # add the is_seller method
    setattr(cls, 'is_seller', is_seller)

    # add the is_client method
    setattr(cls, 'is_client', is_client)

    # add the last_proposal_from method
    setattr(cls, 'last_proposal_from', last_proposal_from)

    # add the last_counterpart_proposal_for method
    setattr(cls, 'last_counterpart_proposal_for', last_counterpart_proposal_for)

    # add the last_client_proposal property
    setattr(cls, 'last_client_proposal', last_client_proposal)

    # add the last_seller_proposal property
    setattr(cls, 'last_seller_proposal', last_seller_proposal)

    # add the initiator property
    setattr(cls, 'initiator', initiator)

    # add the last_updater property
    setattr(cls, 'last_updater', last_updater)

    # add the is_last_updater method
    setattr(cls, 'is_last_updater', is_last_updater)

    # add the history method
    setattr(cls, 'history', history)

    # add the negotiation_options method
    setattr(cls, 'negotiation_options', negotiation_options)

    # EXTEND NEGOTIABLE CLASS'S MANAGERS AND QUERYSETS

    cls._meta.concrete_managers.sort()
    managers = [(mgr_name, manager) for _, mgr_name, manager in cls._meta.concrete_managers]

    setattr(cls, '_default_manager', None)  # clean the default manager
    setattr(cls._meta, 'concrete_managers', [])  # clean the managers

    for mgr_name, manager in managers:

        class ExtendedNegotiableManager(ExtendedNegotiableManagerMixin, manager.__class__):

            class ExtendedNegotiableQueryset(ExtendedNegotiableQuerysetMixin, manager.get_queryset().__class__):
                pass

            def get_queryset(self):
                return self.ExtendedNegotiableQueryset(self.model, using=self._db)

        cls.add_to_class(mgr_name, ExtendedNegotiableManager())

    return cls