from urllib.request import urlopen, Request
import json
import discord
from discord.ext import commands
from discord import Option

API_URL = "https://api.dineoncampus.com/v1/sites/todays_menu?site_id=64872d0f351d53058416c3d5"
HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

response = urlopen(Request(API_URL, headers=HDR))
data_json = json.loads(response.read())
#print(data_json)
location = data_json['locations'][0]['name']
meal_periods = data_json['locations'][0]['periods'][0]['name']
items = data_json['locations'][0]['periods'][0]['stations'][0]['items']
#for item in items:
#    print(f"  - Name: {item['name']}, Calories: {item['calories']}, Portion: {item['portion']}")

desired_stations = {"Homestyle", "500 Degrees", "Flame", "Delicious Without"}

# Iterate over the locations, periods, and stations to find the desired stations
for location in data_json['locations']:
    print(f"Location Name: {location['name']}")
    for period in location['periods']:
        print(f"  Period Name: {period['name']}")
        for station in period['stations']:
            if station['name'] in desired_stations:
                print(f"    Station Name: {station['name']}")
                for item in station['items']:
                    print(f"      Item Name: {item['name']}")
                    print(f"        Calories: {item['calories']}")
                    print(f"        Portion: {item['portion']}")


bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(name="menu", description="Get today's menu for a specific period")
async def menu(ctx: discord.ApplicationContext, period: Option(str, "Choose a period", choices=["Breakfast", "Lunch", "Dinner"])):
    API_URL = "https://api.dineoncampus.com/v1/sites/todays_menu?site_id=64872d0f351d53058416c3d5"
    HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    response = urlopen(Request(API_URL, headers=HDR))
    data_json = json.loads(response.read())

    embed = discord.Embed(title="Today's Menu", description=f"Menu for {period}", color=discord.Color.blue())
    desired_stations = {"Homestyle", "500 Degrees", "Flame", "Delicious Without"}

    for location in data_json['locations']:
        embed.add_field(name="Location", value=location['name'], inline=False)
        for period_data in location['periods']:
            if period_data['name'].lower() == period.lower():
                embed.add_field(name="Period", value=period_data['name'], inline=False)
                for station in period_data['stations']:
                    if station['name'] in desired_stations:
                        station_info = f"**Station Name:** {station['name']}\n"
                        for item in station['items']:
                            station_info += f"**Item Name:** {item['name']}\n"
                            station_info += f"Calories: {item['calories']}\n"
                            station_info += f"Portion: {item['portion']}\n\n"
                        embed.add_field(name=station['name'], value=station_info, inline=False)

    await ctx.respond(embed=embed)

bot.run('YOUR_BOT_TOKEN')


