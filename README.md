# SkimBot

## Overview

This bot, named SkimBot, uses any AI API (designed for and tested on [Ollama](https://ollama.com/)) to summarize recent messages in a Discord channel. It fetches a specified number of messages and sends back a summarized version of the conversation.

## Requirements

- Access to a local or cloud AI API
- Python 3.x
- [discord.py](https://discordpy.readthedocs.io/en/stable/) library
- requests library
- python-dotenv library

You can install these libraries using pip:

```bash
pip install discord.py requests python-dotenv
```

## Setup

1. **Create a Discord Bot:**

   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click new application and customize the bot with a name and profile picture.
   - On the OAuth2 tab, use the OAuth2 URL Generator to generate a server invite link with the following permissions and add the bot to your server:
     - Scopes
       - bot
       - applications.commands
     - Bot Permissions
       - Send messages
       - Read message history
   - On the Bot tab, copy the bot token.

2. **Set Up Environment Variables:**

   - Create a file called `.env`.
   - Fill in the following variables:

     ```plaintext
     TOKEN=your-discord-bot-token
     GUILD_ID=your-guild-id
     URL=http://localhost:11434/api/generate  # Replace with your AI API endpoint
     MODEL=gemma3:12b                       # Replace with your desired model
     ```

     \* You can find the Guild ID by logging into discord on the web, opening the desired server, and copying the last number in the URL.

## Usage

- Once the `.env` file is configured, run the `skimbot.py` Python file.
- In Discord, use the `/skim` slash command followed by the number of messages you want to summarize (e.g., `/skim 20`).
