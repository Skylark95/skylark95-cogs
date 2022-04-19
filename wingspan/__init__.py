from .wingspan import Wingspan


def setup(bot):
    bot.add_cog(Wingspan(bot))