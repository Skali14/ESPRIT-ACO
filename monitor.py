import requests
import json
import time
import helper
import checkout
import discord
from discord import Webhook, RequestsWebhookAdapter, Embed
from datetime import datetime

config = helper.read_config()

availability = False  
webhookurl=config['Webhook']['webhookurl']
requestURL=config['Product']['requestURL']
oosDelay=config['Cooldown']['OOS_Delay']
    
def monitor():
    while availability == False:
        r = requests.get(requestURL)
        data = json.loads(r.text)
        stock = data['product']['inventoryRecord']
        if stock > 0:
            webhook = Webhook.from_url(webhookurl, adapter=RequestsWebhookAdapter())
            embed=discord.Embed(title=f'There are {stock} items left in stock', color=0xff0000)
            webhook.send(embed=embed)
            print(datetime.now(), f"There are {stock} items left in stock!")
            checkout.addToCart()
            break
        else:
            print(datetime.now(), "OOS")
            time.sleep(int(oosDelay))
