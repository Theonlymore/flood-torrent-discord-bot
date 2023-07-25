import os
import discord
from datetime import datetime
from discord import Intents
from discord.ext import commands, tasks
import requests

# Utiliser les variables d'environnement définies dans le Dockerfile
base_url = os.environ['BASE_URL']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
UPDATE_INTERVAL = int(os.environ['UPDATE_INTERVAL'])

# Créer une session requests
session = requests.Session()

# Créer les intents pour le bot
intents = Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

sent_messages = {}
bot_start_time = datetime.now()
completed_torrents = set()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_torrent_status.start()

@tasks.loop(seconds=UPDATE_INTERVAL)
async def check_torrent_status():
    print("Checking torrent status...")
    channel = bot.get_channel(CHANNEL_ID)

    # Authentification
    data = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = session.post(f"{base_url}/api/auth/authenticate", json=data, headers=headers)

    if response.status_code == 200:
        print("Authentication successful.")
        # Récupérer la liste des torrents
        response = session.get(f"{base_url}/api/torrents")

        if response.status_code == 200:
            print("Torrent list retrieved.")
            torrents_list = response.json()["torrents"]
            downloading_torrents = {key: value for key, value in torrents_list.items() if (value["downRate"] > 0 or value["percentComplete"] == 100) and datetime.fromtimestamp(value["dateAdded"]) > bot_start_time}

            for torrent_hash, torrent in downloading_torrents.items():
                if torrent_hash in completed_torrents:
                    continue

                name = torrent["name"]
                size_bytes = torrent["sizeBytes"]
                bytes_done = torrent["bytesDone"]
                down_rate = torrent["downRate"]
                date_added = torrent["dateAdded"]
                percent_complete = torrent["percentComplete"]
                eta = torrent["eta"]
                path = torrent["directory"]

                date_added_formatted = datetime.fromtimestamp(date_added).strftime('%d/%m/%Y-%H:%M:%S')
                eta_minutes, eta_seconds = divmod(eta, 60)
                eta_seconds_rounded = round(eta_seconds)

                if percent_complete == 100:
                    completed_torrents.add(torrent_hash)
                    total_download_time = datetime.now() - datetime.fromtimestamp(date_added)
                    total_download_time_seconds = total_download_time.total_seconds()
                    total_download_time_minutes, total_download_time_seconds = divmod(total_download_time_seconds, 60)
                    total_download_time_seconds_rounded = round(total_download_time_seconds)
                    message_content = (
                        f"Torrent download {name} 100% complete.\n"
                        f"Size: {size_bytes / (1024 * 1024):.2f} MB\n"
                        f"Total download time: {total_download_time_minutes} min and {total_download_time_seconds_rounded} secs\n"
                        f"Path: {path}\n"
                    )
                    print(f"Torrent download {name} 100% complete.")
                else:
                    message_content = (
                        f"Name: {name}\n"
                        f"Percent complete: {percent_complete}%\n"
                        f"Size: {bytes_done / (1024 * 1024):.2f} / {size_bytes / (1024 * 1024):.2f} MB\n"
                        f"Download speed: {down_rate / (1024 * 1024):.2f} MB/s\n"
                        f"Added: {date_added_formatted}\n"
                        f"ETA: {eta_minutes} min and {eta_seconds_rounded} secs\n"
                        f"Path: {path}"
                    )

                if torrent_hash in sent_messages:
                    print(message_content)
                    await sent_messages[torrent_hash].edit(content=message_content)
                else:
                    sent_message = await channel.send(message_content)
                    sent_messages[torrent_hash] = sent_message

bot.run(DISCORD_TOKEN)