"""This module contains the function to mutate the issue using the Linear GraphQL API"""
import os

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

import dotenv

dotenv.load_dotenv()

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")

transport = RequestsHTTPTransport(url="https://api.linear.app/graphql", headers={'Authorization': LINEAR_API_KEY})

with open('./app/models/Linear-API@current.graphql', encoding='utf-8') as f:
    schema_str = f.read()

client = Client(schema=schema_str, transport=transport)

# Set up the mutation to update an issue
mutation = gql(
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

def update_issue(issue_id, title, description, priority):
    '''Mutate the issue with the given id, and update the title, description, and priority'''
    priority_dict = {
        "urgent": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
    }

    result = client.execute(
        mutation,
        variable_values={
            "input": {
                "title": title,
                "description": description,
                "priority": priority_dict[priority],
            },
            "issueUpdateId": issue_id,
        },
    )
    return result

if __name__ == "__main__":
    issue = update_issue("LIN-11", "This is a test title2", "This is a test description", "urgent") # pylint: disable=invalid-name
    print(issue)
