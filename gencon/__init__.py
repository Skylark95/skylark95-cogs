from .gencon import GenCon


async def setup(bot):
    await bot.add_cog(GenCon(bot))
