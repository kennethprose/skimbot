import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
app_id = os.getenv('APPID')


url = f"https://discord.com/api/v10/applications/{app_id}/commands"

# This is an example CHAT_INPUT or Slash Command, with a type of 1
json = {
    "name": "skim",
    "type": 1,
    "description": "Summarize the last few messages in a channel",
    "options": [
        {
            "name": "msg_count",
            "description": "The number of messages to summarize",
            "type": 4,
            "required": True
        }
    ]
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": f"Bot {token}"
}

r = requests.post(url, headers=headers, json=json)

print(r.status_code)
print(r.json())