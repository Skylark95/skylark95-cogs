from .boardgamegeek import BoardGameGeek


async def setup(bot):
    await bot.add_cog(BoardGameGeek(bot))
