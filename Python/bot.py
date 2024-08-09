import discord
from discord import Webhook, Intents
from discord.ext import commands
from checkin import checkin_generator_pb2
import json
import aiohttp
import asyncio
import argparse
import gzip
import utils

parser = argparse.ArgumentParser()
parser.add_argument('--enable-android-ota', action='store_true', help='Enables Android OTA detection. You must have "android.json" populated with build fingerprints first.')
parser.add_argument('--token', required=True, help='Run the Discord bot with this token. Required.')
parser.add_argument('--webhook-url', required=True, help='Send messages to this webhook URL. Required.')
args = parser.parse_args()

class WatchBot(commands.Bot):

    def __init__(self):
        self.stable_version = '0'
        self.beta_version = '0'
        self.dev_version = '0'
        self.canary_version = '0'
        if args.enable_android_ota:
            self.fingerprint_list = json.loads(open('android.json', 'r').read())
            self.response = checkin_generator_pb2.AndroidCheckinResponse()
        super().__init__(command_prefix='o_', intents=Intents.default())

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
        if args.enable_android_ota:
            self.loop.create_task(self.fetch_android())

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

    async def fetch_android(self):
        # This function runs every two hours.
        while not self.is_closed():
            for fingerprint in self.fingerprint_list:
                found = False
                download_url = ""
                (payload, headers) = utils.construct_payload(fingerprint)
                # TODO: Implement
                with gzip.open('android_data.gz', 'wb') as f:
                    f.write(payload)
                    f.close()
                post_data = open('android_data.gz', 'rb')
                async with aiohttp.ClientSession() as session:
                    async with session.post('https://android.googleapis.com/checkin', data=post_data, headers=headers) as resp:
                        # todo: implement
                        data = await resp.text()
                        self.response.ParseFromString(data)
                        print(await resp.text())
                        for entry in self.response.setting:
                            if b'https://android.googleapis.com' in entry.value:
                                print("OTA URL obtained: " + entry.value.decode())
                                found = True
                                download_url = entry.value.decode()
                                break
                post_data.close()
                if found:
                    #embed = discord.Embed(title='New package available!', color=discord.Colour.blue())
                    #embed.add_field()
                    print("New data found")
                await asyncio.sleep(5)
            await asyncio.sleep(30)

    async def sendEmbed(self, embed, title=None):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(args.webhook_url, session=session)
            await webhook.send(embed=embed, username=title)
            await session.close()


client = WatchBot()
client.run(args.token)
