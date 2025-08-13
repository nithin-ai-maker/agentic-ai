from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool, input_guardrail, GuardrailFunctionOutput
from pydantic import BaseModel
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

load_dotenv(override=True)
async def main():

    instructions1 = "You are a sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write professional, serious cold emails."

    instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write witty, engaging cold emails that are likely to get a response."

    instructions3 = "You are a busy sales agent working for ComplAI, \
    a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
    You write concise, to the point cold emails."

    sales_agent1= Agent(
        instructions=instructions1,
        name="Professional Sales Agent",
        model="gpt-4o-mini"
    )
    sales_agent2= Agent(
        instructions=instructions2,
        name="Engaging Sales Agent",
        model="gpt-4o-mini"
    )
    sales_agent3= Agent(
        instructions=instructions3,
        name="Busy Sales Agent",
        model="gpt-4o-mini"
    )
    sales_picker= Agent(
        instructions="You pick the best cold emails from the given options. Imagine you are a customer and pick one you are most likely to respond to. Do not give any explaination just reply with the selected email",
        name="Cold Email Picker- Customer",
        model="gpt-4o-mini"
    )
    class NameCheck(BaseModel):
        is_name_message:bool
        name:str
    
    name_check_agent=Agent(name='Name Check Agent',instructions="Check if the user is including any personal name in what they want to do",output_type=NameCheck)

    @input_guardrail
    async def gaurdrail_against_name(ctx,agent,message):
        result = await Runner.run(name_check_agent,message,context=ctx.context)
        is_name_in_message= result.final_output.is_name_message
        return GuardrailFunctionOutput(output_info={"found_name":result.final_output}, tripwire_triggered=is_name_in_message)

    @function_tool
    def send_email(body:str):  
        """Send out an email with the given body to all the sales prospects"""
        sg= sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email= Email('nithinscr007@gmail.com')
        to_email= To('nithinsuresh7025@gmail.com')
        content= Content("text/plain", body)
        mail= Mail(from_email, to_email, "Sales Email", content).get()
        sg.client.mail.send.post(request_body=mail)
        return {"status": "success"}
    
    description='Write a cold sales email'
    tool1= sales_agent1.as_tool(tool_name='sales_agent1',tool_description=description)
    tool2= sales_agent2.as_tool(tool_name='sales_agent2',tool_description=description)
    tool3= sales_agent3.as_tool(tool_name='sales_agent3',tool_description=description)
    tools=[tool1,tool2,tool3,send_email]

    instructions_sales_manager= "You are a sales manager working for ComplAI. You use the tools given to you to generate cold sales emails. You never generate sales emails yourself; you always use the tools. You try all 3 sales_agent tools once before choosing the best one. You pick the single best email and use the send_email tool to send the best email (adn only the best email) to the user"

    Sales_Manager= Agent(name='Sales Manager Agent',instructions=instructions_sales_manager,tools=tools,input_guardrails=[gaurdrail_against_name],model='gpt-4o-mini')
    message= "Write a cold sales email addrresses to Dear CEO from Alice"

    with trace("Sales Manager"):
        result= await Runner.run(Sales_Manager,message)

if __name__== "__main__":
    asyncio.run(main())