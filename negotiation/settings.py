# coding=utf-8
from django.conf import settings as django_settings

# WORKFLOWS DEFINITIONS

WORKFLOWS = {
    'negotiation.models.Negotiation': {
        'name': 'NEGOTIATION_WORKFLOW',
        'roles': ['Client', 'Seller'],
        'permissions': [
            {
                'name': 'Negotiation Last Updater',
                'codename': 'LAST_UPDATER',
            },
            {
                'name': 'Negotiation Counterpart',
                'codename': 'COUNTERPART',
            },
        ],
        'initial_state': {
            'name': 'Negotiating',
            'state_perm_relation': []
        },
        'states': [
            {
                'name': 'Accepted',
                'state_perm_relation': []
            },
            {
                'name': 'Cancelled',
                'state_perm_relation': []
            },
        ],
        'transitions': [
            {
                'name': 'Accept',
                'destination': 'Accepted',
                'permission': 'COUNTERPART',
                'description': 'Accept the current proposal.',
            },
            {
                'name': 'Cancel',
                'destination': 'Cancelled',
                'permission': 'COUNTERPART',
                'description': 'Cancel the negotiation.',
            },
            {
                'name': 'Negotiate',
                'destination': 'Negotiating',
                'permission': 'COUNTERPART',
                'description': 'Make a counter-proposal.',
            },
            {
                'name': 'Modify',
                'destination': 'Negotiating',
                'permission': 'LAST_UPDATER',
                'description': 'Make a new modified proposal.',
            },
        ],
        'state_transitions': {
            'Negotiating': ['Accept', 'Cancel', 'Negotiate', 'Modify'],
        },
        'user_roles': [
            {
                'user_path': 'client',
                'role': 'Client'
            },
            {
                'user_path': 'seller',
                'role': 'Seller'
            },
        ]
    }
}

# APPLICATION WORKFLOWS
workflows = getattr(django_settings, 'WORKFLOWS', {})
workflows.update(WORKFLOWS)
setattr(django_settings, 'WORKFLOWS', workflows)