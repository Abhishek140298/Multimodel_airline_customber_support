from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import os
import base64
from io import BytesIO
from PIL import Image

load_dotenv()

clinet=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}
def get_ticket_price(destination_city):
    print(f"Tool called to get price of ticket for {destination_city}")
    city=destination_city.lower()
    return ticket_prices.get(city,"unknown")
def image_generation(city):
    image_res=client.image.generate(model="dall-e-3",
                                    promt=f"Genrate a vibrant image of the destination{city} with the iconic landmarks",
                                    size="1024x1024",
                                    n=1,
                                    response_format="b64__json")
    return image_res.data[0].b64__json

def base_64_image(b64_image):
    image_binary=base64.b64decode(b64_image)
    return Image.open(BytesIO(image_binary))
    
    

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
    image=None
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
               image=base_64_image(image_generation(city))
               
        response=cliet.chat.completion.create(model="gpt-4o-mini",messages=messages)       
        reply=response.choices[0].message.content
    
    return reply,image
#!Image generation
#gr.ChatInterface(fn=chat,type="messages").launch()

#Layout with image also
with gr.Blocks() as ui:
    with gr.Row():
        chatboat=gr.Chatbot(hieght=500,type="messages")
        image_result=gr.Image(height=500)
    with gr.Row():
        textbox=gr.Textbox(lable="Please ask your query")
    with gr.Row():
        clear=gr.Button('clear')
    
    def user_turn(message,history):
        return "" ,history + [{"role":"user","content":message}] 
    def bot_turns(history):
        user_message=history[-1].content
        reply,image=chat(user_message,history[:-1])
        history.append({"role":"assitant","content":reply})
        return history,image
    textbox.submit(user_turn,[textbox,chatboat],[textbox,chatboat]).then(bot_turns,chatboat,[chatboat,image_result])       
ui.launch()