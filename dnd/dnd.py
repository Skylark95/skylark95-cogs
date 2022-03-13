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
        """List magic schools
        
        Do `[p]school <magic_school>` to get info about magic school
        """
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
    async def school(self, ctx: commands.Context, *, magic_school: str):
        """Get info about a magic school
        
        `magic_school` is the name of the magic school
        Do `[p]schools` to list possible magic schools
        """
        index = magic_school.lower()
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/magic-schools/{index}', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    name = json.get('name')
                    desc = json.get('desc')

                    embed = discord.Embed(title=f'Magic School: {name}', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                elif resp.status == 404:
                    return await ctx.send(f'Could not find magic school {magic_school}')
                else:
                    return await ctx.send('Oops! Something went wrong finding magic schools.')
        except aiohttp.aiohttp.ClientConnectionError: 
            return await ctx.send('Oops! Something went wrong finding magic schools.')

    @commands.command()
    async def conditions(self, ctx: commands.Context):
        """List conditions
        
        Do `[p]condition <condition>` to get info about a condition
        """
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
        """Get info about a condition
        
        `condition` is the name of the condition
        Do `[p]conditions` to list possible conditions
        """
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
    async def classes(self, ctx: commands.Context):
        """List character classes
        
        Do `[p]spells <level> [character_class]` to list spells for a class
        """
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/classes', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    desc = ', '.join(list(map(lambda c: c.get('name'), json.get('results', []))))

                    embed = discord.Embed(title=f'Classes', description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                else:
                    return await ctx.send('Oops! Something went wrong listing character classes.')
        except aiohttp.aiohttp.ClientConnectionError: 
            return await ctx.send('Oops! Something went wrong listing character classes.')

    @commands.command()
    async def spells(self, ctx: commands.Context, level: str, *, character_class = ""):
        """List spells by level and optionally class
        
        `level` is the level of the spell (required)
        `character_class` is the class to list spells for (optional)
        Do `[p]classes` to list possible character classes
        Do `[p]spell <spell_name>` to get info about a spell
        """
        try:
            level_num = int(level)
            if level_num < 0 or level_num > 9:
                return await ctx.send("Spell level must be between 0-9")
        except ValueError:
            return await ctx.send("Spell level must be numeric")

        class_spells = []
        if character_class != "":
            index = character_class.lower()
            try:
                async with aiohttp.request('GET', f'{BASE_URL}/classes/{index}/spells', headers=HEADERS) as resp:
                    if resp.status == 200:
                        json = await resp.json()
                        class_spells = list(map(lambda c: c.get('name'), json.get('results', [])))
                        if len(class_spells) == 0:
                            return await ctx.send(f'Unknown character class {character_class}.')
                    elif resp.status == 404:
                        return await ctx.send(f'Unknown character class {character_class}.')
                    else:
                        return await ctx.send('Oops! Something went wrong listing spells.')
            except aiohttp.ClientConnectionError:
                return await ctx.send('Oops! Something went wrong listing spells.')
        
        try:
            async with aiohttp.request('GET', f'{BASE_URL}/spells/?level={level}', headers=HEADERS) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    title = f'Spells: Level {level}'
                    spells = list(map(lambda c: c.get('name'), json.get('results', [])))
                    if len(class_spells) > 0:
                        title = title + ' ' + character_class.capitalize()
                        spells = sorted(list(set(spells) & set(class_spells)))
                    desc = ', '.join(spells)
                    embed = discord.Embed(title=title, description=desc, color=(await ctx.embed_colour()))
                    return await ctx.send(embed=embed)
                else:
                    return await ctx.send('Oops! Something went wrong listing spells.')
        except aiohttp.ClientConnectionError:
            return await ctx.send('Oops! Something went wrong listing spells.')

    @commands.command()
    async def spell(self, ctx: commands.Context, *, spell_name: str):
        """Get info about a spell
        
        `spell_name` is the name of the spell
        Do `[p]spells <level> [character_class]` to list possible spells
        """
        index = spell_name.lower().replace(' ', '-')
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
                    return await ctx.send(f'Could not find spell {spell_name}')
                else:
                    return await ctx.send('Oops! Something went wrong finding spells.')
        except aiohttp.ClientConnectionError:
            return await ctx.send('Oops! Something went wrong finding spells.')

    @commands.command(aliases=["heal"])
    async def healing(self, ctx: commands.Context):
        """Get info about Potions of Healing"""
        desc = "Potion, varies\n\nYou regain hit points when you drink this potion. The number of hit points depends on the potion's rarity, " \
            "as shown in the Potions of Healing table. Whatever its potency, the potion's red liquid glimmers when agitated."
        embed = discord.Embed(title='Potions of Healing (table)', description=desc, color=(await ctx.embed_colour()))
        embed.add_field(name="Healing", value="2d4 + 2")
        embed.add_field(name="Greater healing", value="4d4 + 4")
        embed.add_field(name="Superior healing", value="8d4 + 8")
        embed.add_field(name="Supreme healing", value="10d4 + 20")
        return await ctx.send(embed=embed)
