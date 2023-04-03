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
                    message_content = f"Le téléchargement du torrent {name} est terminé à 100%."
                else:
                    message_content = (
                        f"Nom du torrent: {name}\n"
                        f"Taille du torrent: {size_bytes / (1024 * 1024):.2f} MB\n"
                        f"Taille actuelle du téléchargement: {bytes_done / (1024 * 1024):.2f} MB\n"
                        f"Vitesse de téléchargement: {down_rate / (1024 * 1024):.2f} MB/s\n"
                        f"Date d'ajout du torrent: {date_added_formatted}\n"
                        f"Pourcentage d'avancement: {percent_complete}%\n"
                        f"Temps restant estimé: {eta_minutes} minutes et {eta_seconds_rounded} secondes\n"
                        f"Chemin du torrent: {path}"
                    )

                if torrent_hash in sent_messages:
                    await sent_messages[torrent_hash].edit(content=message_content)
                else:
                    sent_message = await channel.send(message_content)
                    sent_messages[torrent_hash] = sent_message

bot.run(DISCORD_TOKEN)