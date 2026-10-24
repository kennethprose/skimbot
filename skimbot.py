import json
import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
URL = os.getenv('URL')
MODEL = os.getenv('MODEL')
PROMPT = os.getenv('PROMPT')
NUM_CTX = os.getenv('NUM_CTX', '').strip()
if NUM_CTX:
    try:
        NUM_CTX = int(NUM_CTX)
        if NUM_CTX <= 0:
            raise ValueError
    except ValueError:
        raise ValueError('NUM_CTX must be a positive integer when supplied.') from None

def summarize_conversation(sorted_messages):
    message_ids = {msg['id'] for msg in sorted_messages}
    conversation = {"order": "oldest_first", "messages": []}
    for msg in sorted_messages:
        entry = dict(msg)
        if entry['reply_to'] is not None:
            entry['reply_to_included'] = entry['reply_to'] in message_ids
        conversation['messages'].append(entry)
    
    payload = {
        "model": MODEL,
        "system": PROMPT,
        "prompt": json.dumps(conversation, ensure_ascii=False, indent=2),
        "stream": False
    }
    if NUM_CTX:
        payload["options"] = {"num_ctx": NUM_CTX}
    
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        
        summary = response.json()['response']
    except Exception as e:
        summary = f"Error contacting Ollama: {str(e)}"
    
    return summary

class SlashClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync()

client = SlashClient()

@client.tree.command(name="skim", description="Summarize the last few messages in a channel")
async def _skim(interaction: discord.Interaction, msg_count: int) -> None:
    await interaction.response.send_message("Fetching messages...")

    messages = []
    async for message in interaction.channel.history(limit=msg_count+1):
        if message.author.bot:
            continue
        message_details = {
            "id": str(message.id),
            "author": message.author.name,
            "content": message.content,
            "timestamp": message.created_at.isoformat(),
            "reply_to": None
        }
        if (
            message.type == discord.MessageType.reply
            and message.reference is not None
            and message.reference.message_id is not None
        ):
            message_details['reply_to'] = str(message.reference.message_id)
        messages.append(message_details)
    sorted_messages = sorted(messages, key=lambda x: x['timestamp'], reverse=False)

    await interaction.edit_original_response(content="Summarizing...")

    summary = summarize_conversation(sorted_messages)
    await interaction.edit_original_response(content=str(summary))

client.run(TOKEN)
