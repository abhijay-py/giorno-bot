import discord
from discord.ext import commands, tasks
from discord.utils import get
from helper import pluginEnabled, create_connection, create_table, error_helper
import sqlite3
from sqlite3 import Error

class WelcomeAndLeaving(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not await pluginEnabled("join/leave messages", member.guild):
            return
        try:
            database = "fullDB.db"
            conn = create_connection(database)
            curr = conn.cursor()
            curr.execute("SELECT * FROM joined WHERE guild=" + str(member.guild.id) + ";")
            results = curr.fetchall()[0]
            channel = results[2]
            message = results[3]
            channel = self.client.get_channel(channel)
            message = message.replace("{}", member.mention)
            await channel.send(message)
        except:
            try:
                if (await error_helper(channel, True)):
                    return
            except:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not await pluginEnabled("join/leave messages", member.guild):
            return
        try:
            database = "fullDB.db"
            conn = create_connection(database)
            curr = conn.cursor()
            curr.execute("SELECT * FROM leave WHERE guild=" + str(member.guild.id) + ";")
            results = curr.fetchall()[0]
            channel = results[2]
            message = results[3]
            channel = self.client.get_channel(channel)
            message = message.replace("{}", "**"+str(member)+"**")
            await channel.send(message)
        except:
            try:
                if (await error_helper(channel, True)):
                    return
            except:
                pass

    @commands.command(aliases=["set_join_message"])
    @commands.has_permissions(manage_channels=True)
    async def setJoinMessage(self, ctx, channel:discord.TextChannel, *, message):
        if not await pluginEnabled("join/leave messages",ctx.guild):
            return
        database = "fullDB.db"
        conn = create_connection(database)
        curr = conn.cursor()
        sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS joined (
                                            id integer PRIMARY KEY,
                                            guild integer NOT NULL,
                                            channel integer NOT NULL,
                                            message text NOT NULL
                                    );"""
        create_table(conn, sql_create_tasks_table)
        try:
            sql = '''DELETE FROM joined WHERE guild=''' + str(ctx.guild.id)
            curr.execute(sql)
            conn.commit()
        except:
            pass
        sql = ''' INSERT INTO joined(guild, channel, message)
                  VALUES(?,?,?) '''
        curr.execute(sql, (ctx.guild.id, channel.id, message))
        conn.commit()
        await ctx.send("Updated the welcome message.")

    @commands.command(aliases=["set_leave_message"])
    @commands.has_permissions(manage_channels=True)
    async def setLeaveMessage(self, ctx, channel: discord.TextChannel, *, message):
        if not await pluginEnabled("join/leave messages", ctx.guild):
            return
        database = "fullDB.db"
        conn = create_connection(database)
        curr = conn.cursor()
        sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS leave (
                                            id integer PRIMARY KEY,
                                            guild integer NOT NULL,
                                            channel integer NOT NULL,
                                            message text NOT NULL
                                    );"""
        create_table(conn, sql_create_tasks_table)
        try:
            sql = '''DELETE FROM leave WHERE guild=''' + str(ctx.guild.id)
            curr.execute(sql)
            conn.commit()
        except:
            pass
        sql = ''' INSERT INTO leave(guild, channel, message)
                  VALUES(?,?,?) '''
        curr.execute(sql, (ctx.guild.id, channel.id, message))
        conn.commit()
        await ctx.send("Updated the leaving message.")

    @setLeaveMessage.error
    @setJoinMessage.error
    async def wal_error(self, ctx, error):
        if (await error_helper(ctx, True)):
            return