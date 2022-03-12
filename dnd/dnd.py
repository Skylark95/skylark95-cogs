from redbot.core import commands
import discord
import aiohttp

BASE_URL = 'https://www.dnd5eapi.co/api'
HEADERS = {'Accept': 'application/json'}

class Dnd(commands.Cog):
    """Interact with dnd5eapi.co"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['magics'])
    async def schools(self, ctx: commands.Context):
        """List magic schools"""
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/magic-schools', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    desc = ', '.join(list(map(lambda c: c.get('name'), json.get('results', []))))

                    embed = discord.Embed(title=f'Conditions', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                else:
                    return await ctx.send('Oops! Something went wrong listing magic schools.')
        except aiohttp.aiohttp.ClientConnectionError: 
            return await ctx.send('Oops! Something went wrong listing magic schools.')

    @commands.command(aliases=['magic'])
    async def school(self, ctx: commands.Context, *, school: str):
        """Get info about a magic school"""
        index = school.lower()
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/magic-schools/{index}', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    name = json.get('name')
                    desc = json.get('desc')

                    embed = discord.Embed(title=f'Magic School: {name}', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                elif resp.status == 404:
                    return await ctx.send(f'Could not find magic school {school}')
                else:
                    return await ctx.send('Oops! Something went wrong finding magic schools.')
        except aiohttp.aiohttp.ClientConnectionError: 
            return await ctx.send('Oops! Something went wrong finding magic schools.')

    @commands.command()
    async def conditions(self, ctx: commands.Context):
        """List conditions"""
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/conditions', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    desc = ', '.join(list(map(lambda c: c.get('name'), json.get('results', []))))

                    embed = discord.Embed(title=f'Conditions', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                else:
                    return await ctx.send('Oops! Something went wrong listing conditions.')
        except aiohttp.aiohttp.ClientConnectionError: 
            return await ctx.send('Oops! Something went wrong listing conditions.')

    @commands.command()
    async def condition(self, ctx: commands.Context, *, condition: str):
        """Get info about a condition"""
        index = condition.lower()
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/conditions/{index}', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    name = json.get('name')
                    desc = '\n\n'.join(json.get('desc', []))

                    embed = discord.Embed(title=f'Condition: {name}', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                elif resp.status == 404:
                    return await ctx.send(f'Could not find condition {condition}')
                else:
                    return await ctx.send('Oops! Something went wrong finding conditions.')
        except aiohttp.aiohttp.ClientConnectionError: 
            return await ctx.send('Oops! Something went wrong finding conditions.')

    @commands.command()
    async def spells(self, ctx: commands.Context, *, level: str):
        """List spells by level"""
        try:
            level_num = int(level)
            if level_num < 0 or level_num > 9:
                return await ctx.send("Spell level must be between 0-9")
        except ValueError:
            return await ctx.send("Spell level must be numeric")
        
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/spells/?level={level}', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    desc = ', '.join(list(map(lambda c: c.get('name'), json.get('results', []))))

                    embed = discord.Embed(title=f'Spells: Level {level}', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                else:
                    return await ctx.send('Oops! Something went wrong listing spells.')
        except aiohttp.ClientConnectionError:
            return await ctx.send('Oops! Something went wrong listing spells.')

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

                    duration = json.get('duration', '')
                    concentration = json.get('concentration', False)
                    if concentration:
                        duration = 'Concentration, ' + duration
                    
                    school = json.get('school', {}).get('name')
                    ritual = json.get('ritual', False)
                    if ritual:
                        school = school + ' (Ritual)'

                    classes = ', '.join(list(map(lambda c: c.get('name'), json.get('classes', []))))

                    embed = discord.Embed(title=f'Spell: {name}', description=desc, color=(await ctx.embed_colour()))
                    embed.add_field(name="Level", value=json.get('level'))
                    embed.add_field(name="Casting Time", value=json.get('casting_time'))
                    embed.add_field(name="Range/Area", value=json.get('range'))
                    embed.add_field(name="Components", value=','.join(json.get('components', [])))
                    embed.add_field(name="Duration", value=duration)
                    embed.add_field(name="School", value=school)
                    embed.add_field(name="Damage/Effect", value=json.get('damage', {}).get('damage_type', {}).get('name'))
                    embed.add_field(name="Classes", value=classes)
                    return await ctx.send(embed=embed)
                elif resp.status == 404:
                    return await ctx.send(f'Could not find spell {spell}')
                else:
                    return await ctx.send('Oops! Something went wrong finding spells.')
        except aiohttp.ClientConnectionError:
            return await ctx.send('Oops! Something went wrong finding spells.')
