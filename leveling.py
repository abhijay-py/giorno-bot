import discord
from discord.ext import commands, tasks
from discord.utils import get
import datetime
from helper import pluginEnabled, create_connection, create_table, error_helper
import sqlite3
from disputils import *
import random
from sqlite3 import Error
import asyncio

lastMessages = {}

class Leveling(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        if not await pluginEnabled("leveling",  member.guild):
            return
        try:
            database = "levels.db"
            conn = create_connection(database)
            curr = conn.cursor()
            sql = "DELETE FROM levels WHERE guild="+str(member.guild.id)+" AND user=" + str(member.id)
            curr.execute(sql)
            conn.commit()
        except:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await pluginEnabled("leveling", message.guild):
            return
        if message.content == "":
            return
        if message.author.bot:
            return
        try:
            x = lastMessages[message.guild.id]
        except:
            lastMessages[message.guild.id] = {}
        database = "levels.db"
        conn = create_connection(database)
        curr = conn.cursor()
        try:
            curr.execute("SELECT * FROM levels WHERE user=" + str(message.author.id) + " AND guild="+str(message.guild.id))
            results = curr.fetchall()[0]
            level = results[3]
            xp = results[4]
            messages = results[5]

        except:
            level = 0
            xp = 0
            messages = 0
        if level == 0:
            level = 1
            try:
                await message.channel.send("GG " + message.author.mention + ", you advanced to level 1!")
            except:
                error_helper(message.channel, True)
                return
        try:
            if (lastMessages[message.guild.id][message.author.id] + datetime.timedelta(seconds=30) < message.created_at):
                lastMessages[message.guild.id][message.author.id] = message.created_at
                xp += random.randint(1, 10)
            messages += 1
        except:
            lastMessages[message.guild.id][message.author.id] = message.created_at
            xp  += random.randint(1, 10)
            messages += 1
        if xp > (level - 1) * 125 + 250 * level + ((1.1*(level))**2)//10 * 10 and level != 0:
            level += 1
            try:
                await message.channel.send("GG " + message.author.mention + ", you advanced to level " + str(level) + "!")
            except:
                error_helper(message.channel, True)
                return
        try:
            curr.execute(
                "SELECT * FROM levels WHERE user=" + str(message.author.id) + " AND guild=" + str(message.guild.id))
            results = curr.fetchall()[0]
            sql = "UPDATE levels SET level="+str(level)+", xp="+str(xp)+", messages="+str(messages)+" WHERE user="+str(message.author.id)+" AND guild="+str(message.guild.id)+";"
            curr.execute(sql)
        except:
            task_1 = (message.guild.id, message.author.id, level, xp, messages)
            sql = ''' INSERT INTO levels(guild, user, level, xp, messages) 
                                     VALUES(?,?,?,?,?) '''
            curr.execute(sql, task_1)
        conn.commit()

    @commands.command(aliases=["levels", "lb"])
    async def leaderboard(self, ctx):
        if not await pluginEnabled("leveling", ctx.guild):
            return
        database = "levels.db"
        conn = create_connection(database)
        curr = conn.cursor()
        sql = "SELECT user, level, xp, messages FROM levels WHERE guild="+str(ctx.guild.id)+" ORDER BY xp DESC;"
        curr.execute(sql)
        results = curr.fetchall()
        embeds = []
        title = ""
        lastIndex = 0
        offset = 0
        embed = discord.Embed()
        for i in range(len(results)):
            if (i  - offset) % 7  == 0:
                if i != 0:
                    embeds.append(embed)
                embed = discord.Embed(title="Leaderboard Page "+str(i//7 + 1), colour=discord.Colour.blue(), width=1000)
            if self.client.get_user(int(results[i][0])) == None or ctx.guild.get_member(int(results[i][0])) == None:
                database = "levels.db"
                conn = create_connection(database)
                curr = conn.cursor()
                sql = "DELETE FROM levels WHERE guild=" + str(ctx.guild.id) + " AND user=" + str(results[i][0])
                curr.execute(sql)
                conn.commit()
                offset +=1
                continue
            results[i] = list(results[i])
            if results[i][3] >= 1100:
                results[i][3] = results[i][3] // 100
                results[i][3] = results[i][3] / 10
                results[i][3] = str(results[i][3]) + "k"
            embed.add_field(name=str(i + 1-offset) + ". " + self.client.get_user(int(results[i][0])).display_name,
                            value="Level: " + str(results[i][1]) + ", Messages Sent: " +
                                  str(results[i][3]), inline=False)
            if i == len(results)-1:
                embeds.append(embed)
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command()
    async def rank(self, ctx, *, member:discord.Member = None):

        if not await pluginEnabled("leveling", ctx.guild):
            return
        if member == None:
            members = ctx.author
        else:
            members = member
        database = "levels.db"
        conn = create_connection(database)
        curr = conn.cursor()
        sql = "SELECT id, user FROM levels WHERE guild="+str(ctx.guild.id)+" ORDER BY xp DESC;"
        curr.execute(sql)
        leaderboard = curr.fetchall()
        sql = "SELECT id, level, xp, messages FROM levels WHERE guild=" + str(ctx.guild.id) + " AND user="+str(members.id)
        curr.execute(sql)
        id, level, xp, messages = curr.fetchall()[0]
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_thumbnail(url = ctx.guild.icon_url)
        embed.set_author(name=members.display_name, icon_url=members.avatar_url)
        rank = "N/A"
        offset = 0
        for i in range(len(leaderboard)):
            if self.client.get_user(int(leaderboard[i][1])) == None or ctx.guild.get_member(int(leaderboard[i][1])) == None:
                database = "levels.db"
                conn = create_connection(database)
                curr = conn.cursor()
                sql = "DELETE FROM levels WHERE guild=" + str(ctx.guild.id) + " AND user=" + str(leaderboard[i][1])
                curr.execute(sql)
                conn.commit()
                offset +=1
                continue
            if id == leaderboard[i][0]:
                rank = i+1
                break
        embed.add_field(name="Rank:", value=str(rank), inline=True)
        embed.add_field(name="Level:", value=str(level), inline=True)
        holder = (level - 1) * 125 + 250 * level + ((1.1*(level))**2)//10 * 10
        holder2 = (level - 2) * 125 + 250 * (level-1)+ ((1.1*(level-1))**2)//10 * 10
        holder -= holder2
        holder = int(holder)
        xp -= holder2
        xp = int(xp)
        if holder > 10000:
            holder = holder//100
            holder = holder/10
            holder = str(holder)+"k"
        if xp > 10000:
            xp = xp//100
            xp = xp/10
            xp = str(xp)+"k"
        embed.add_field(name="Experience:", value=str(xp) + "/" + str(holder) + " xp", inline=False)
        await ctx.send(embed=embed)

    @leaderboard.error
    @rank.error
    async def levels_error(self, ctx, error):
        if (await error_helper(ctx, True)):
            return
