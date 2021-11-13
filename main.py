import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from music_cog import music_cog
import json
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from DefaultApiKeys import BASE_URL, API_KEY, ASSISTANT_ID

def init():
    authenticator = IAMAuthenticator(API_KEY)
    assistant = AssistantV2(
        version='2021-06-14',
        authenticator=authenticator
    )

    assistant.set_service_url(BASE_URL)
    session_id = createSession(assistant, ASSISTANT_ID)

    return authenticator, assistant, session_id

def createSession(assistant, assistant_id):    
    session = assistant.create_session(assistant_id).get_result()
    session_json = json.dumps(session, indent=2)
    session_dict = json.loads(session_json)
    return session_dict['session_id']

def deleteSession(assistant, session_id, assistant_id):
    assistant.delete_session(assistant_id, session_id).get_result()

def send_message(assistant, session_id, assistant_id, message):
    response = assistant.message(
        assistant_id = assistant_id,
        session_id = session_id,
        input={
            'message_type': 'text',
            'text': message
        }
    ).get_result()
    return response['output']['generic'][0]['text'] if 'text' in response['output']['generic'][0] else ''


load_dotenv()
TOKEN = os.getenv('TOKEN')
Client = commands.Bot(command_prefix="!")
Client.add_cog(music_cog(Client))
authenticator, assistant, session_id = init()

@Client.listen('on_message')
async def msg(message):
    if message.content.startswith("!"):
        return
    if message.author == Client.user:
        return
    if message.content != 'exit':
        await message.channel.send(send_message(assistant, session_id, ASSISTANT_ID, message.content))
    if message.content == 'exit':
        deleteSession(assistant, session_id, ASSISTANT_ID)
        await message.channel.send('Shutting down..')

Client.run(TOKEN)
