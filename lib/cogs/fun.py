from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord.errors import HTTPException, InvalidArgument
from discord.ext.commands import Cog, BucketType, cooldown
from discord.ext.commands import command


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='hello', aliases=['hi'])
    async def say_hello(self, ctx):
        """
        Saying hello to someone
        :param ctx:
        :return:
        !hello @someone
        """
        await ctx.channel.send(f'{choice(("Hello", "Hi", "Hey", "Wassup", "Sup bro", "Hi there", "Hello there"))} {ctx.message.author.mention}!')

    @command(name='dice', aliases=['roll'])
    @cooldown(1, 60, BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        """
        Roll a n number of custom dices
        :param ctx:
        :param die_string:
        :return:
        !roll 2d6
        """
        dice, value = (int(term) for term in die_string.split('d'))
        rolls = [randint(1, value) for i in range(dice)]

        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @roll_dice.error
    async def roll_dice_error(self, ctx, exc):
        if isinstance(exc, HTTPException):
            await ctx.send('Result too large. Please try a lower number.')

    @command(name='slap', aliases=['hit'])
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for No reason"):
        """
        Slaps dem boyz for some specific reason or just for lulz
        :param ctx:
        :param member:
        :param reason:
        :return:
        !slap @boy
        !slap @boy for a reason
        """
        await ctx.send(f'{ctx.author.display_name} slapped {member.mention} {reason}!')

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, InvalidArgument):
            await ctx.send('Can`t find that member')

    @command(name='echo', aliases=['say'])
    async def echo_message(self, ctx, *, message):
        """
        bot just echoing a message and deleting it beforehand
        :param ctx:
        :param message:
        :return:
        !echo message
        """
        await ctx.message.delete()
        await ctx.send(message)

    @command(name='fact')
    async def animal_fact(self, ctx, animal: str = None):
        """
        Displaying a random fact about a random animal, or a random fact about specific animal
        :param ctx:
        :param animal:
        :return:
        !fact
        !fact cat
        """
        ANIMALS = ['dog', 'cat', 'panda', 'fox', 'bird', 'koala']
        if animal is None:
            animal = choice(ANIMALS)
        if (animal := animal.lower()) in ANIMALS:
            fact_url = f'https://some-random-api.ml/facts/{animal}'
            image_url = f'https://some-random-api.ml/img/{"birb" if animal == "bird" else animal}'

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data['link']
                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f'{animal.title()} fact',
                                  description=data['fact'],
                                  colour=ctx.author.colour
                                  )
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f'Api returned {response.status} status')
        else:
            await ctx.send('No fact for this animal')


    @Cog.listener()
    async def on_ready(self):
        # await self.bot.stdout.send('Fun cog ready')
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')

def setup(bot):
    bot.add_cog(Fun(bot))