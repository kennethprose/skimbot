import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
URL = os.getenv('URL')
MODEL = os.getenv('MODEL')

def summarize_conversation(sorted_messages):
    conversation = ""
    for msg in sorted_messages:
        conversation += f"{msg['author']}: {msg['message']}\n"
    
    prompt_text = f"Please summarize the following conversation. Please keep it as short as possible without missing any key arguments or details.\n\n{conversation}"
    
    payload = {
        "model": MODEL,
        "prompt": prompt_text,
        "stream": False
    }
    
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
            "author": message.author.name,
            "message": message.content,
            "timestamp": message.created_at.timestamp()
        }
        messages.append(message_details)
    sorted_messages = sorted(messages, key=lambda x: x['timestamp'], reverse=False)

    await interaction.edit_original_response(content="Summarizing...")

    summary = summarize_conversation(sorted_messages)
    await interaction.edit_original_response(content=str(summary))

client.run(TOKEN)