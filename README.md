# SkimBot

## Overview

This bot, named SkimBot, uses [Ollama](https://ollama.com/) to summarize recent messages in a Discord channel. It fetches a specified number of messages and sends back a summarized version of the conversation.

## Bot Setup

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

## Enviorment Variables

The following environment variables are required for this bot to function properly:
 
 - `TOKEN`: The Discord API token.
 - `GUILD_ID`: The ID of the
 - `URL`: The URL of the Ollama instance.
 - `MODEL`: The model to use for summarization.

 \* You can find the Guild ID by logging into discord on the web, opening the desired server, and copying the last number in the URL.

## Docker Setup

A dockerized version of this app is available on [Docker Hub](https://hub.docker.com/r/roseatoni/skimbot).

All you need to do for the dockerized version is provide your enviornment variables when running the docker container.

### Docker Run Command

```bash
docker run -d \
  --env TOKEN=your_token \
  --env GUILD_ID=your-guild-id \
  --env URL=http://your-ai-api-endpoint \
  --env MODEL=your-model \
  roseatoni/skimbot:latest
```

### Docker Compose File

```yml
services:
    skimbot:
        environment:
            - TOKEN=your-token
            - GUILD_ID=your-guild-id
            - URL=http://your-ai-api-endpoint
            - MODEL=your-model
        image: roseatoni/skimbot:latest
```

## Native Setup

1. Install Requirements
    - Python 3.x
    - [discord.py](https://discordpy.readthedocs.io/en/stable/) library
    - requests library
    - python-dotenv library

    You can install these libraries using pip:

    ```bash
    pip install discord.py requests python-dotenv
    ```
2. Download this repo

3. Set Up Environment Variables
    - Create a file called `.env`.
    - Fill in the enviorment variables:

      ```plaintext
      TOKEN=your-discord-bot-token
      GUILD_ID=your-guild-id
      URL=http://localhost:11434/api/generate  # Replace with your Ollama endpoint
      MODEL=gemma3:12b                         # Replace with your chosen model
      ```

4. Run the bot
    - Once the `.env` file is configured, run the `skimbot.py` Python file.
    - In Discord, use the `/skim` slash command followed by the number of messages you want to summarize (e.g., `/skim 20`).