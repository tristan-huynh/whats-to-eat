import discord, os, time, logging, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from os import listdir
from src.cache.cache_manager import MenuCacheManager

load_dotenv()

TOKEN: str = os.getenv("token")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Initialize cache manager
cache_manager = MenuCacheManager()

bot.start_time = time.time()
bot.version = os.getenv("version")
bot.embed_color = 0xfca41c
bot.cache_manager = cache_manager  # Make cache manager available to commands

class ColoredFormatter(logging.Formatter):
    # Define color codes for each level
    LEVEL_COLORS = {
        'DEBUG': '\033[32m',    # White
        'INFO': '\033[34m',     # Blue
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        if levelname in self.LEVEL_COLORS:
            record.levelname = f"{self.LEVEL_COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s %(levelname)s       %(message)s', datefmt="%Y-%m-%d %H:%M:%S"))
    
logging.basicConfig(level=logging.INFO, handlers=[handler])

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="/menu"))
    
    # Start the cache scheduler
    cache_manager.start_scheduler()
    logging.info("Menu cache system initialized")
    
    # Sync command tree for discord.py
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

async def load_extensions():
    for filename in os.listdir('./src/commands/'):
        if filename.endswith('.py'):
            await bot.load_extension(f'src.commands.{filename[:-3]}')
            logging.info(f'Loaded {filename[:-3]}')



async def main():
    try:
        await load_extensions()
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested")
    finally:
        # Clean shutdown of cache manager
        if 'cache_manager' in globals():
            cache_manager.stop_scheduler()
        await bot.close()

asyncio.run(main())
