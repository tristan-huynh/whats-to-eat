import discord, json, os, subprocess, logging #, aiohttp
from discord import app_commands
from discord.ext import commands
from urllib.request import urlopen, Request

CACHE_FILE = "src/cache/todays_menu.json"

API_URL = "https://api.dineoncampus.com/v1/sites/todays_menu?site_id=64872d0f351d53058416c3d5"
HDR = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.5',
}

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Configuration constants
    DESIRED_STATIONS = {"Homestyle", "Delicious Without", "Flame", "Taste of Home", "The Diner", "The Kitchen"}
    EXCLUDED_LOCATIONS = {"Brkfst & Co", "Tu Taco", "Par and Grill"}
    
    # Special rules for specific location/station combinations
    LOCATION_STATION_EXCLUSIONS = {
        "Food Hall at Wadsworth": {"500 Degrees"}
    }


    def _get_station_menu_items(self, station):

        if not station.get('items'):
            return "No items available"
        
        items = []
        for item in station['items']:
            if 'name' in item:
                item_name = item['name'].strip()
                if item_name:
                    items.append(item_name)
        
        return "\n".join(items) if items else "No items available"

    def _should_include_station(self, location_name, station_name):
        # Check if station is in desired stations
        if station_name not in self.DESIRED_STATIONS:
            return False
        
        # Check exclusions
        if location_name in self.LOCATION_STATION_EXCLUSIONS:
            if station_name in self.LOCATION_STATION_EXCLUSIONS[location_name]:
                return False
        
        return True

    @app_commands.command(name="menu", description="Get today's menu for a specific period")
    @app_commands.describe(period="The period you want the menu for")
    @app_commands.choices(period=[
        app_commands.Choice(name="Breakfast", value="Breakfast"),
        app_commands.Choice(name="Lunch", value="Lunch"),
        app_commands.Choice(name="Dinner", value="Dinner")
    ])
    async def menu(self, interaction: discord.Interaction, period: str):
        try:
            # Use cached data instead of fetching from API
            data_json = self.bot.cache_manager.load_cached_menu()
            
            if not data_json:
                # Fallback to direct API call if cache fails
                response = urlopen(Request(API_URL, headers=HDR))
                data_json = json.loads(response.read())
                logging.warning("Using fallback API call due to cache failure")
                
        except Exception as e:
            await interaction.response.send_message(f"Unknown error: {e}. Please try again later.", ephemeral=True)
            logging.error(f"Error fetching menu data: {e}")
            return

        embed = discord.Embed(title=f"{period} Menu", color=self.bot.embed_color)
        locations_added = 0
        for location in data_json.get('locations', []):
            location_name = location.get('name', '')
        
            if location_name in self.EXCLUDED_LOCATIONS:
                continue
            matching_period = None
            for period_data in location.get('periods', []):
                if period_data.get('name', '').lower() == period.lower():
                    matching_period = period_data
                    break
            
            if not matching_period:
                continue
            location_has_stations = False
            location_stations = []

            for station in matching_period.get('stations', []):
                station_name = station.get('name', '')
                
                if self._should_include_station(location_name, station_name):
                    station_items = self._get_station_menu_items(station)
                    location_stations.append((station_name, station_items))
                    location_has_stations = True
            # Add to embed
            if location_has_stations:
                embed.add_field(name=f"📍 {location_name}", value="", inline=False)
                
                for station_name, station_items in location_stations:
                    # Discord message limit check
                    if len(station_items) > 2000:
                        station_items = station_items[:950] + "\n... (truncated)"
                    
                    embed.add_field(name=station_name, value=station_items or "No items available", inline=True)
                
                locations_added += 1

        if locations_added == 0:
            embed.add_field(name="No Menu Available", value=f"No menu items found for {period} at the selected locations.", inline=False)

        embed.set_footer(
            text=f"{self.bot.user.name} • v{self.bot.version}",
            icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="refresh_cache", description="Manually refresh the menu cache")
    async def refresh_cache(self, interaction: discord.Interaction):
        await interaction.response.defer()  # This operation might take a few seconds trigger manual cache refresh
        
        try:
            self.bot.cache_manager.fetch_and_cache_menu()
            cache_info = self.bot.cache_manager.get_cache_info()
            
            embed = discord.Embed(
                title="✅ Cache Refreshed", 
                description=f"Menu cache updated successfully at {cache_info['last_modified'].strftime('%Y-%m-%d %H:%M:%S')}",
                color=self.bot.embed_color
            )
            embed.add_field(name="Cache Size", value=f"{cache_info['size_bytes']:,} bytes", inline=True)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(
                text=f"{self.bot.user.name} • v{self.bot.version}",
                icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Cache Refresh Failed", 
                description=f"Error: {str(e)}",
                color=self.bot.embed_color
            )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Menu(bot))