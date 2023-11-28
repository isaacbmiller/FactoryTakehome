# Linear Webhook Ticket Bot

TODO: Add description, details, and demo video

This is a bot that uses the Linear API to automatically add relevant information to a ticket when it is created.

It uses LangChain to work with the OpenAI API to generate the following fields for the ticket:

1. Title
2. Objective
3. Subtasks
4. Success Criteria
5. Priority

## How it works

The bot is built using Flask, GraphQL, and LangChain.

When the Linear webhook is triggered, it sends a POST request to the `/linear-consumer` endpoint. This request contains the Title, Description, Identifier, and other information about the ticket.

These are extracted and then passed into the LangChain pipeline.

The LangChain pipeline is a series of prompts that are chained together to generate the ticket fields.

The resulting fields are then sent to the Linear API using a GraphQL mutation to update the ticket.

### LangChain

It uses different prompts for each field, and then uses the output from the previous prompt to generate the next field.

For example, the prompt for the objective is:

```python
"""
You are an engineering manager with an eye for detail and creating actionable objectives.
You are helping to create parts of a ticket for a task.
Task context:
    Description: "{description}"
---
Write a concise primary actionable objective for the task.
"""
```

These are chained together using LCEL (LangChain Expression Language), to easily pipe the output from one prompt to the next, gradually building up the ticket.
See ./app/chain/chain.py for the full code.

### GraphQL

The GraphQL schema is not actually used. Because I am only using a singular mutation, I have hard coded the mutation into the code. If I were to add more functionality, I would use the schema to generate the mutations.

The code then looks like this:

```python
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
# ...
result = client.execute(
        mutation,
        variable_values={
            "input": {
                "title": title,
                "description": description,
                "priority": priority,
            },
            "issueUpdateId": issue_id,
        },
    )
```

You can see the entire file inside of app/models/update_issue.py

### Error handling

For the fields that specifically have to be certain strings, being the priority and the type, I use a pydantic model to validate the input. If the input is not valid, it will raise an error, and the ticket will not be updated. Langchain will retry the prompt, and if it fails again, it will raise an error and the ticket will not be updated.

## Setup/Installation

### Set up proxy for local development

You need to set up any sort of proxy to forward traffic from your local machine to the internet.

I chose to use ngrok because it is free and easy, but you can use any other proxy service, as long as it forwards traffic to your local port 3000.

You can make an ngrok account [here](https://dashboard.ngrok.com/signup).

You need to get the auth token and the static domain(free) for your account.

```bash
brew install ngrok

ngrok config add-authtoken <token>

ngrok http --domain=<your domain here> 3000
```

### Linear setup

Follow the guide [here](https://developers.linear.app/docs/graphql/webhooks) to add a webhook to your linear workspace. I used the Issue data changed event, and the link should be the ngrok url with the `/linear-consumer` endpoint.

You will also need to add a personal access token to your linear account. You can do this by going to your account settings, and clicking on the API tab. Then click on the "Create new token" button. You will need to copy this token and add it to the `.env` file in the root directory of this project under the `LINEAR_API_KEY` variable.

### Run the local server

In a separate terminal, start the flask server in debug mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run the flask server
python run.py
```

## TODO

- [x] Finish developing the chain according to the linear fields
- [x] Convert the chain into GraphQL schema to use with linear api
- [ ] Clean up code
- [ ] Add error handling with LangChain
- [ ] Add tests
  - [ ] Test endpoints
  - [ ] Evaluate prompts using langsmith(still on waitlist :/)
- [ ] Figure out how to share without deploying
- [ ] Dockerize and deploy to AWS
