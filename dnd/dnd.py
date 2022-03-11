from redbot.core import commands
import discord

class Dnd(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spell(self, ctx: commands.Context, *, text: str):
        """This does stuff!"""
        embed = discord.Embed(color=(await ctx.embed_colour()))
        embed.add_field(name="Name", value="Acid Arrow")
        embed.add_field(name="Level", value="2")
        embed.add_field(name="Casting Time", value="1 Action")
        embed.add_field(name="Range/Area", value="90 ft")
        embed.add_field(name="Components", value="V,S,M *")
        embed.add_field(name="Duration", value="Instantaneous")
        embed.add_field(name="School", value="Evocation")
        embed.add_field(name="Attack/Save", value="Ranged")
        embed.add_field(name="Damage/Effect", value="Acid")
        embed.add_field(name="Description", value="A shimmering green arrow streaks toward a target within range and bursts in a spray of acid. Make a ranged spell attack against the target. On a hit, the target takes 4d4 acid damage immediately and 2d4 acid damage at the end of its next turn. On a miss, the arrow splashes the target with acid for half as much of the initial damage and no damage at the end of its next turn.")
        await ctx.send(embed=embed)
