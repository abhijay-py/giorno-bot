import discord
from discord.ext import commands, tasks
from discord.utils import get
import datetime
from helper import pluginEnabled, create_connection, create_table, error_helper
import sqlite3
from sqlite3 import Error

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member = None):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        role = get(ctx.guild.roles, name="muted")
        if role == None:
            await ctx.guild.create_role(name="muted")
            role = get(ctx.guild.roles, name="muted")
        overwrite = discord.PermissionOverwrite(send_messages=False)
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, overwrite=overwrite)
        await member.add_roles(role)
        await ctx.send(f'{member} was muted!')

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member = None):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        role = get(ctx.guild.roles, name="muted")
        if role == None:
            await ctx.guild.create_role(name="muted")
            role = get(ctx.guild.roles, name="muted")
        overwrite = discord.PermissionOverwrite(send_messages=True)
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, overwrite=overwrite)
        await member.remove_roles(role)
        await ctx.send(f'{member} was unmuted!')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self,ctx, amount=1):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        if (amount < 1):
            await ctx.send("Please enter a valid amount of messages (>= 1).")
        amount += 1
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self,ctx, member: discord.Member = None, *, reason=None):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        await member.kick(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        await member.ban(reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self,ctx, *, member = ""):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        banned_users = await ctx.guild.bans()
        if len(member.split("#"))!= 2:
            await ctx.send("Please enter a valid user.")
            return
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}.')
                return

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self,ctx, amount: int = 0, *, reason: str = "None"):
        if not await pluginEnabled("moderation",ctx.guild):
            return
        if amount < 0:
            await ctx.send("Please enter a valid amount for slow mode in seconds (>= 0).")
            return
        if amount > 21600:
            await ctx.send("The max slowmode time is 6 hours (21600 seconds).")
            return
        await ctx.channel.edit(reason=reason, slowmode_delay=amount)
        if amount != 0:
            minute = amount//60
            seconds = amount-minute*60
            hour = minute//60
            minute = minute-hour*60
            await ctx.send("Enabled Slowmode for "+ str(hour) + " hours, "+ str(minute)+" minutes, and "+str(seconds)+" seconds due to " + reason + ".")
        else:
            await ctx.send("Disabled Slowmode.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason=None):
        if not await pluginEnabled("moderation", ctx.guild):
            return
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        if reason == None:
            reasoned = "None"
        else:
            reasoned = reason

        database = "fullDB.db"
        conn = create_connection(database)

        now = datetime.datetime.now()
        timeStr = now.strftime("%m/%d/%Y, %H:%M:%S")
        username = member.id
        curr = conn.cursor()
        task_1 = (ctx.guild.id, username, reasoned, timeStr)
        sql = ''' INSERT INTO warns(guild, user, warn, date) 
                     VALUES(?,?,?,?) '''
        curr.execute(sql, task_1)
        conn.commit()
        embed = discord.Embed(colour=discord.Colour.blue(), description="Reason: " + reasoned)
        embed.set_author(name=str(member) + " has been warned.", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def infractions(self, ctx, member: discord.Member = None):
        if not await pluginEnabled("moderation", ctx.guild):
            return
        database = "fullDB.db"
        conn = create_connection(database)
        curr = conn.cursor()
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        try:
            curr.execute("SELECT * FROM warns WHERE user=" + str(member.id) + " AND guild="+str(ctx.guild.id))
        except:
            embed = discord.Embed(title=member.display_name + "'s Infractions",
                                  description="Infractions: 0",
                                  color=discord.Colour.blue())
            await ctx.send(embed=embed)
            return
        results = curr.fetchall()
        embed = discord.Embed(title=member.display_name + "'s Infractions",
                              description="Infractions: " + str(len(results)), color=discord.Colour.blue())
        i = 1
        for id, guild, user, warn, date in results:
            embed.add_field(name=str(i) + ". Warning on " + date + " GMT", value=warn, inline=False)
            i += 1
        await ctx.send(embed=embed)

    @commands.command(aliases = ["remove_warn"])
    @commands.has_permissions(manage_roles = True)
    async def removeWarn(self, ctx, member:discord.Member = None, amount:int = 1):
        if not await pluginEnabled("moderation", ctx.guild):
            return
        database = "fullDB.db"
        conn = create_connection(database)
        curr = conn.cursor()
        if member is None or member not in member.guild.members:
            await ctx.send('Please pass in a valid user.')
            return
        try:
            curr.execute("SELECT * FROM warns WHERE user=" + str(member.id) + " AND guild="+str(ctx.guild.id))
        except:
            await ctx.send("This user has no warnings!")
            return
        results = curr.fetchall()
        if len(results) < amount:
            await ctx.send("This user only has "+str(len(results))+" warnings!")
            return
        elif amount < 1:
            await ctx.send("Please choose a valid warning (>=1).")
            return
        id = results[amount-1][0]
        sql = 'DELETE FROM warns WHERE id=' + str(id)
        curr.execute(sql)
        conn.commit()
        await ctx.send("Removed warning for " + str(member) + ", from " + results[amount - 1][4] + " GMT.")

    @removeWarn.error
    @infractions.error
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BadArgument):
            return
        if (await error_helper(ctx, True)):
            return

    @mute.error
    @unmute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BadArgument):
            return
        if (await error_helper(ctx, True)):
            return
        await ctx.send("Please give the bot permission to manage roles.")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BadArgument):
            return
        if (await error_helper(ctx, True)):
            return
        await ctx.send("Please give the bot permission to manage messages.")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BadArgument):
            return
        if (await error_helper(ctx, True)):
            return
        await ctx.send("Please give the bot permission to kick people.")

    @unban.error
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BadArgument):
            return
        if (await error_helper(ctx, True)):
            return
        await ctx.send("Please give the bot permission to ban people.")

    @slowmode.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BadArgument):
            return
        if (await error_helper(ctx, True)):
            return
        await ctx.send("Please give the bot permission to manage channels.")