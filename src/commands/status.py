import discord, psutil, time, dotenv, os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @discord.slash_command(description="Show the bot's status")
    async def status(self, ctx: discord.ApplicationContext):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        uptime = time.time() - self.start_time
        uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
        server_count = len(self.bot.guilds)

        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(days)}d, {int(hours)}h, {int(minutes)}m, {int(seconds)}s"

        embed = discord.Embed(title="System Status", color=self.bot.embed_color)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory_info.percent}%", inline=True)
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Servers", value=server_count, inline=True)
        embed.add_field(name="Client Latency", value=f"{round(self.bot.latency)}ms", inline=True)        
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None, 
                         text=f"{self.bot.user.name} • v{self.bot.version}")
        embed.timestamp = discord.utils.utcnow()
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Status(bot))
