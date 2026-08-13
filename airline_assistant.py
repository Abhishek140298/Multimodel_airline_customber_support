from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import os

load_dotenv()

clinet=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}
def get_ticket_price(destination_city):
    print(f"Tool called to get price of ticket for {destination_city}")
    city=destination_city.lower()
    return ticket_prices.get(city,"unknown")

system_prompt=(
    "You are helpful customber support assitant for the airline called flight "
    "Give the short courteous answer not more than one line "
    "Always be accrate ,if you do not know the answer then say so"
)


price_function={
    "name":"get_ticket_price",
    "description":"Get the price of the ticket to the destination city,call this whenever customer asks for the price",
    "parameters":{
        "type":"object",
        "properties":{
            "destination_city":{"type":"string",
                                "description":"The city customber wants to travel"}
        },
        "reqired":["destination_city"]
    }
    
}


tools=[{"type":"function","function":price_function}]

def chat(message,history):
    # 'history' is a list of past {"role": ..., "content": ...} messages Gradio manages for us
    messages=[{"role":"system","content":system_prompt}]+history+{{"role": "user", "content": message}}
    response=cleint.chat.completion.create(model="gpt-4o-mini",message=messages,tools=tools)
    
    return response.choices[0].message.content

gr.ChatInterface(fn=chat,type="messages").launch()
