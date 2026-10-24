import json
import os
import discord
import requests
from dotenv import load_dotenv
from message_utils import split_summary
from skim_utils import collect_messages, resolve_selection

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

async def skim_messages(interaction: discord.Interaction, *, count=None, after=None) -> None:
    if interaction.channel is None or not hasattr(interaction.channel, 'history'):
        await interaction.response.send_message(
            "Use this command in a channel with message history.", ephemeral=True
        )
        return
    await interaction.response.send_message("Fetching messages...")

    try:
        history = await collect_messages(
            interaction.channel, before=interaction.created_at, after=after, count=count
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content="I don't have permission to read this channel's message history."
        )
        return
    except discord.HTTPException:
        await interaction.edit_original_response(
            content="Discord couldn't return the message history. Please try again."
        )
        return

    if not history:
        await interaction.edit_original_response(content="No messages found for that selection.")
        return

    messages = []
    for message in history:
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
    await interaction.edit_original_response(content=f"Summarizing {len(messages)} messages...")

    summary = summarize_conversation(messages)
    chunks = split_summary(str(summary))
    if not chunks:
        chunks = ["Ollama returned an empty summary."]
    await interaction.edit_original_response(content=chunks[0])
    for chunk in chunks[1:]:
        await interaction.followup.send(content=chunk)

@client.tree.command(name="skim", description="Summarize messages using exactly one selection option")
@discord.app_commands.describe(
    duration="Time to look back, such as 30m, 4h, or 2d",
    count="Number of non-bot messages to summarize (at least 1)",
    since="ISO timestamp with timezone, e.g. 2026-10-24T09:00:00-04:00",
)
async def skim(
    interaction: discord.Interaction,
    duration: str | None = None,
    count: int | None = None,
    since: str | None = None,
) -> None:
    try:
        selection = resolve_selection(
            interaction.created_at, duration=duration, count=count, since=since
        )
    except ValueError as error:
        await interaction.response.send_message(str(error), ephemeral=True)
        return
    await skim_messages(interaction, **selection)

if __name__ == '__main__':
    client.run(TOKEN)
