from redbot.core import commands
import discord
import aiohttp
import asyncio

BASE_URL = 'https://www.dnd5eapi.co/api'
HEADERS = {'Accept': 'application/json'}
class Dnd(commands.Cog):
    """Interact with dnd5eapi.co"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spell(self, ctx: commands.Context, *, spell: str):
        """Get info about a spell"""
        index = spell.lower().replace(' ', '-')
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/spells/{index}', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    name = json.get('name')
                    desc = '\n\n'.join(json.get('desc', []))

                    higher_level = json.get('higher_level', [])
                    if len(higher_level) > 0:
                        desc = desc + '\n\n**At Higher Levels.** ' + '\n\n'.join(higher_level)

                    material = json.get('material')
                    if material != None:
                        desc = desc + '\n\n**Material.** ' + material

                    classes = ', '.join(list(map(lambda c: c.get('index'), json.get('classes', []))))

                    embed = discord.Embed(title=f'Spell: {name}', description=desc, color=(await ctx.embed_colour()))
                    embed.add_field(name="Level", value=json.get('level'))
                    embed.add_field(name="Casting Time", value=json.get('casting_time'))
                    embed.add_field(name="Range/Area", value=json.get('range'))
                    embed.add_field(name="Components", value=','.join(json.get('components', [])))
                    embed.add_field(name="Duration", value=json.get('duration'))
                    embed.add_field(name="School", value=json.get('school', {}).get('name'))
                    embed.add_field(name="Attack/Save", value=json.get('attack_type'))
                    embed.add_field(name="Damage/Effect", value=json.get('damage', {}).get('damage_type', {}).get('name'))
                    embed.add_field(name="Classes", value=classes)
                    return await ctx.send(embed=embed)
                elif resp.status == 404:
                    return await ctx.send(f'Could not find spell {spell}')
                else:
                    return await ctx.send('Oops! Something went wrong finding spells.')
        except aiohttp.ClientConnectionError:
            return await ctx.send('Oops! Something went wrong finding spells.')

