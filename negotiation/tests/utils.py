# coding=utf-8
import logging
from django.core.cache import cache
from workflows import Workflow, Transition

logger = logging.getLogger(__name__)


def negotiation_workflow():
    _negotiation_workflow = cache.get('NEGOTIATION_WORKFLOW')
    if _negotiation_workflow is not None:
        return _negotiation_workflow
    try:
        _negotiation_workflow = Workflow.objects.get(name='NEGOTIATION_WORKFLOW')
        cache.set('NEGOTIATION_WORKFLOW', _negotiation_workflow)
        return _negotiation_workflow
    except Workflow.DoesNotExist as e:
        logger.exception(e)


def accept_transition():
    _accept_transition = cache.get('NEGOTIATION_ACCEPT_TRANSITION')
    if _accept_transition is not None:
        return _accept_transition
    try:
        _accept_transition = Transition.objects.get(name="Accept", workflow=negotiation_workflow())
        cache.set('NEGOTIATION_ACCEPT_TRANSITION', _accept_transition)
        return _accept_transition
    except Transition.DoesNotExist as e:
        logger.exception(e)


def cancel_transition():
    _cancel_transition = cache.get('NEGOTIATION_CANCEL_TRANSITION')
    if _cancel_transition is not None:
        return _cancel_transition
    try:
        _cancel_transition = Transition.objects.get(name="Cancel", workflow=negotiation_workflow())
        cache.set('NEGOTIATION_CANCEL_TRANSITION', _cancel_transition)
        return _cancel_transition
    except Transition.DoesNotExist as e:
        logger.exception(e)


def negotiate_transition():
    _negotiate_transition = cache.get('NEGOTIATION_NEGOTIATE_TRANSITION')
    if _negotiate_transition is not None:
        return _negotiate_transition
    try:
        _negotiate_transition = Transition.objects.get(name="Negotiate", workflow=negotiation_workflow())
        cache.set('NEGOTIATION_NEGOTIATE_TRANSITION', _negotiate_transition)
        return _negotiate_transition
    except Transition.DoesNotExist as e:
        logger.exception(e)


def modify_transition():
    _modify_transition = cache.get('NEGOTIATION_MODIFY_TRANSITION')
    if _modify_transition is not None:
        return _modify_transition
    try:
        _modify_transition = Transition.objects.get(name="Modify", workflow=negotiation_workflow())
        cache.set('NEGOTIATION_MODIFY_TRANSITION', _modify_transition)
        return _modify_transition
    except Transition.DoesNotExist as e:
        logger.exception(e)



