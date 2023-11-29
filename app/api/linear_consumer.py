"""This module contains a function to consume the webhook, 
extract and generate the relevant data, and update the issue"""

from app.chain.chain import generate_ticket_details
from app.api.update_issue import update_issue_info, update_issue_reaction

def consume_linear_webhook(data):
    '''Consume Linear webhook, and update issue'''

    if data.get("action") and data["action"] != "create":
        return 'Action is not create', 200

    if data.get("data") and data["data"].get("identifier") and data["data"].get("title"):
        identifier = data["data"]["identifier"]
        description = data["data"]["title"]
    else:
        return 'Missing identifier or title', 400

    try:
        if data["data"].get("id"):
            issue_uuid = data["data"]["id"]
            update_issue_reaction(issue_uuid)
    except Exception as _:
        # Would Log error in reality
        # Reaction is not important enough to abort execution
        pass

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

    try:
        update_issue_info(**params)
        return 'Issue updated', 200
    except Exception as _:
        return 'Error updating issue', 500
