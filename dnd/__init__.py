from .dnd import Dnd


def setup(bot):
    bot.add_cog(Dnd(bot))