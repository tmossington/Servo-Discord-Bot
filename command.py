import requests
import json
import os

client_id = os.getenv('client_id')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


url = f"https://discord.com/api/v10/applications/{client_id}/commands"

headers = {
    "Authorization": "Bot f{DISCORD_TOKEN}",
}

# Define the command
#json = {
 #   "name": "price",
  #  "description": "Get the price of a stock",
   # "options": [
    #    {
     #       "name": "symbol",
      #      "description": "Stock symbol",
       #     "type": 3,
        #    "required": True
        #}
   # ]
#}

# Make the POST request
#r = requests.post(url, headers=headers, json=json)

#print(r.json())

# Delete request
response = requests.delete(url, headers=headers)
print(response.status_code)


