from pytz import timezone
from redbot.core import commands
from datetime import datetime, timezone

class Wingspan(commands.Cog):
    """Wingspan game related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def expansion(self, ctx: commands.Context):
        """Time until Wingspan European expansion is released"""
        date_today = datetime.now(timezone.utc)
        date_release = datetime(2022, 5, 2, 0, 0, 0, 0, timezone.utc)
        time_until = date_release - date_today
        return await ctx.send(f'Wingspan: European Expansion will be released in **{time_until.days} days**')
