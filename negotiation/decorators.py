# coding=utf-8
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.auth.models import Group
from .models import Negotiation, NegotiationPart


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
    new_negotiation.save(user=self.creator)
    new_negotiation.init_permissions()
    return True


def freeze(self):
    raise NotImplementedError("Negotiable classes must implement a freeze(self) method.")

@property
def creator(self):
    raise NotImplementedError("Negotiable classes must either have an creator property or an creator field.")

@property
def negotiation(self):
    try:
        return self.negotiations.all()[0]
    except IndexError:
        return None


def negotiable(cls):
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

    return cls