import discord
from discord.ext import commands
import psutil
import time


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.bot.version = "1.0.0"

    @discord.slash_command(description="Show the bot's status")
    async def status(self, ctx: discord.ApplicationContext):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        uptime = time.time() - self.start_time
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
        server_count = len(self.bot.guilds)

        embed = discord.Embed(title="Status", color=discord.Color.blue())
        embed.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory_info.percent}%", inline=True)
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Servers", value=server_count, inline=True)
        embed.add_field(name="Websocket Latency", value=f"0 ms", inline=True)
        embed.add_field(name="Client Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(icon_url=self.bot.user.avatar.url, text=f"{self.bot.user.name} v{self.bot.version}")

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Status(bot))
