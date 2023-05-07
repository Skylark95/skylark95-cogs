from .wingspan import Wingspan


async def setup(bot):
    await bot.add_cog(Wingspan(bot))