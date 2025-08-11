from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os

load_dotenv(override=True)
class Me:
    def __init__(self):
        self.openai= OpenAI()
        self.name='Nithin Suresh'
        reader = PdfReader("me_agent/me/resume.pdf")
        self.resume=''
        for page in reader.pages:
            text= page.extract_text()
            if text:
                self.resume+=text
        with open("me_agent/me/summarize.txt","r",encoding="utf-8") as f:
            self.summary=f.read()

    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
            particularly questions related to {self.name}'s career, background, skills and experience. \
            Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
            You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
            Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
             "
        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt    

    def chat(self,message,history):
        messages=[{"role":"system", "content":self.system_prompt()}]+ history + [{"role":"user", "content":message}]
        response=  self.openai.chat.completions.create(model='gpt-4o-mini', messages=messages)
        return response.choices[0].message.content






if __name__== "__main__":
    me=Me()
    gr.ChatInterface(me.chat, type='messages').launch()