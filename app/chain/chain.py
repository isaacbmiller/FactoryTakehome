from operator import itemgetter

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser

import dotenv
import os

dotenv.load_dotenv()

set_llm_cache(SQLiteCache(database_path=".langchain.db"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI()

model_parse_str = model | StrOutputParser()

objective_prompt = PromptTemplate.from_template(''' 
                                            You are an engineering manager with an eye for detail and creating actionable objectives. You are helping to create parts of a ticket for a task. \
                                            Task context:
                                                Description: "{description}"
                                            ---
                                            Write a concise primary actionable objective for the task.
                                            ''')
objective_chain = objective_prompt | model_parse_str

title_prompt = PromptTemplate.from_template(''' 
                                           You are an engineering manager with an eye for detail. You are helping to create parts of a ticket for a task. \
                                           Task context:
                                                Description: "{description}"
                                                Objective: "{objective}"
                                            ---
                                            Write a concise title for the task''')
title_chain = title_prompt | model_parse_str

success_prompt = PromptTemplate.from_template(''' 
                                            You are an engineering manager with an eye for detail and creating actionable objectives. You are helping to create parts of a ticket for a task. \
                                            Task context:
                                                    Description: "{description}"
                                                    Objective: "{objective}"
                                            ---
                                            Write a fleshed out success criteria for the task. The criteria should be measurable and observable. \
                                            The criteria should be written in a way that it is clear when the task is complete. \
                                            The format should be markdown checkboxes as one would see inside of a Jira ticket.''')
success_chain = success_prompt | model_parse_str



class TicketTypeAndPriority(BaseModel):
    type: str = Field(description="one of feature, bug, improvement")
    priority: str = Field(description="one of urgent, high, medium, low")

    @validator("type")
    def ticket_is_valid_type(cls, field):
        if field not in ["feature", "bug", "improvement"]:
            raise ValueError("Invalid ticket type")
        return field
    
    @validator("priority")
    def ticket_is_valid_priority(cls, field):
        if field not in ["urgent", "high", "medium", "low"]:
            raise ValueError("Invalid ticket priority")
        return field
    
ticket_type_parser = PydanticOutputParser(pydantic_object=TicketTypeAndPriority)

ticket_type_prompt = PromptTemplate.from_template(''' \
                                            You are an engineering manager with an eye for detail. You are helping to create parts of a ticket for a task. \
                                            Task context:
                                                    Description: "{description}"
                                                    Objective: "{objective}"
                                            ---
                                            You should classify the ticket as one of the following types: \
                                                feature, bug, KTLO, system_improvement
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
                                            Given the above information, your job is to create  \
                                              
                                              
                                              ''')



# ---------------------------------------------

ticket_output_prompt = PromptTemplate.from_template(''' \
                                             You are an engineering manager with an eye for detail. \
                                             Given the following information: \
                                                Title: {title} \
                                                Description: {description} \
                                                Objective: {objective} \
                                            Create a ticket with in the following format: \
                                                Ticket: <title> \n \
                                                Description: <description> \n \
                                                Objective: <objective> \n \
                                                Type of Ticket: <feature|bug|KTLO|system_improvement> \n \
                                            ---
                                            ''')



ticket_chain = (
    RunnablePassthrough.assign(objective=objective_chain)
        | RunnablePassthrough.assign(title=title_chain)
        | ticket_output_prompt
        | model_parse_str
)

test_chain = (
    RunnablePassthrough.assign(objective=objective_chain)
        | RunnablePassthrough.assign(title=title_chain)
        | RunnablePassthrough.assign(ticket_type=ticket_type_chain)
        | RunnablePassthrough.assign(success_criteria=success_chain)
)
test_descriptions = [
    "Add Two-Factor Authentication to User Accounts",
    # "Optimize Database Query Performance on Sales Page",
    # "Update Documentation for API Endpoints"
]

for description in test_descriptions:
    result = test_chain.invoke({"description": description})
    print(result)
    
# Title: A concise and clear summary of the issue or feature request. - Done
# Description: A detailed explanation of the issue or feature, including the expected behavior and the actual behavior (for bugs). - Done
# Objective: For feature requests, a description of the desired outcome. - Done
# Type of Ticket: Categorizing the ticket (e.g., bug, feature request, improvement, task). - Done
# Success Criteria: For feature requests, a description of the desired outcome. - Done
# Priority: Indicating the urgency (e.g., critical, high, medium, low) - Done
# Expected Resolution: For feature requests, a description of the desired outcome.
# Tags/Labels: Keywords to help categorize and search for the ticket.
# Estimated Time for Completion: An estimate of how long it will take to resolve the ticket.
# Reporter: The person who reported or created the ticket - Written by AI, submitted from API user
# Current Status: The current state of the ticket - Open
# Only if integrated with API. Attachments/Screenshots: Any relevant images, logs, or files that provide additional context.