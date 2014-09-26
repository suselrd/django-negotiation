#coding=utf-8
import logging
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def render_negotiation_options(context, negotiable, scope='', kwargs={}):
    if negotiable.negotiation is not None:
        ctype = ContentType.objects.get_for_model(negotiable)
        template_search_list = [
            "%s/%s/%s/negotiation_buttons.html" % (ctype.app_label, ctype.model, scope),
            "%s/%s/negotiation_buttons.html" % (ctype.app_label, ctype.model),
            "%s/negotiation_buttons.html" % ctype.app_label,
            "negotiation_buttons.html",
        ]
        return render_to_string(
            template_search_list, {
                'object': negotiable,
                'transitions': negotiable.negotiation.get_allowed_transitions(
                    context['user']
                ),
                'user': context['user']
            }
        )
    else:
        return ''


@register.filter
def is_last_updater(negotiable, user):
    """
    Returns whether a user is the last updater of the passed negotiable or not.
    """
    #noinspection PyBroadException
    try:
        return negotiable.negotiation.is_last_updater(user)
    except Exception as e:
        logger.exception(e)
        return False


@register.filter
def members(negotiation_part):
    if negotiation_part is not None:
        _members = [user.get_full_name() for user in negotiation_part.users]
        return ', '.join(_members)
    else:
        return ''


@register.simple_tag
def render_members(negotiation_part):
    if negotiation_part is not None:
        tpl = "<a href='%s'>%s</a>"  # TODO add the permalink of the user profile
        _members = [tpl % ('#', user.get_full_name()) for user in negotiation_part.users]
        return ', '.join(_members)
    else:
        return ''