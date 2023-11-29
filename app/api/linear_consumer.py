"""This module contains a function to consume the webhook, 
extract and generate the relevant data, and update the issue"""

from app.chain.chain import generate_ticket_details
from app.api.update_issue import update_issue

def consume_linear_webhook(data):
    '''Consume Linear webhook, and update issue'''

    if data["action"] != "create":
        return 'Action is not create', 200

    identifier = data["data"]["identifier"]
    description = data["data"]["title"]

    # TODO: Clean up this code
    try:
        generated_ticket_details = generate_ticket_details(description)
    except Exception as _:
        return 'Error generating ticket details', 500

    params = {
        "issue_id": identifier,
        "title": generated_ticket_details["title"],
        "description": generated_ticket_details["compiled_description"],
        "priority": generated_ticket_details["ticket_type"].priority,
    }

    # TODO: Handle gql errors
    _ = update_issue(**params)

    return 'Issue updated', 200
