from typing import Dict

from ixoncdkingress.cbc.context import CbcContext

from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket

import json


@CbcContext.expose
def get_zendesk_tickets(context: CbcContext):
    if not context.agent and not context.asset:
        return {'status': 'error', 'message': 'No agent or asset found'}

    zenpy_client = Zenpy(**_get_zendesk_creds_from_context(context))
    custom_fields = _get_custom_fields_from_context(context, zenpy_client)

    if not any(custom_field['value'] for custom_field in custom_fields) or not any(custom_field['id'] for custom_field in custom_fields):
        return {'status': 'error', 'message': 'At least one custom field value is required to map machine to a zendesk ticket. Make sure it has a value in IXON Cloud and is created in Zendesk and configured in the app config'}

    kwargs = {'type': 'ticket', 'sort_by': 'created_at', 'sort_order': 'desc'}
    for custom_field in custom_fields:
        a = f"custom_field_{custom_field['id']}"
        kwargs[a] = custom_field['value']

    results = zenpy_client.search(**kwargs)

    tickets = [ticket for ticket in results]
    tickets = [{'id': ticket.id, 'description': ticket.description, 'status': ticket.status,
                'priority': ticket.priority, 'createdAt': ticket.created_at} for ticket in tickets]

    return {'status': 'success', 'tickets': tickets}


@CbcContext.expose
def create_ticket(
        context: CbcContext, ticket_description, ticket_priority):
    zenpy_client = Zenpy(**_get_zendesk_creds_from_context(context))

    if not ticket_description or not ticket_priority:
        return {'status': 'error', 'message': 'Ticket description and priority are required'}

    ticket_priority = ticket_priority.lower()
    if ticket_priority not in ['low', 'normal', 'high', 'urgent']:
        return {'status': 'error', 'message': 'Ticket priority can only be low, normal, high or urgent'}

    ixon_user = _get_user(context)

    user = User(name=ixon_user['name'], email=ixon_user['emailAddress'])
    user = zenpy_client.users.create_or_update(user)

    custom_fields = _get_custom_fields_from_context(context, zenpy_client)

    ticket = Ticket(
        requester=User(id=user.id, email=user.email, name=user.name),
        description=ticket_description, priority=ticket_priority,
        custom_fields=custom_fields)
    ticket = zenpy_client.tickets.create(ticket)

    if (ticket):
        return {'status': 'success', 'message': 'Ticket created successfully'}
    else:
        return {'status': 'error', 'message': 'Ticket creation failed'}


def _get_user(context: CbcContext):
    response = context.api_client.get(
        'User',
        url_args={'publicId': context.user.public_id})
    return response['data']


def _get_zendesk_creds_from_context(context: CbcContext):
    zendesk_creds = {
        "email": context.config.get("zendesk_email"),
        "token": context.config.get("zendesk_token"),
        "subdomain": context.config.get("zendesk_subdomain")}
    return zendesk_creds


def _get_custom_fields_from_context(context: CbcContext, zenpy_client):
    custom_fields = context.config.get("custom_fields")
    if (not custom_fields):
        return []
    if isinstance(custom_fields, str):
        custom_fields = custom_fields.replace("'", '"')
        custom_fields = json.loads(custom_fields)

    ticket_fields = zenpy_client.ticket_fields()

    for custom_field in custom_fields:
        field_id = custom_field.pop('zendesk')
        ticket_field = next(
            (field for field in ticket_fields if field.id == field_id), None)

        custom_field['id'] = field_id if ticket_field else None
        custom_field['value'] = context.agent_or_asset.custom_properties.get(
            custom_field.pop('ixon'))
    return custom_fields
