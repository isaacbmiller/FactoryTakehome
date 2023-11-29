"""This module contains the function to mutate the issue using the Linear GraphQL API"""
import os

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

import dotenv

dotenv.load_dotenv()

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
API_URL = "https://api.linear.app/graphql"
SCHEMA_PATH = "./app/api/Linear-API@current.graphql"

transport = RequestsHTTPTransport(url=API_URL, headers={'Authorization': LINEAR_API_KEY})

with open(SCHEMA_PATH, encoding='utf-8') as f:
    schema_str = f.read()

client = Client(schema=schema_str, transport=transport)

# Set up the mutation to update an issue
issue_update_mutation = gql(
"""
mutation IssueUpdate($input: IssueUpdateInput!, $issueUpdateId: String!) {
    issueUpdate(input: $input, id: $issueUpdateId) {
        issue {
            id
        }
    }
}
"""
)

reaction_create_mutation = gql(
"""
mutation ReactionCreate($input: ReactionCreateInput!) {
  reactionCreate(input: $input) {
      success
  }
}
"""
)

def update_issue_info(issue_id, title, description, priority):
    '''Mutate the issue with the given id, and update the title, description, and priority'''
    priority_dict = {
        "urgent": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
    }

    try:
        _ = client.execute(
            issue_update_mutation,
            variable_values={
                "input": {
                    "title": title,
                    "description": description,
                    "priority": priority_dict[priority],
                },
                "issueUpdateId": issue_id,
            },
        )
        return
    except Exception as _:
        raise Exception("Error updating issue")

def update_issue_reaction(issue_uuid, emoji="robot_face"):
    '''Mutate the issue with the given id, and update the title, description, and priority'''
    try:
        _ = client.execute(
            reaction_create_mutation,
            variable_values={
                "input": {
                    "issueId": issue_uuid,
                    "emoji": emoji
                },
            },
        )
        return
    except Exception as _:
        raise Exception("Error updating issue reaction")

if __name__ == "__main__":
    update_issue_info("LIN-11", "This is a test title2", "This is a test description", "urgent")
