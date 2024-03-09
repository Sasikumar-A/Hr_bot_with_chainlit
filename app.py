from openai import AsyncOpenAI
import chainlit as cl
import os
from chainlit.types import ThreadDict


os.environ['OPENAI_API_KEY'] = 'your openai key'

client = AsyncOpenAI()

cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0
}


@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")


@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    # do some work
    await cl.sleep(2)

    msg.content = f"Processed message {message.content}"

    await msg.update()


counter = 0


@cl.on_message
async def on_message(message: cl.Message):
    global counter
    counter += 1

    await cl.Message(content=f"You sent {counter} message(s)!").send()


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def chain_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    message = [
                  {
                      "content": "You are a company HR bot, Think like a HR and replay only through like that."
                                 "Don't tell any unwanted thing in replay.",
                      "role": "system"
                  },
                  {
                      "content": message.content,
                      "role": "user"
                  }
              ]
    msg = cl.Message(content="")
    await msg.send()

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.1,
        messages=message,
        stream=True
    )
    # await cl.sleep(3)
    async for part in response:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
    # await cl.Message(content=response.choices[0].message.content).send()
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()

