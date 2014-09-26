# coding=utf-8
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_syncdb
from permissions.models import Permission
from permissions.utils import register_role
from workflows.models import Workflow, State, WorkflowPermissionRelation
from business_workflow.models import WorkflowTransition
from . import models as negotiation_app
from . import NEGOTIATION_WORKFLOW_NAME


def create_negotiation_workflow(sender, **kwargs):

    ctype = ContentType.objects.get_for_model(sender.Negotiation)

    # create permissions
    last_updater, created = Permission.objects.get_or_create(
        name="Negotiation Last Updater",
        codename="LAST_UPDATER",
    )
    last_updater.content_types = [ctype]
    last_updater.save()
    counterpart, created = Permission.objects.get_or_create(
        name="Negotiation Counterpart",
        codename="COUNTERPART",
    )
    counterpart.content_types = [ctype]
    counterpart.save()

    #create roles
    register_role("Client")
    register_role("Seller")

    # create a workflow for negotiate stuff
    negotiation_workflow, created = Workflow.objects.get_or_create(
        name=NEGOTIATION_WORKFLOW_NAME,
    )

    # add all permissions which are managed by the workflow
    WorkflowPermissionRelation.objects.get_or_create(workflow=negotiation_workflow, permission=counterpart)
    WorkflowPermissionRelation.objects.get_or_create(workflow=negotiation_workflow, permission=last_updater)

    #  assign workflow to Negotiation model
    negotiation_workflow.set_to_model(ctype)

    # create workflow states
    initial_state, created = State.objects.get_or_create(
        name="Negotiating",
        workflow=negotiation_workflow
    )
    negotiation_workflow.initial_state = initial_state
    negotiation_workflow.save()

    success_state, created = State.objects.get_or_create(
        name="Accepted",
        workflow=negotiation_workflow
    )
    failure_state, created = State.objects.get_or_create(
        name="Cancelled",
        workflow=negotiation_workflow
    )

    # create workflow transitions and add them to the proper state(s)
    accept_transition, created = WorkflowTransition.objects.get_or_create(
        name="Accept",
        workflow=negotiation_workflow,
        destination=success_state,
        permission=counterpart,
        description="Accept the current proposal."
    )
    cancel_transition, created = WorkflowTransition.objects.get_or_create(
        name="Cancel",
        workflow=negotiation_workflow,
        destination=failure_state,
        permission=counterpart,
        description="Cancel the negotiation."
    )
    counteroffer_transition, created = WorkflowTransition.objects.get_or_create(
        name="Negotiate",
        workflow=negotiation_workflow,
        destination=initial_state,
        permission=counterpart,
        description="Make a counter-proposal."
    )
    modify_offer_transition, created = WorkflowTransition.objects.get_or_create(
        name="Modify",
        workflow=negotiation_workflow,
        destination=initial_state,
        permission=last_updater,
        description="Make a new modified proposal."
    )

    initial_state.transitions.add(accept_transition,
                                  cancel_transition,
                                  counteroffer_transition,
                                  modify_offer_transition)

post_syncdb.connect(create_negotiation_workflow, sender=negotiation_app)