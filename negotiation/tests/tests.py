# coding=utf-8
from django.contrib.auth.models import User
from django.test import TestCase
from ..models import client_role
from models import Offer, OfferWithoutFreeze
from utils import accept_transition, cancel_transition, negotiate_transition, modify_transition


class NegotiationTest(TestCase):

    def setUp(self):
        self.users = {
            'client1': User.objects.create(username='pedro'),
            'client2': User.objects.create(username='juan'),
            'seller': User.objects.create(username='pablo')
        }
        self.offer = Offer.objects.create(amount=1000, creator=self.users['client1'])
        self.bad_offer = OfferWithoutFreeze.objects.create(amount=1000)

    def test_decorator(self):
        # negotiate an Offer instance
        self.offer.negotiate(self.users['client1'], self.users['seller'], "I offer 1000 dollars.")
        self.assertTrue(self.offer.is_client(self.users['client1']))
        self.assertTrue(self.offer.is_seller(self.users['seller']))
        self.assertEqual(self.offer.negotiation.content, self.offer)
        self.assertEqual(self.offer.negotiation.notes, "I offer 1000 dollars.")

        # try to negotiate an OfferWithoutFreeze instance
        self.assertRaises(NotImplementedError, self.bad_offer.negotiate, self.users['client1'], self.users['seller'],
                          "I offer 1000 dollars.")

    def test_permissions(self):
        self.offer.negotiate(self.users['client1'], self.users['seller'], "I offer 1000 dollars.")
        self.assertEqual(len(self.offer.negotiation_options(self.users['client1'])), 1)
        self.assertIn(modify_transition(), self.offer.negotiation_options(self.users['client1']))

        # modify a previous offer and execute corresponding WF transition
        self.offer.amount = 900
        self.offer.save()
        self.offer.modify_proposal(self.users['client1'], "I changed my mind, I offer 900 dollars now.")
        self.assertEqual(len(self.offer.negotiation_options(self.users['client1'])), 1)
        self.assertIn(modify_transition(), self.offer.negotiation_options(self.users['client1']))
        self.assertEqual(len(self.offer.negotiation_options(self.users['seller'])), 3)
        self.assertIn(accept_transition(), self.offer.negotiation_options(self.users['seller']))
        self.assertIn(cancel_transition(), self.offer.negotiation_options(self.users['seller']))
        self.assertIn(negotiate_transition(), self.offer.negotiation_options(self.users['seller']))

        # counter offer and execute corresponding WF transition
        self.offer.amount = 950
        self.offer.save()
        self.offer.counter_proposal(self.users['seller'], "I can only do 950.")
        self.assertEqual(len(self.offer.negotiation_options(self.users['seller'])), 1)
        self.assertIn(modify_transition(), self.offer.negotiation_options(self.users['seller']))
        self.assertEqual(len(self.offer.negotiation_options(self.users['client1'])), 3)
        self.assertIn(accept_transition(), self.offer.negotiation_options(self.users['client1']))
        self.assertIn(cancel_transition(), self.offer.negotiation_options(self.users['client1']))
        self.assertIn(negotiate_transition(), self.offer.negotiation_options(self.users['client1']))

    def test_transitions(self):
        self.offer.negotiate(self.users['client1'], self.users['seller'], "I offer 1000 dollars.")

        # modify a previous offer and execute corresponding WF transition
        self.offer.amount = 900
        self.offer.save()
        self.offer.modify_proposal(self.users['client1'], "I changed my mind, I offer 900 dollars now.")
        self.assertEqual(len([version for version in self.offer.history()]), 2)
        self.assertEqual(self.offer.last_client_proposal['content']['value'], 900)
        self.assertEqual(self.offer.last_seller_proposal, None)

        # counter offer and execute corresponding WF transition
        self.offer.amount = 950
        self.offer.save()
        self.offer.counter_proposal(self.users['seller'], "I can only do 950.")
        self.assertEqual(len([version for version in self.offer.history()]), 3)
        self.assertEqual(self.offer.last_client_proposal['content']['value'], 900)
        self.assertEqual(self.offer.last_seller_proposal['content']['value'], 950)

    def test_initiator_property(self):
        self.offer.negotiate(self.users['client1'], self.users['seller'], "I offer 1000 dollars.")
        initiator = self.offer.initiator
        self.assertEqual(initiator[0], self.users['client1'])
        self.assertEqual(initiator[1], client_role())
