from .chatgpt import ChatGPT


async def setup(bot):
    await bot.add_cog(ChatGPT(bot))