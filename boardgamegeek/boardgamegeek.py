import html
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp
import discord
from redbot.core import commands

baseUrl = 'https://www.boardgamegeek.com/xmlapi2'

class BoardGameGeekException(Exception):
    pass

class BoardGameGeek(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['bgg'])
    async def boardgamegeek(self, ctx, *, query):
        """Lookup a board game on BoardGameGeek

        `query` is the name of the board game you want to lookup
        """
        try:
            id = await self.search(query)
            if id is None:
                return await ctx.send("No results found")
            embed = await self.thing(ctx, id)
            return await ctx.send(embed=embed)
        except BoardGameGeekException as e:
            return await ctx.send(str(e))

    async def search(self, query):
        params = { 'exact': 1, 'query': query, 'type': 'boardgame,boardgameexpansion' }
        async with aiohttp.request('GET', f'{baseUrl}/search', params=params) as resp:
            if resp.status != 200:
                raise BoardGameGeekException(f"Error: {resp.status}")
            text = await resp.text()
            root = ET.fromstring(text)
            item = root.find('./item')
            if item is None:
                return None

            return item.attrib['id']

    async def thing(self, ctx, id):
        params = { 'id': id, 'stats': 1 }
        async with aiohttp.request('GET', f'{baseUrl}/thing', params=params) as resp:
            text = await resp.text()
            root = ET.fromstring(text)

            name = self.value(root, './item/name')
            description = self.text(root, './item/description')
            thumbnail = self.text(root, './item/thumbnail')
            year = self.value(root, './item/yearpublished')
            players = self.players(root)
            playing_time = self.playing_time(root)
            average_rating = self.round_value(root, './item/statistics/ratings/average')
            average_weight = self.round_value(root, './item/statistics/ratings/averageweight')
            publisher = self.value(root, './item/link[@type="boardgamepublisher"]')
            url = f"https://boardgamegeek.com/boardgame/{id}"

            embed = discord.Embed(title=name, description=description, color=(await ctx.embed_colour()))
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name="Average Rating", value=average_rating)
            embed.add_field(name="Year Published", value=year)
            embed.add_field(name="Players", value=players)
            embed.add_field(name="Playing Time", value=playing_time)
            embed.add_field(name="Average Weight", value=average_weight)
            embed.add_field(name="Publisher", value=publisher)
            embed.add_field(name="More Info", value=f"[BoardGameGeek]({url})")
            return embed

    def text(self, root, path):
        element = root.find(path)
        if element is not None:
            return html.unescape(element.text) if element.text else None
        return None

    def playing_time(self, root):
        min = self.value(root, './item/minplaytime')
        max = self.value(root, './item/maxplaytime')
        return f"{min} - {max}"

    def players(self, root):
        min = self.value(root, './item/minplayers')
        max = self.value(root, './item/maxplayers')
        return f"{min} - {max}"

    def value(self, root, path):
        element = root.find(path)
        if element is not None:
            return element.attrib['value']
        return None

    def round_value(self, root, path):
        element = root.find(path)
        if element is not None:
            return round(float(element.attrib['value']), 2)
        return None
