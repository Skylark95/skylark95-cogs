from redbot.core import commands
from zoneinfo import ZoneInfo
from datetime import datetime

class GenCon(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gencon(self, ctx):
        tzinfo = ZoneInfo('America/New_York')
        today_date = datetime.now(tzinfo)
        gencon_date = datetime(2024, 8, 1, tzinfo=tzinfo)
        delta = gencon_date - today_date
        days = delta.days + 1
        if days > 1:
            await ctx.send(f'Countdown to Gen Con: {days} days')
        elif days == 1:
            await ctx.send(f'Countdown to Gen Con: {days} day')
        else:
            await ctx.send(f'Countdown to Gen Con: 0 days')
