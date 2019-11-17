import discord
from discord.ext import commands
import json
import aiohttp
import asyncio

class WatchBot(commands.Bot):

    def __init__(self):
        self.stable_version = '0'
        self.beta_version = '0'
        self.dev_version = '0'
        super().__init__(command_prefix='o_')

    async def on_ready(self):
        print('Logged in')
        async with aiohttp.ClientSession() as session:
            async with session.get('https://omahaproxy.appspot.com/all.json?os=linux') as resp:
                data = await resp.json()
            await session.close()
        self.stable_version = data[0]['versions'][2]['version']
        self.beta_version = data[0]['versions'][1]['version']
        self.dev_version = data[0]['versions'][0]['version']
        self.loop.create_task(self.fetch_omaha())

    async def on_message(self, message):
        if message.author == self.user:
            return

    async def fetch_omaha(self):
        # This function runs every hour.
        channel = self.get_channel(645121830268698634)
        embed = discord.Embed(title="Update available", color=discord.Colour.blue())
        async with aiohttp.ClientSession() as session:
            async with session.get('https://omahaproxy.appspot.com/all.json?os=linux') as resp:
                data = await resp.json()
            await session.close()
        if data[0]['versions'][2]['version'] != self.stable_version:
            self.stable_version = data[0]['versions'][2]['version']
            embed = discord.Embed(title='Stable update available!', color=discord.Colour.blue())
            embed.add_field(name='New version: ', value=self.stable_version, inline=False)
            await channel.send(embed=embed)
        if data[0]['versions'][1]['version'] != self.beta_version:
            self.beta_version = data[0]['versions'][1]['version']
            embed = discord.Embed(title='Beta update available!', color=discord.Colour.yellow())
            embed.add_field(name='New version: ', value=self.beta_version, inline=False)
            await channel.send(embed=embed)
        if data[0]['versions'][0]['version'] != self.dev_version:
            self.dev_version = data[0]['versions'][0]['version']
            embed = discord.Embed(title='Dev update available!', color=discord.Colour.red())
            embed.add_field(name='New version: ', value=self.dev_version, inline=False)
            await channel.send(embed=embed)
        await asyncio.sleep(3600)

client = WatchBot()
client.run('token')
