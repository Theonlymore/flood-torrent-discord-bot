# Flood Bot for Discord

This project contains a Discord bot that fetches torrent information from a running Flood instance and displays it in a Discord channel.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/) (optional)
- A Discord account with a created bot and access token
- A running Flood instance with access credentials

## Quick Start with Docker Run

If you prefer to use `docker run`, you can pull the image from [Docker Hub](https://hub.docker.com/r/onlymore/flood-torrent-discord-bot) (`flood-torrent-discord-bot`) and run the following command:

   ```
   docker run -e BASE_URL=<your_base_url> -e USERNAME=<your_username> -e PASSWORD=<your_password> -e DISCORD_TOKEN=<your_discord_token> -e CHANNEL_ID=<your_channel_id> -e UPDATE_INTERVAL=<update_interval> onlymore/flood-torrent-discord-bot
   ```

The Discord bot will begin displaying torrent information in the specified Discord channel.

## In discord 

- ![image exemple](pics/discordInterface.png)

## Installation and Configuration with Docker Compose

1. Clone this repository or download the following files into a new directory:
   - The Python script containing the bot code
   - The Dockerfile
   - The docker-compose.yml file

2. Modify the `docker-compose.yml` file to replace the default environment variable values with your own information:

   - `BASE_URL`: the base URL of your Flood instance
   - `USERNAME`: your Flood username
   - `PASSWORD`: your Flood password
   - `DISCORD_TOKEN`: the access token of your Discord bot
   - `CHANNEL_ID`: the ID of the Discord channel where you want to display torrent information
   - `UPDATE_INTERVAL`: the time between torrent information updates, in seconds

3. Open a terminal in the directory where the files are located and run the following command to build and launch the service using Docker Compose:

   ```
   docker-compose up -d
   ```

4. The Discord bot will begin displaying torrent information in the specified Discord channel.

## Update and Maintenance

To stop the service, run the following command in the same directory as the `docker-compose.yml` file:

```
docker-compose down
```

If you want to update the bot code, make the necessary changes to the Python file, then rebuild and relaunch the service using the command `docker-compose up -d --build`.
