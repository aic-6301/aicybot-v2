import discord
from discord.ext import commands

from logging import getLogger, basicConfig, DEBUG
from dotenv import load_dotenv
import coloredlogs
import os
import sys
import traceback
import asyncio
import datetime

from utils import database

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

class aicybot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('a.'),
            help_command=None,
            intents=discord.Intents.all()
        )
        basicConfig(level=DEBUG)  # ログの基本設定を追加
        self.logger = getLogger('AicyBot')
        coloredlogs.install(level=DEBUG, logger=self.logger)
        self.logger.setLevel(DEBUG)
        self.uptime = datetime.datetime.now()

    async def on_ready(self):
        self.change_presence(status=discord.Status.dnd)
        if sys.version_info < (3, 12):
            self.logger.critical('Python 3.12以上が必要です。')
            sys.exit()
            
        self.logger.debug('Setup Database')
        database.setup()
        self.logger.info('Loaded Database')
        self.logger.debug('Loading Cogs')
        for file in os.listdir("./cogs"):
            if file.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{file[:-3]}')
                    self.logger.info(f"Loaded cogs: cogs.{file[:-3]}")
                except Exception as e:
                    self.logger.info(f"cogs.{file[:-3]} failed to load", e)
                    traceback.print_exc()
        self.logger.debug('Loaded All Cogs!')
        self.logger.debug('Loading jishaku')
        try:
            await self.load_extension('jishaku')
            self.logger.info("Loaded cogs: jishaku")
        except Exception as e:
            self.logger.info("jishaku failed to load", e)
            traceback.print_exc()
        self.logger.debug('Syncing slash commands')
        synced = await self.tree.sync()
        self.logger.info(f"Synced {len(synced)} commands")
        self.logger.info('Bot is ready!')

    

if __name__ == '__main__':
    bot = aicybot()
    bot.run(token)