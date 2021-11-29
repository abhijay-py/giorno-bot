import discord
from discord.ext import commands, tasks
from discord.utils import get
import datetime
from helper import pluginEnabled, create_connection, create_table, error_helper
import sqlite3
from disputils import *
import random
import datetime
import pytz
from sqlite3 import Error


botID = 785687696781737995
def getPrefixx(client, message):
    if message.guild == None:
        return "~"
    conn = create_connection("fullDB.db")
    curr = conn.cursor()
    curr.execute("SELECT guild,prefix FROM prefixes;")
    results = curr.fetchall()
    guilds = [int(i[0]) for i in results]
    index = guilds.index(message.guild.id)
    return results[index][1]

logs = ["messages", "channels", "pins", "join/leave", "member updates", "server updates", "roles", "emojis", "voice", "bans", "invites"]
realLogs = ["message", "channels", "pins", "jl", "ronick", "updat", "role", "emoji", "voice", "bans", "invite"]

async def logEnabled(log, guild):
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute(
        "SELECT message, channels, pins, jl, ronick, updat, role, emoji, voice, bans, invite FROM logs WHERE guild=" + str(
            guild.id) + ";")
    try:
        result = curr.fetchall()[0]
        result = list(result)
    except:
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    index = len(realLogs)
    for i in range(len(realLogs)):
        if logs[i] == log:
            index = i
            break

    if result[index] == 0:
        return False
    return True

async def getPerms(role):
    pass

invites = []

