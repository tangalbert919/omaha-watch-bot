import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import json
import aiohttp
import asyncio

class WatchBot(commands.Bot):

    def __init__(self):
        self.stable_version = '0'
        self.beta_version = '0'
        self.dev_version = '0'
        self.canary_version = '0'
        super().__init__(command_prefix='o_')

    async def on_ready(self):
        print('Logged in')
        async with aiohttp.ClientSession() as session:
            async with session.get('https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/all/versions/all/releases?filter=endtime=none&order_by=fraction%20desc') as resp:
                data = await resp.json()
            await session.close()
        self.stable_version = data['releases'][0]['version']
        self.beta_version = data['releases'][1]['version']
        self.dev_version = data['releases'][2]['version']
        self.canary_version = data['releases'][3]['version']
        self.loop.create_task(self.fetch_omaha())

    async def on_message(self, message):
        if message.author == self.user:
            return

    async def fetch_omaha(self):
        # This function runs every hour.
        while not self.is_closed():
            async with aiohttp.ClientSession() as session:
                async with session.get('https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/all/versions/all/releases?filter=endtime=none&order_by=fraction%20desc') as resp:
                    data = await resp.json()
                await session.close()
            if data['releases'][0]['version'] != self.stable_version:
                self.stable_version = data['releases'][0]['version']
                embed = discord.Embed(title='Stable update available!', color=discord.Colour.green())
                embed.add_field(name='New version: ', value=self.stable_version, inline=False)
                await self.sendEmbed(embed, title='Chromium Stable Channel')
            if data['releases'][1]['version'] != self.beta_version:
                self.beta_version = data['releases'][1]['version']
                embed = discord.Embed(title='Beta update available!', color=discord.Colour.gold())
                embed.add_field(name='New version: ', value=self.beta_version, inline=False)
                await self.sendEmbed(embed, title='Chromium Beta Channel')
            if data['releases'][2]['version'] != self.dev_version:
                self.dev_version = data['releases'][2]['version']
                embed = discord.Embed(title='Dev update available!', color=discord.Colour.red())
                embed.add_field(name='New version: ', value=self.dev_version, inline=False)
                await self.sendEmbed(embed, title='Chromium Dev Channel')
            if data['releases'][3]['version'] != self.canary_version:
                self.canary_version = data['releases'][3]['version']
                embed = discord.Embed(title='Canary update available!', color=discord.Colour.purple())
                embed.add_field(name='New version: ', value=self.canary_version, inline=False)
                await self.sendEmbed(embed, title='Chromium Canary Channel')
            await asyncio.sleep(1800)

    async def sendEmbed(self, embed, title=None):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url('url-here', adapter=AsyncWebhookAdapter(session))
            await webhook.send(embed=embed, username=title)
            await session.close()


client = WatchBot()
client.run('token')
