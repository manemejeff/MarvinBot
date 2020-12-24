import os
from asyncio import sleep
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents, Forbidden, DMChannel, Embed
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, Context, MissingRequiredArgument, CommandOnCooldown
from discord.ext.commands import when_mentioned_or

from lib.db import db
from settings.settings import TEST_TOKEN, BASE_DIR, COG_DIR

OWNER_IDS = []
COGS = [os.path.join(COG_DIR, f[:-3]).replace('/', '.') for f in os.listdir(os.path.join(BASE_DIR, COG_DIR)) if os.path.isfile(os.path.join(os.path.join(BASE_DIR, COG_DIR), f))]

def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM Guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)

class Ready(object):
    def __init__(self):
        print(COGS)
        for cog in COGS:
            setattr(self, cog, True)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'{cog} cog is ready')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):

    def __init__(self):
        # self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents().all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f'{cog}')
            print(f'{cog} cog loaded')

        print('Setup complete')

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (USerID) VALUES (?)",
                     ((member.id,) for guild in self.guilds for member in guild.members if not member.bot))

        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                     ((id_,) for id_ in to_remove))

        db.commit()

    def run(self, version):
        self.VERSION = version
        print('Running setup...')
        self.setup()

        print('Running bot...')
        super().run(TEST_TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send('I`m not ready to recieve command. Please wait a few seconds')

    async def rules_reminder(self):
        await self.stdout.send('This is timed message')

    # @command(name='prefix')
    # @has_permissions(manage_guild=True)
    # async def change_prefix(self, ctx, new: str):
    #     if len(new) > 5:
    #         await ctx.send('Prefix can not be more than 5 characters in length.')
    #     else:
    #         db.execute('UPDATE guilds SET Prefix = ? WHERE GuildID = ?', new, ctx.guild.id)
    #         await ctx.send(f'Prefix set to {new}')


    async def on_connect(self):
        print('Bot connected!')

    async def on_disconnect(self):
        print('Bot disconnected!')

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            await args[0].send('Something went wrong.')

        await self.stdout.send('An arror occured')
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send('One or more arguments are missing')

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f'That command is on {str(exc.cooldown.type).split(".")[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.')

        elif hasattr(exc, 'original'):

            if isinstance(exc.original, Forbidden):
                await ctx.send('I do not have permission to do that')
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:

            self.guild = self.get_guild(785923224470290433)
            self.stdout = self.get_channel(785923224470290436)

            # ADDING JOBS
            # self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()

            self.update_db()

            # await self.stdout.send('Now online')

            # CREATING AND SENDING EMBED
            # --------------------------------------------------------------
            # embed = Embed(title='Now online!',
            #               description='Marvin is now online.',
            #               colour=0xFF0000,
            #               timestamp=datetime.utcnow())
            # fields = [
            #     ('Name', 'Value', True),
            #     ('Another field', 'Second Field', True),
            #     ('A non-inline field', 'Third field', False)
            # ]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name='Marvin bot', icon_url=self.guild.icon_url)
            # embed.set_footer(text='This is footer')
            # await channel.send(embed=embed)

            # SOME OTHER SNIPPETS
            # ---------------------------------------------------------------
            # THUMBNAIL IS SMALLER PICTURE IN RIGHT CORNER
            # embed.set_thumbnail(url=self.guild.icon_url)
            # IMAGE IS BIG PICTURE IN THE BOTTOM OF EMBED
            # embed.set_image(url=self.guild.icon_url)
            # SEND A PICTURE FILE IN CHAT
            # await channel.send(file=File('./images/Marvin1.jpg'))
            while not self.cogs_ready.all_ready():
                await sleep(0.5)
            self.ready = True
            print('Logged on as {0}!'.format(self.user))

        else:
            print('Bot reconnected!')

    async def on_message(self, message):
        # print('Message from {0.author}: {0.content}'.format(message))
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if len(message.content) < 50:
                    await message.channel.send('Your message should be at least 50 characters in length.')

                else:
                    member = self.guild.get_member(message.author.id)
                    embed = Embed(title='Modmail',
                                  colour=member.colour,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=member.avatar_url)

                    fields = [
                        ('Member', member.display_name, False),
                        ('Message', message.content, False),
                    ]
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    mod = self.get_cog('Mod')
                    await mod.log_channel.send(embed=embed)
                    await message.channel.send('Message relayed to moderator')
            else:
                await self.process_commands(message)
