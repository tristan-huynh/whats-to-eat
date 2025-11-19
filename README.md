# whats-to-eat

A Discord bot that provides real-time dining hall menu information for Michigan Tech students. Get instant access to breakfast, lunch, and dinner menus from campus dining locations.

## Description

This Discord bot fetches and displays the daily menu from Michigan Tech's dining services through the DineOnCampus API. It features an intelligent caching system that updates menus automatically throughout the day, providing fast responses without overloading the API. The bot uses Discord's slash command interface for easy interaction.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Docker (optional, for containerized deployment)

### Dependencies

The bot requires the following Python packages (see `requirements.txt`):

### Installing

1. **Clone the repository**
   ```bash
   git clone https://github.com/tristan-huynh/whats-to-eat.git
   cd whats-to-eat
   ```

2. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   token=YOUR_DISCORD_BOT_TOKEN
   version=1.0.0
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Bot

#### Option 1: Run Locally

```bash
python main.py
```

#### Option 2: Run with Docker

Build and run using Docker Compose:
```bash
docker-compose up -d
```

Or build and run manually:
```bash
docker build -t whatstoeat:latest .
docker run -d --name whatstoeat-bot whatstoeat:latest
```

#### Option 3: VS Code Tasks

The project includes VS Code tasks for Docker:
- `docker-build`: Build the Docker image
- `docker-run: debug`: Build and run in debug mode

## Usage

Once the bot is running and invited to your Discord server, use these commands:

### `/menu [period]`
Get the menu for a specific meal period.
- **Options**: Breakfast, Lunch, or Dinner
- **Example**: `/menu Lunch`

### `/status`
Display bot status information including:
- CPU and memory usage
- Uptime
- Server count
- Latency

## Authors

Tristan Huynh - [@tristan-huynh](https://github.com/tristan-huynh)

## Version History


## License

This project is licensed under GNU GPLv3 - see the LICENSE.md file for details

## Acknowledgments