from discord import Forbidden
from discord.ext.commands import Cog

from lib.db import db


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('welcome')

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
        await self.bot.get_channel(785923224470290436).send(f'Wlcome to **{member.guild.name}** {member.mention}!')
        try:
            await member.send(f'Welcome to ***{member.guild.name}***! Enjoq your stay!')
        except Forbidden:
            pass
        # TO ADD ROLES TO USER
        # await member.add_roles(*list_of_roles)

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
        await self.bot.get_channel(785923224470290436).send(f"{member.display_name} has left {member.guild.name}.")

def setup(bot):
    bot.add_cog(Welcome(bot))