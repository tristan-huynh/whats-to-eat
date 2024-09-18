import discord, json, aiohttp, os, dotenv
from discord.ext import commands
from discord import Option
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv

API_URL = "https://api.dineoncampus.com/v1/sites/todays_menu?site_id=64872d0f351d53058416c3d5"
HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.version = os.getenv("version")

    @discord.slash_command(name="menu", description="Get today's menu for a specific period")
    @discord.option("period", description="The period you want the menu for", choices=["Breakfast", "Lunch", "Dinner"])
    async def menu(self, ctx: discord.ApplicationContext, period: str):
        response = urlopen(Request(API_URL, headers=HDR))
        data_json = json.loads(response.read())

        desired_stations = {"Homestyle", "500 Degrees", "Flame", "Delicious Without", "The Kitchen"}
        excluded_locations = {"Brkfst & Co", "Tu Taco"}

        embed = discord.Embed(title=f"{period}", color=discord.Color.blue())
        # forfiet wads one, include mcnair 500 degrees
        for location in data_json['locations']:
            if location['name'] not in excluded_locations:
                embed.add_field(name="Location", value=location['name'], inline=False)
                for period_data in location['periods']:
                    if period_data['name'].lower() == period.lower():
                        for station in period_data['stations']:
                            if station['name'] in desired_stations:
                                # Exclude "500 Degrees" from appearing under Wadsworth
                                if location['name'] == "Food Hall at Wadsworth" and station['name'] == "500 Degrees":
                                    continue
                                station_info = ""
                                for item in station['items']:
                                    station_info += f"{item['name']}\n"
                                embed.add_field(name=station['name'], value=station_info, inline=True)

        embed.set_footer(
            text=f"{self.bot.user.name} • v{self.bot.version}",
            icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None
        )
        await ctx.respond(embed=embed)



def setup(bot):
    bot.add_cog(Menu(bot))