class Logs(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not await pluginEnabled("logging", message.guild):
            return
        if not await logEnabled("messages", message.guild):
            return
        if message.content == None:
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                message.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        embed = discord.Embed(colour=discord.Colour.red(), description = "Message deleted in "+message.channel.mention)
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        user = self.client.get_user(botID)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        embed.add_field(name = "Content", value = message.content, inline=False)
        embed.add_field(name = "Date Sent", value = message.created_at.strftime("%a, %d %b %Y %H:%M:%S")+" GMT")
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        try:
            await channel.send(embed = embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, messageb, messagea):
        if not await pluginEnabled("logging", messagea.guild):
            return
        if not await logEnabled("messages", messagea.guild):
            return
        if messageb.content == messagea.content:
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                messagea.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        embed = discord.Embed(colour=discord.Colour.red(), description= "**"+str(messageb.author)+"** updated their message in " + str(messageb.channel)+".")
        embed.set_author(name=str(messagea.author), icon_url=messagea.author.avatar_url)
        user = self.client.get_user(botID)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        embed.add_field(name="Channel", value=channel.mention+"\n[Go To Message]("+ messagea.jump_url + " 'Go To Message')")
        embed.add_field(name="Now", value=messagea.content, inline=False)
        embed.add_field(name="Previous", value=messageb.content, inline=False)
        embed.set_author(name=str(messagea.author), icon_url=messagea.author.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not await pluginEnabled("logging", member.guild):
            return
        if not await logEnabled("join/leave", member.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                member.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        embed = discord.Embed(colour=discord.Colour.red(),
                              description= "**"+str(member)+ "** joined")
        user = self.client.get_user(botID)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        embed.add_field(name="Name", value=str(member)+" "+member.mention)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%a, %d %b %Y %H:%M:%S")+" GMT", inline=False)
        embed.add_field(name="Member Count", value=len(member.guild.members), inline=True)
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        if not await pluginEnabled("logging", member.guild):
            return
        if not await logEnabled("join/leave", member.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                member.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        embed = discord.Embed(colour=discord.Colour.red(),
                              description="**"+str(member) + "** left")
        user = self.client.get_user(botID)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        embed.add_field(name="Name", value=str(member) +" "+ member.mention)
        des = "None"
        checker = True
        for role in member.roles:
            if checker:
                checker = not checker
            elif des == "None":
                des= str(role)
            else:
                des+= ", "+str(role)
        embed.add_field(name = "Roles", value = des, inline=False)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%a, %d %b %Y %H:%M:%S") + " GMT",
                        inline=False)
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        if not await pluginEnabled("logging", guild):
            return
        if not await logEnabled("bans", guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        logged = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        logged = logged[0]
        embed = discord.Embed(colour=discord.Colour.red(),
                              description="**"+str(member) + "** was banned")
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.set_footer(text=str(logged.user), icon_url=logged.user.avatar_url)
        embed.add_field(name="User Information", value=str(member) + " " + member.mention)
        if logged.reason == None:
            embed.add_field(name="Reason", value="None", inline=False)
        else:
            embed.add_field(name="Reason", value=logged.reason, inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        if not await pluginEnabled("logging", guild):
            return
        if not await logEnabled("bans", guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        logged = await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
        logged = logged[0]
        embed = discord.Embed(colour=discord.Colour.red(),
                              description="**"+str(member) + "** was unbanned")
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.set_footer(text=str(logged.user), icon_url=logged.user.avatar_url)
        embed.add_field(name="User Information", value=str(member) + " " + member.mention)
        if logged.reason == None:
            embed.add_field(name="Reason", value="None", inline=False)
        else:
            embed.add_field(name="Reason", value=logged.reason, inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, vb, va):
        if not await pluginEnabled("logging", member.guild):
            return
        if not await logEnabled("voice", member.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                member.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        embed = discord.Embed(colour=discord.Colour.red(),
                              description="**" + str(member) + "** had their voice state updated.")
        if va.channel == vb.channel and va.deaf == vb.deaf and va.mute == vb.mute:
            return
        if va.channel != vb.channel:
            if va.channel == None:
                embed = discord.Embed(colour=discord.Colour.red(),
                                      description="**"+str(member) + "** left voice channel: "+str(vb.channel)+".")
                user = self.client.get_user(botID)
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Channel", value=str(vb.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            elif vb.channel == None:
                embed = discord.Embed(colour=discord.Colour.red(),
                                      description="**" + str(member) + "** joined voice channel: " + str(
                                          va.channel) + ".")
                user = self.client.get_user(botID)
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Channel", value=str(va.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(colour=discord.Colour.red(),
                                      description="**" + str(member) + "** moved from #"+str(vb.channel)+" to #" + str(va.channel) + ".")
                user = self.client.get_user(botID)
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Current Channel", value=str(va.channel))
                embed.add_field(name="Previous Channel", value=str(vb.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            return
        elif va.deaf != vb.deaf:
            logged = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update).flatten()
            logged = logged[0]
            if va.deaf:
                user = logged.user
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Action", value="server deafened")
                embed.add_field(name="Voice Channel", value=str(va.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            else:
                user = logged.user
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Action", value="undeafened")
                embed.add_field(name="Voice Channel", value=str(va.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            return
        else:
            logged = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update).flatten()
            logged = logged[0]
            if va.mute:
                user = logged.user
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Action", value="server muted")
                embed.add_field(name="Voice Channel", value=str(va.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            else:
                user = logged.user
                embed.set_footer(text=str(user), icon_url=user.avatar_url)
                embed.add_field(name="Action", value="unmuted")
                embed.add_field(name="Voice Channel", value=str(va.channel))
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await channel.send(embed=embed)
            return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if not await pluginEnabled("logging", role.guild):
            return
        if not await logEnabled("roles", role.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                role.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        logged = await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten()
        logged = logged[0]
        user = self.client.get_user(botID)
        embed = discord.Embed(colour=discord.Colour.red(),
                              description=" A role was deleted")
        embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        embed.add_field(name="Name", value=str(role))
        if logged.reason == None:
            embed.add_field(name="Reason", value="None", inline=False)
        else:
            embed.add_field(name="Reason", value=logged.reason, inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if not await pluginEnabled("logging", role.guild):
            return
        if not await logEnabled("roles", role.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                role.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        logged = await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create).flatten()
        logged = logged[0]
        user = self.client.get_user(botID)
        embed = discord.Embed(colour=discord.Colour.red(),
                              description="A role was created.")

        if str(role) != "new role":
            embed.add_field(name="Bot Role", value=str(role))
        else:
            embed.add_field(name="Name", value = str(role))
        embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, rb, ra):
        if not await pluginEnabled("logging", ra.guild):
            return
        if not await logEnabled("roles", ra.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                ra.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        logged = await ra.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update).flatten()
        logged = logged[0]
        user = self.client.get_user(botID)
        if rb.colour != ra.colour:
            embed = discord.Embed(colour=ra.color,
                                  description="A role was updated")
        else:
            embed = discord.Embed(colour=discord.Colour.red(),
                              description="A role was updated")
        embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
        embed.set_footer(text=str(user), icon_url=user.avatar_url)
        now = ""
        old = ""
        if rb.hoist==ra.hoist and rb.colour==ra.color and rb.name == ra.name and rb.mentionable==ra.mentionable and rb.permissions==ra.permissions:
            return

        if rb.name != ra.name:
            now += "Name = " + str(ra.name) + "\n"
            old += "Name = " + str(rb.name) + "\n"
        if rb.colour != ra.colour:
            now += "Color = " + str(ra.color) + "\n"
            old+= "Color = " + str(rb.color) + "\n"
        if rb.mentionable != ra.mentionable:
            if rb.mentionable:
                old += "Mentionable = True\n"
                now += "Mentionable = False\n"
            else:
                now += "Mentionable = True\n"
                old += "Mentionable = False\n"
        if rb.hoist != ra.hoist:
            if rb.hoist:
                now += "Displayed Separately = False\n"
                old += "Displayed Separately = True\n"
            else:
                now += "Displayed Separately = True\n"
                old += "Displayed Separately = False\n"
        if rb.permissions != ra.permissions:
            pass
        embed.add_field(name = "Now", value=now, inline=False)
        embed.add_field(name = "Old", value=old, inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, mb, ma):
        if not await pluginEnabled("logging", ma.guild):
            return
        if not await logEnabled("member updates", ma.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                ma.guild.id) + ";")
        result = curr.fetchall()[0][0]
        channel = self.client.get_channel(result)
        if ma.nick == mb.nick and len(ma.roles) == len(mb.roles):
            return

        if ma.nick != mb.nick:
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="**" + str(ma) + "** " + ma.mention + " had their nickname updated.")
            if ma.nick == None:
                embed.add_field(name="New Name", value=str(ma).split("#")[0])
            else:
                embed.add_field(name="New Name", value=ma.nick)
            if mb.nick == None:
                embed.add_field(name="Old Name", value=str(mb).split("#")[0])
            else:
                embed.add_field(name="Old Name", value=mb.nick)
            user = self.client.get_user(botID)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.set_author(name=str(ma), icon_url=ma.avatar_url)
            await channel.send(embed=embed)
        else:
            logged = await ma.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()
            logged = logged[0]
            if len(ma.roles) > len(mb.roles):
                mbRoles = [role.name for role in mb.roles]
                embed = discord.Embed(colour=discord.Colour.red(),
                                      description="**" + str(ma) + "** " + ma.mention + " got a new role.")
                embed.set_footer(text=str(logged.user), icon_url=logged.user.avatar_url)
                embed.set_author(name=str(ma), icon_url=ma.avatar_url)
                for role in ma.roles:
                    if role.name not in mbRoles:
                        embed.add_field(name="New Role", value=role.name)
                        break
                await channel.send(embed = embed)
            else:
                maRoles = [role.name for role in ma.roles]
                embed = discord.Embed(colour=discord.Colour.red(),
                                      description="**" + str(ma) + "** " + ma.mention + " lost a role.")
                embed.set_footer(text=str(logged.user), icon_url=logged.user.avatar_url)
                embed.set_author(name=str(ma), icon_url=ma.avatar_url)
                for role in mb.roles:
                    if role.name not in maRoles:
                        embed.add_field(name="Old Role", value=role.name)
                        break
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not await pluginEnabled("logging", channel.guild):
            return
        if not await logEnabled("channels", channel.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                channel.guild.id) + ";")
        result = curr.fetchall()[0][0]
        c = self.client.get_channel(result)
        logged = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()
        logged = logged[0]
        user = self.client.get_user(botID)
        if isinstance(channel, discord.TextChannel):
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="A text channel was created.\nChannel: "+channel.mention)
            embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.add_field(name = "Name", value = channel.name)
            embed.add_field(name="Position", value=str(channel.position + 1))
            if channel.category == None:
                embed.add_field(name = "Category", value = "None", inline=False)
            else:
                embed.add_field(name = "Category", value = channel.category, inline=False)

            await c.send(embed=embed)
        elif isinstance(channel, discord.VoiceChannel):
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="A voice channel was created.\nChannel: "+channel.mention)
            embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.add_field(name="Name", value=channel.name)
            embed.add_field(name="Position", value=str(channel.position + 1))
            if channel.category == None:
                embed.add_field(name="Category", value="None", inline=False)
            else:
                embed.add_field(name="Category", value=channel.category, inline=False)

            await c.send(embed=embed)
        else:
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="A category was created.\nCategory: "+channel.name)
            embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.add_field(name="Name", value=channel.name)
            embed.add_field(name="Position", value=str(channel.position+1))
            await c.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not await pluginEnabled("logging", channel.guild):
            return
        if not await logEnabled("channels", channel.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT channel FROM logs WHERE guild=" + str(
                channel.guild.id) + ";")
        result = curr.fetchall()[0][0]
        c = self.client.get_channel(result)
        logged = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()
        logged = logged[0]
        user = self.client.get_user(botID)
        if isinstance(channel, discord.TextChannel):
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="A text channel was deleted.")
            embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.add_field(name="Name", value=channel.name)
            embed.add_field(name="Position", value=str(channel.position + 1))
            if channel.category == None:
                embed.add_field(name="Category", value="None", inline=False)
            else:
                embed.add_field(name="Category", value=channel.category, inline=False)

            await c.send(embed=embed)
        elif isinstance(channel, discord.VoiceChannel):
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="A voice channel was deleted.")
            embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.add_field(name="Name", value=channel.name)
            embed.add_field(name="Position", value=str(channel.position + 1))
            if channel.category == None:
                embed.add_field(name="Category", value="None", inline=False)
            else:
                embed.add_field(name="Category", value=channel.category, inline=False)

            await c.send(embed=embed)
        else:
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="A category was deleted.")
            embed.set_author(name=str(logged.user), icon_url=logged.user.avatar_url)
            embed.set_footer(text=str(user), icon_url=user.avatar_url)
            embed.add_field(name="Name", value=channel.name)
            embed.add_field(name="Position", value=str(channel.position + 1))
            await c.send(embed=embed)



    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def logs(self, ctx):
        if not await pluginEnabled("logging", ctx.guild):
            return
        embed = discord.Embed(color=discord.Colour.blue(), title="Logs",
                              description="``messages``, ``channels``, ``pins``, ``join/leave``, ``member updates``, ``server updates``, ``roles``, ``emojis``, ``voice``, ``bans``, ``invites``")
        embed.set_footer(text="To enable a log to be logged, run the enableLog <logName> command")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def aboutLogging(self, ctx):
        if not await pluginEnabled("logging", ctx.guild):
            return
        symbol = getPrefixx(self.client, ctx)
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        curr.execute(
            "SELECT message, channels, pins, jl, ronick, updat, role, emoji, voice, bans, invite FROM logs WHERE guild=" + str(
                ctx.guild.id) + ";")
        try:
            result = curr.fetchall()[0]
            result = list(result)
        except:
            result = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0 , 0]
        holder = "This is the Giorno bot logging configuration.\n\n Use "+symbol+"logs to find a list of logs that you can enable.\n\n Configuration:\n"
        for i in range(len(result)):
            if result[i] == 1:
                holder += ":white_check_mark: ``" + logs[i] + "``\n"
            else:
                holder += ":x: ``" + logs[i] + "``\n"
        holder += "\n"
        holder += "Run enableLog <log> or disableLog <log> to enable/disable a log."
        embed = discord.Embed(colour=discord.Colour.blue(), title="About Logging", description=holder)
        embed.set_thumbnail(
            url="https://static.wikia.nocookie.net/jjba/images/1/19/Giorno_Giovanna_Anime.png/revision/latest?cb=20200310175513")
        await ctx.send(embed=embed)

    @commands.command(aliases=["setLoggingChannel"])
    @commands.has_permissions(manage_channels=True)
    async def setLogChannel(self, ctx, chann:discord.TextChannel = None):
        if not await pluginEnabled("logging", ctx.guild):
            return
        if chann == None:
            channel = ctx.channel
        else:
            channel = chann
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        try:
            curr.execute(
                "SELECT * FROM logs WHERE guild=" + str(ctx.guild.id))
            results = curr.fetchall()[0]
            sql = "UPDATE logs SET channel = "+str(channel.id)+" WHERE guild="+str(ctx.guild.id)+";"
            curr.execute(sql)
            conn.commit()
        except:
            sql = ''' INSERT INTO logs(guild, channel, message, channels, pins, jl, ronick, updat, role, emoji, voice, bans, invite) 
                            VALUES(?,?,?,?,?,?,?,?, ?, ?, ?, ?, ?);'''
            curr.execute(sql, (ctx.guild.id, channel.id, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0 , 0))
            conn.commit()

        await ctx.send("Logging channel set to " + channel.mention+".")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def enableLog(self, ctx, *, log):
        if not await pluginEnabled("logging", ctx.guild):
            return
        if log.lower() not in logs:
            await ctx.send("Please enter a valid log. To view the different logs, try the aboutLogging command.")
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        index = len(realLogs)
        for i in range(len(realLogs)):
            if logs[i] == log.lower():
                index = i
                break
        try:
            sql = "UPDATE logs SET "+realLogs[index]+" = 1 WHERE guild=" + str(ctx.guild.id) + ";"
            curr.execute(sql)
            conn.commit()
            curr.execute(
                "SELECT * FROM logs WHERE guild=" + str(ctx.guild.id))
            results = curr.fetchall()[0]
        except:
            await ctx.send("Please set a logging channel.")
            return
        await ctx.send("Enabled the "+log+" log.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def disableLog(self, ctx, *, log):
        if not await pluginEnabled("logging", ctx.guild):
            return
        conn = create_connection(r"fullDB.db")
        curr = conn.cursor()
        if log.lower() not in logs:
            await ctx.send("Please enter a valid log. To view the different logs, try the aboutLogging command.")
            return
        index = len(realLogs)
        for i in range(len(realLogs)):
            if logs[i] == log.lower():
                index = i
                break
        try:
            sql = "UPDATE logs SET "+realLogs[index]+" = 0 WHERE guild=" + str(ctx.guild.id) + ";"
            curr.execute(sql)
            conn.commit()
            curr.execute(
                "SELECT * FROM logs WHERE guild=" + str(ctx.guild.id))
            results = curr.fetchall()[0]
            await ctx.send("Disabled the " + log + " log.")
        except:
            await ctx.send("Please set a logging channel first.")
