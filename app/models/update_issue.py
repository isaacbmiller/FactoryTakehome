import os

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

import dotenv

dotenv.load_dotenv()

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")

transport = RequestsHTTPTransport(url="https://api.linear.app/graphql", headers={'Authorization': LINEAR_API_KEY})
client = Client(transport=transport, fetch_schema_from_transport=True)

# Set up the mutation to update an issue
mutation = gql(
"""
mutation IssueUpdate($input: IssueUpdateInput!, $issueUpdateId: String!) {
    issueUpdate(input: $input, id: $issueUpdateId) {
        issue {
            title
        }
    }
}
"""
)

def update_issue(issue_id, title, description, priority):
    '''Update an issue in Linear'''
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
                # "type": type, ## TODO: add type
            },
            "issueUpdateId": issue_id,
        },
    )
    return result

if __name__ == "__main__":
    issue = update_issue("LIN-11", "This is a test title", "This is a test description", "urgent")
    print(issue)
