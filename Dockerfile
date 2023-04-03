
# Utiliser l'image officielle Python comme base
FROM python:3.9-slim

# Créer un répertoire de travail
WORKDIR /app

# Installer les dépendances directement
RUN pip install --no-cache-dir discord.py requests

# Copier le reste des fichiers dans le répertoire de travail
COPY . .

# Définir les variables d'environnement (vous pouvez les remplacer par vos propres valeurs)
ENV BASE_URL=https://flood.example.net
ENV USERNAME=user
ENV PASSWORD=pass
ENV DISCORD_TOKEN=your_discord_token
ENV CHANNEL_ID=123456789
ENV UPDATE_INTERVAL=20

# Exécuter le script Python lors du lancement de l'image
CMD ["python","-u", "floodDiscordBot.py"]