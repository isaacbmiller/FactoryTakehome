import os
import dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field, validator

dotenv.load_dotenv()

# Constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_PATH = ".langchain.db"

# Initialize cache and model
set_llm_cache(SQLiteCache(database_path=DATABASE_PATH))
model = ChatOpenAI()
model_parse_str = model | StrOutputParser()

objective_prompt = PromptTemplate.from_template(
'''
You are an engineering manager with an eye for detail and creating actionable objectives.
You are helping to create parts of a ticket for a task.
Task context:
    Description: "{description}"
---
Write a concise primary actionable objective for the task.
''')
objective_chain = objective_prompt | model_parse_str

title_prompt = PromptTemplate.from_template(
'''
You are an engineering manager with an eye for detail. You are helping to create parts of a ticket for a task.
Task context:
    Description: "{description}"
    Objective: "{objective}"
---
Write a concise title for the task.
''')
title_chain = title_prompt | model_parse_str

success_prompt = PromptTemplate.from_template(
'''
You are an engineering manager with an eye for detail and creating actionable objectives. You are helping to create parts of a ticket for a task.
Task context:
        Description: "{description}"
        Objective: "{objective}"
---
Write a fleshed out success criteria for the task. The criteria should be measurable and observable.
The criteria should be written in a way that it is clear when the task is complete.
The format should be markdown checkboxes as one would see inside of a Jira ticket.
''')
success_chain = success_prompt | model_parse_str


class TicketTypeAndPriority(BaseModel):
    '''A pydantic model for ticket type and priority'''

    type: str = Field(description="one of feature, bug, improvement")
    priority: str = Field(description="one of urgent, high, medium, low")

    @validator("type")
    def ticket_is_valid_type(cls, field): # pylint: disable=no-self-argument
        '''Validate that the ticket type is one of feature, bug, improvement'''
        if field not in ["feature", "bug", "improvement"]:
            raise ValueError("Invalid ticket type")
        return field

    @validator("priority")
    def ticket_is_valid_priority(cls, field): # pylint: disable=no-self-argument
        '''Validate that the ticket priority is one of urgent, high, medium, low'''
        if field not in ["urgent", "high", "medium", "low"]:
            raise ValueError("Invalid ticket priority")
        return field


ticket_type_parser = PydanticOutputParser(
    pydantic_object=TicketTypeAndPriority)

ticket_type_prompt = PromptTemplate.from_template(''' \
You are an engineering manager with an eye for detail. You are helping to create parts of a ticket for a task. \
Task context:
        Description: "{description}"
        Objective: "{objective}"
---
You should classify the ticket as one of the following types: \
    feature, bug, improvement
{format_instructions}''',
        partial_variables={"format_instructions": ticket_type_parser.get_format_instructions()})

ticket_type_chain = ticket_type_prompt | model | ticket_type_parser

subtask_prompt = PromptTemplate.from_template('''
You are an engineering manager with an eye for detail. You are helping to create parts of a ticket for a task. \
Task context:
    Description: "{description}"
    Objective: "{objective}"
    Success Criteria: "{success_criteria}"
---
Given the above information, your job is to create actionable substeps. \
Each of these substeps should be a task that can be completed by a single person. \
The scope of each substep should be small enough that it can be completed in a single day. \
The format should be a list markdown checkboxes of actionable task descriptions.
''')
subtask_chain = subtask_prompt | model_parse_str

COMPILED_DESCRIPTION = (
    "Description:\n{description}\n\nObjective:\n{objective}\n\nSubtasks:\n{subtasks}\n\nSuccess Criteria:\n{success_criteria}"
)

# Main function to generate ticket details
def generate_ticket_details(description):
    '''Generate ticket details from a description'''
    try:
        ticket_detail_chain = (
            RunnablePassthrough.assign(objective=objective_chain)
            | RunnablePassthrough.assign(title=title_chain)
            | RunnablePassthrough.assign(ticket_type=ticket_type_chain)
            | RunnablePassthrough.assign(success_criteria=success_chain)
            | RunnablePassthrough.assign(subtasks=subtask_chain)
        )
        result = ticket_detail_chain.invoke({"description": description})
        compiled_description = (
            "Description:\n{description}\n\nObjective:\n{objective}\n\nSubtasks:\n{subtasks}\n\nSuccess Criteria:\n{success_criteria}"
        )
        result["compiled_description"] = compiled_description.format(**result)
        return result
    except Exception as e:
        # Handle or log the exception as needed
        raise e

if __name__ == "__main__":
    test_descriptions = [
        # "Add Two-Factor Authentication to User Accounts",
        # "Optimize Database Query Performance on Sales Page",
        "Update Documentation for API Endpoints"
    ]
    for description in test_descriptions:
        ticket_details = generate_ticket_details(description)
        print(ticket_details)
