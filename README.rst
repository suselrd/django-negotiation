==========================
Django Negotiation
==========================

Negotiation Workflow Management for Django>=1.6.1


Changelog
=========

0.3.0
-----
Added convenient methods to negotiable models, to return whether the instance has currently a specific state or not.
Example usage:
   if negotiable.is_accepted:
        ## do something
   elif negotiable.is_cancelled:
        ## do something else
   elif negotiable.is_negotiating:
        ## last case, do something appropriate
   else:
        pass  # unexpected results


Added convenient methods to negotiable models managers, to filter instances by a specific current state.
Example usage:
    accepted_list = Negotiable.objects.accepted(),
    cancelled_count = Negotiable.objects.cancelled().count()
    negotiating_list = Negotiable.objects.negotiating()
** Note: assuming that 'Negotiable' is a Django model, decorated with @negotiable

0.2.0
-----

Replaced dependencies django-workflows and django-business-workflow for django-wflow.
Added convenient methods to negotiable models, to handle its correspondent negotiation.
Added new custom template tags, to access a negotiable clients and sellers (and render them properly), without having to
access its correspondent negotiation object.


0.1.2
-----

Added new method 'has_last_updater_permissions' to negotiation objects.
New templatetag 'has_last_updater_permissions' that calls this new method.

0.1.1
-----

Template tag 'render_members' now generates links to the user's profile absolute url (if any).

0.1.0
-----

PENDING...

Notes
-----

PENDING...

Usage
-----

1. Run ``python setup.py install`` to install.

2. Modify your Django settings to use ``negotiation``: