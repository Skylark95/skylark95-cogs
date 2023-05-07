from .dnd import Dnd


async def setup(bot):
    await bot.add_cog(Dnd(bot))