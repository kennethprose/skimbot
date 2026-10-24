# SkimBot

## Overview

This bot, named SkimBot, uses [Ollama](https://ollama.com/) to summarize messages in a Discord channel. Select a message count, a recent duration, or a specific start time.

## Commands

| Option | Example | Selection |
| --- | --- | --- |
| `count` | `/skim count:20` | The last 20 non-bot messages |
| `duration` | `/skim duration:4h` | All non-bot messages from the last four hours |
| `since` | `/skim since:2026-10-24T09:00:00-04:00` | All non-bot messages after a specific time |

`duration` accepts a positive whole number followed by `m` (minutes), `h` (hours), or `d` (24-hour days), such as `30m`, `4h`, or `2d`. Units are case-insensitive.

`since` accepts an ISO 8601 timestamp with an explicit timezone: use `Z` for UTC (for example, `2026-10-24T13:00:00Z`) or an offset such as `-04:00`. Timestamps without a timezone, invalid dates, and start times at or after the command invocation are rejected.

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
 - `PROMPT`: Instructions for how the LLM should summarize the conversation, sent in Ollama's `system` field. The conversation itself is sent separately in `prompt`.

 \* You can find the Guild ID by logging into discord on the web, opening the desired server, and copying the last number in the URL.

Optional environment variables:

 - `NUM_CTX`: A positive integer specifying the Ollama context window size in tokens (for example, `32768`). When unset or empty, the bot omits `options.num_ctx` from the request and uses Ollama's default. Invalid values cause a startup error.

For native setup, add `NUM_CTX=32768` to `.env`. For Docker, add `--env NUM_CTX=32768` to the run command or `- NUM_CTX=32768` to the Compose environment list.

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
  --env PROMPT="Please summarize the following conversation. Please keep it as short as possible without missing any key arguments or details." \
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
            - PROMPT="Please summarize the following conversation. Please keep it as short as possible without missing any key arguments or details."
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
      PROMPT=Please summarize the following conversation. Please keep it as short as possible without missing any key arguments or details. 
      ```

4. Run the bot
    - Once the `.env` file is configured, run the `skimbot.py` Python file.
    - In Discord, use `/skim` with exactly one of `count`, `duration`, or `since` as shown above.

## Tests

Run the time parsing and message selection tests without Discord or Ollama access:

```bash
python -m unittest discover -s tests -v
```
