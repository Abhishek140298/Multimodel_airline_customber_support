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
    messages=[{"role":"system","content":system_prompt}]+history+[{{"role": "user", "content": message}}]
    response=cleint.chat.completion.create(model="gpt-4o-mini",messages=messages,tools=tools)
    if response.choices[0].finish_reason=="tool_calls":
        tool_call_message=response.choices[0].message
        messages.append(tool_call_message)  # record that the model asked for a tool call
        for tool_call in tool_call_message.tool_calls:
            if tool_call.function.name=="get_ticket_price":
               args=json.loads( tool_call.function.arguments)
               city=args.get("destination_city")
               price=get_ticket_price(city)
               messages.append({"role":"tool", "content": json.dumps({"destination_city": city, "price": price}),
                    "tool_call_id": tool_call.id})
        response=cliet.chat.completion.create(model="gpt-4o-mini",messages=messages)       

    
    return response.choices[0].message.content
#!Image generation
gr.ChatInterface(fn=chat,type="messages").launch()
