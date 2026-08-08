from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import os

load_dotenv()

clinet=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt=(
    "You are helpful customber support assitant for the airline called flight "
    "Give the short courteous answer not more than one line "
    "Always be accrate ,if you do not know the answer then say so"
)

def chat(message,history):
    # 'history' is a list of past {"role": ..., "content": ...} messages Gradio manages for us
    messages=[{"role":"system","content":system_prompt}]+history+{{"role": "user", "content": message}}
    response=cleint.chat.completion.create(model="gpt-4o-mini",message=messages)
    
    return response.choices[0].message.content

gr.ChatInterface(fn=chat,type="messages").launch()
