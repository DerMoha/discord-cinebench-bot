# Discord Cinebench Bot

The Discord Cinebench Bot is a Python-based Discord bot that allows users to submit and retrieve CPU benchmark scores using the Cinebench benchmark software. It stores user-submitted scores in a SQLite database and provides commands to view the top scores.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Usage](#usage)

## Features

- **User Submissions:** Users can submit their CPU benchmark scores along with optional information.
- **Top Scores:** Users can view the top CPU benchmark scores, optionally filtered by benchmark type and Cinebench version.
- **Docker:** The bot can be runs as a Docker container for easy deployment on your server.
- **Data Persistence:** User submissions are stored in a SQLite database for data persistence.

## Prerequisites

Before running the Discord Cinebench Bot, make sure you have the following prerequisites installed:

- [Python 3.11](https://www.python.org/downloads/release/python-3110/)
- [Docker](https://www.docker.com/get-started)
- Discord Bot Token (You can create a Discord bot and get a token from the [Discord Developer Portal](https://discord.com/developers/applications))

## Getting Started

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/DerMoha/discord-cinebench-bot.git
   cd discord-cinebench-bot
   ```
2. Build the docker image:
   ```bash
   docker build -t discord-cinebench-bot .
   ```
3. Edit the docker-compose.yml file and replace the two environment variables with the ones you use.
4. Run the bot using Docker Compose:
   ```bash
   docker-compose up -d
   ```

# Usage

To use the Discord Cinebench Bot, invite it to your Discord server and interact with it in the designated channel.

1. Use the `/start` command to start a new CPU benchmark entry.
2. Follow the bot's prompts to enter your CPU name, benchmark type, Cinebench score, optional comment, and Cinebench version.
3. Use the `/top` command to view the top CPU benchmark scores.
4. Profit

# Disclaimer
This project helped me in learning sqlite and docker. I don't think this is a good way to store data. I would recommend using a "real" database like postgresql or mysql.
I also don't think this is a good way to run a discord bot. 