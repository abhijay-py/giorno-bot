import discord
import random
import smtplib
import os
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
import sqlite3
from sqlite3 import Error
import datetime as dt
import pytz
from weeb import *
from mod import *
from wal import *
from util import *
from custom import *
from helper import *
from music import *
from leveling import *

def getPrefix(client, message):
    if message.guild == None:
        return ["~", "-"]
    try:
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT guild,prefix FROM prefixes;")
        results = curr.fetchall()
        guilds = [int(i[0]) for i in results]
        index = guilds.index(message.guild.id)
        if results[index][1] == "~":
            return ["~", "-"]
    except:
        return ["~", "-"]
    return results[index][1]

beforeReady = True
programmerID = os.environ['PROGRAMMERID']
botID = 785687696781737995
logID = 820117325109919754
token = os.environ['TOKEN']
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=getPrefix, intents=intents, case_insensitive=True)
client.remove_command("help")
client.load_extension("jishaku")
pluginList = [["moderation", "mod"],
              ["join/leave messages", "join", "leave", "join messages", "leaving messages", "welcome",
               "welcome messages", "welcome and leaving", "welcome and leaving messages"],
              ["utility", "util"], ["custom"], ["music"], ["leveling", "levels"]]
messageBACK = [718234876075311245, programmerID]
messaged = []
client.add_cog(Moderation(client))
client.add_cog(WelcomeAndLeaving(client))
client.add_cog(Utility(client))
client.add_cog(Custom(client))
client.add_cog(Weeb(client))
client.add_cog(Music(client))
client.add_cog(Leveling(client))


def guildLeave(guild):
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    sql = '''DELETE FROM prefixes WHERE guild=''' + str(guild)
    curr.execute(sql)
    conn.commit()
    sql = '''DELETE FROM plugins WHERE guild=''' + str(guild)
    curr.execute(sql)
    conn.commit()
    try:
        sql = '''DELETE FROM joined WHERE guild=''' + str(guild)
        curr.execute(sql)
        conn.commit()
    except:
        pass

    try:
        sql = '''DELETE FROM leave WHERE guild=''' + str(guild)
        curr.execute(sql)
        conn.commit()
    except:
        pass

    try:
        sql = '''DELETE FROM warns WHERE guild=''' + str(guild)
        curr.execute(sql)
        conn.commit()
    except:
        pass

    try:
        sql = '''DELETE FROM levels WHERE guild=''' + str(guild)
        curr.execute(sql)
        conn.commit()
    except:
        pass

def update():
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute("SELECT guild FROM plugins;")
    result = curr.fetchall()
    guilds = [int(i[0]) for i in result]
    j = 0
    if (len(list(result)) == len(list(client.guilds))):
        pass
    else:
        for guild in client.guilds:
            if guild.id not in guilds:
                client.dispatch("guild_join", guild)
                j += 1
        for i in guilds:
            guild = client.get_guild(i)
            if guild == None:
                guildLeave(i)
                j += 1
    return j

# EVENTS
async def status():
    while True:
        await asyncio.sleep(30)
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="~help | " + str(
                len(list(client.guilds))) + " Servers"), status=discord.Status.idle)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="~help | " + str(
        len(list(client.guilds))) + " Servers"), status=discord.Status.idle)
    client.loop.create_task(status())
    giveClient(client)
    print('Bot is ready!')
    embed = discord.Embed(color=discord.Colour.blue(), title=":white_check_mark: Giorno Status - Online :white_check_mark:", description="The bot has come online.")
    embed.set_thumbnail(
        url="https://giantbomb1.cbsistatic.com/uploads/scale_small/46/462814/3181186-8832722279-af535.jpg")
    now = dt.datetime.now(tz=pytz.timezone("US/Central"))
    embed.set_footer(text=now.strftime("%b %d, %Y %I:%M %p"))
    await client.get_channel(logID).send(embed=embed)

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild:
        await client.process_commands(message)
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute("SELECT user FROM optout;")
    result = curr.fetchall()
    results = [i[0] for i in result]
    try:
        owners = [guild.owner.id for guild in client.guilds]
    except:
        return
    if not message.guild and message.author.id != botID:
        if message    .author.id not in messaged:
            messaged.append(message.author.id)
        if message.author.id in messageBACK and message.content[:4] == "TO: ":
            try:
                number = int(message.content[4:22])
                if number not in messaged:
                    return
            except:
                return

            user = client.get_user(number)
            await user.send("From: Giorno Support Team\nSupport Member: "+str(message.author)+"\n"+message.content[22:])
            await message.author.send("Sucessfully sent message to "+str(user)+".")
            return
        if message.content == "STOP" and message.author.id in owners and message.author.id not in results:
            await message.author.send("You have now opted out of bot-wide messages. We recommend you join our support server for announcments on the bot: https://discord.gg/YC9h8t3Kxb")
            sql = ''' INSERT INTO optout(user) VALUES(?);'''
            tupl = tuple([message.author.id])
            curr.execute(sql, tupl)
            conn.commit()
            return
        elif message.content == "STOP" and message.author.id in owners and message.author.id in results:
            await message.author.send("You are already opted out of bot-wide messages. Reply with START to opt back in.")
            return
        elif message.content == "START" and message.author.id in owners and message.author.id in results:
            await message.author.send(
                "You have now opted into bot-wide messages.")
            curr.execute("DELETE FROM optout WHERE user="+str(message.author.id))
            conn.commit()
            return
        elif message.content == "START" and message.author.id in owners and message.author.id not in results:
            await message.author.send(
                "You are already opted into bot-wide messages.")
            return
        elif message.author.id in messageBACK:
            return
        await emailing(message.content, message.author, client)

@client.event
async def on_guild_join(guild):
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    sql = ''' INSERT INTO plugins(guild, plugin1, plugin2, plugin3, plugin4, plugin5, plugin6) 
                VALUES(?,?,?,?,?,?,?);'''
    curr.execute(sql, (guild.id, 0, 0, 0, 0, 0, 0))
    conn.commit()
    sql = ''' INSERT INTO prefixes(guild, prefix) 
                                        VALUES(?,?);'''
    curr.execute(sql, (guild.id, "~"))
    conn.commit()
    update()

@client.event
async def on_guild_leave(guild):
    guild_leave(guild.id)
    update()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass in all required arguments correctly.")
    elif isinstance(error, commands.MissingPermissions):
        pass
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please pass in all required arguments correctly.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("Sorry, commands can only be used in servers at this time.")
    elif str(error) == "Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions":
        pass
    elif str(error) == "":
        pass
    else:
        embed = discord.Embed(color=discord.Colour.blue(), title=":warning: Giorno Status - Error :warning:",
                              description="`"+str(error)+"`")
        embed.set_thumbnail(
            url="https://giantbomb1.cbsistatic.com/uploads/scale_small/46/462814/3181186-8832722279-af535.jpg")
        now = dt.datetime.now(tz=pytz.timezone("US/Central"))
        embed.set_footer(text=now.strftime("%b %d, %Y %I:%M %p"))
        await client.get_channel(logID).send(embed=embed)
        await client.get_channel(logID).send(embed=embed)
        raise error
# HELP COMMANDS
@client.command(pass_context=True)
async def help(ctx, *, category: str = "all"):
    guild = ctx.guild
    embed = discord.Embed(colour=discord.Colour.blue(),
                          description="[Join the support discord!](https://discord.gg/YC9h8t3Kxb '" + "Join the support discord!" + "')""")
    user = client.get_user(botID)
    embed.set_author(name="Giorno Help Menu", icon_url=user.avatar_url)
    embed.set_footer(text="To edit configuration, run the plugins command. Try help <category> to view specific help on a category.")
    if category == "all":
        embed.add_field(name="Weeb Commands",
                        value="`anime`, `manga`, `animeList`, `mangaList`, `animeStats`, `mangaStats`",
                        inline=False)
        if await pluginEnabled("utility", ctx.guild):
            embed.add_field(name="Utility Commands", value="`randomNum`, `coinFlip`, `pfp`, `solve`, `derivative`, `iintegral`", inline=False)
        if await pluginEnabled("moderation", ctx.guild):
            embed.add_field(name="Moderation Commands",
                            value="`mute`, `unmute`, `clear`, `kick`, `ban`, `unban`, `slowmode`, `warn`, `infractions`, `removeWarn`",
                            inline=False)
        if await pluginEnabled("join/leave messages", ctx.guild):
            embed.add_field(name="Join/Leave Commands", value="`setJoinMessage`, `setLeaveMessage`", inline=False)
        if await pluginEnabled("music", ctx.guild):
             embed.add_field(name="Music Commands", value="`join`, `leave`, `pause`, `play`, `stop`, `skip`, `queue`, `shuffle`, `loop`, `back`", inline=False)
        if await pluginEnabled("leveling", ctx.guild):
            embed.add_field(name = "Leveling Commands", value = "`rank`, `leaderboard`")
        embed.add_field(name="Other Commands",
                        value="`help`, `about`, `plugins`, `enablePlugin`, `disablePlugin`, `links`, `setPrefix`",
                        inline=False)
        await ctx.send(embed=embed)
        return
    elif (
            category == "Util" or category == "Utility" or category == "util" or category == "utility") and await pluginEnabled(
            "utility", ctx.guild):
        holder = """**randomNum <lowerBound> <upperBound>** - outputs a random number. \n **coinFlip** - flips a coin\n **pfp <user>** - displays the users pfp. Displays your pfp, if no user.\n\nFor the following commands, make sure to put a * between every term of the function.\n\n**d <var> <function>** - calculates the derivative of the given function. \n**ii <x> <function>** - takes the indefinite integral of the function.\n**solve <expression>** - solves the expression if it contains only mod, powers, and the 4 basic operations."""
        embed.add_field(name="Utility Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    elif category == "Weeb" or category == "weeb":
        holder = """**anime <animeName>**  - returns info about the anime.\n**manga <mangaName>** - returns info about the manga.\n**animeList <MAL username>** - returns the user's animelist\n**mangaList <MAL username>** - returns the user's mangalist \n**animeStats <MAL username>** - returns the user's anime stats\n**mangaStats <MAL username>** - returns the user's manga stats"""
        embed.add_field(name="Weeb Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    elif (
            category == "Mod" or category == "mod" or category == "moderation" or category == "Moderation") and await pluginEnabled(
            "moderation", ctx.guild):
        holder = """**mute <user>** - mutes the specified user\n**unmute <user>** - unmutes the specified user\n**clear <n>** - clears the last n messages\n**kick <user>** - kicks the specified user\n**ban <user>** - bans the specified user\n**unban <user>** - unbans the specified user\n**warn <user> <reason>** - warns the user\n**infractions <user>** - views the specified user's warnings\n**removeWarn <user> <n>** - removes the user's nth warning.\n**slowmode <n>** - enables a slowmode of n seconds.\n**warn <user> <reason>** - warns a user due to a specified reason. None is the reason if not specified.\n**infractions <user>** - views the warnings of a user.\n**removeWarn <user> <n>** - removes the nth warn for the specified user."""
        embed.add_field(name="Moderation Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    elif (category.lower() in pluginList[1]) and await pluginEnabled("join/leave messages", ctx.guild):
        holder = "**setJoinMessage <channel> <message>** - sets the join message. \nUse {} if you want to tag the joining member.\n **setLeaveMessage <channel> <message>** - sets the join message. \nUse {} if you want to tag the leaving member."
        embed.add_field(name="Leveling Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    elif (category == "Music" or category == "music") and await pluginEnabled("music", ctx.guild):
        holder = "**join** - bot joins your vc. \n **leave** - bot leaves your vc. \n**queue** <n> - displays the next n songs in queue (default is 10).\n **play <song name>** - plays the song, if none provided, plays the next song in queue or resumes music. \n **shuffle** - shuffles the queue\n**skip** - skips to the next song in the queue.\n**back** - goes back to the previous song in the queue.\n**stop** - clears the queue and stops playing music.\n**pause** - pauses the music.\n**loop <none/1/all>** - loops the queue the corresponding amount of times."
        embed.add_field(name="Music Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    elif (category.lower() in pluginList[5] and await pluginEnabled("leveling", ctx.guild)):
        holder = "**rank <user>** - shows you the rank card of the specified user. If none is specified, pulls up your rank card.\n **leaderboard** - pulls up the server leaderboard."
        embed.add_field(name="Leveling Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    elif category == "other" or category == "Other":
        holder = """**help <category>** - pulls up this help menu. \n**about** - sends a message with details about the bot.\n**plugins** - sends a list of the available plugins\n**enablePlugin <plugin>** - enables the specified plugin.\n**disablePlugin <plugin>** - disables the specified plugin.\n**links** - outputs important links for the bot.\n**setPrefix <prefix>** - sets the server prefix to the prefix inputted."""
        embed.add_field(name="Other Commands", value=holder, inline=False)
        await ctx.send(embed=embed)
        return
    await ctx.send("Please enter a valid category.")


@client.command(aliases=["info", "about"])
async def information(ctx):
    symbol = getPrefix(client, ctx)
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute("SELECT plugin1, plugin2, plugin3, plugin4, plugin5, plugin6 FROM plugins WHERE guild=" + str(ctx.guild.id) + ";")
    result = curr.fetchall()[0]
    result = list(result)
    try:
        symbol = symbol[0]
    except:
        pass
    holder = "This is the Giorno bot. Use "+symbol+"help to find a list of commands.\n\n" + "The bot is currently running v2.7.6\n\nConfiguration:\n"
    for i in range(len(result)):
        if result[i] == 1:
            holder += ":white_check_mark: `" + pluginList[i][0] + "`\n"
        else:
            holder += ":x: `" + pluginList[i][0] + "`\n"
    holder += "\n"
    holder += "Developer: AA\n" + "Discord: \n\n" + "[Join the support discord!](https://discord.gg/YC9h8t3Kxb '" + "Join the support discord!" + "')"
    embed = discord.Embed(colour=discord.Colour.blue(), title="About", description=holder)
    embed.set_thumbnail(
        url="https://static.wikia.nocookie.net/jjba/images/1/19/Giorno_Giovanna_Anime.png/revision/latest?cb=20200310175513")
    await ctx.send(embed=embed)


@client.command(aliases=["link"])
async def links(ctx):
    holder = "[Join the support discord server!](https://discord.gg/YC9h8t3Kxb '" + "Join the support discord!" + "')\n\n"
    holder += "[Invite the bot to your server!](https://discord.com/api/oauth2/authorize?client_id=785687696781737995&permissions=2420113142&redirect_uri=https%3A%2F%2Fdiscord.com%2Fapi%2Foauth2%2Fauthorize%3Fclient_id%3D785687696781737995%26permissions%3D1408761718%26redirect_uri%3Dhttps%253A%252F%252Fdiscord.com%252Fapi%252Foauth2%252Fauthorize%253Fclient_id&scope=bot '" + "Add the Giorno Bot!" + "')\n\n"
    holder += "[Vote for the bot on top.gg!](https://top.gg/bot/785687696781737995/vote '" + "Vote for the bot on top.gg!" + "')\n\n"
    embed = discord.Embed(color=discord.Colour.blue(), title="Important Links", description=holder)
    await ctx.send(embed=embed)


@client.command()
async def plugins(ctx):
    embed = discord.Embed(color=discord.Colour.blue(), title="Plugins",
                          description="`Moderation`, `Join/Leave Messages`, `Utility`, `Music`, `Custom`, `Leveling`")
    embed.set_footer(text="To enable a plugin, run the enablePlugin <pluginName> command.")
    await ctx.send(embed=embed)


@client.command(aliases=["enable_plugin"])
@commands.has_permissions(manage_guild=True)
async def enablePlugin(ctx, *, plugin):
    index = -1
    for i in range(len(pluginList)):
        if plugin.lower() in pluginList[i]:
            index = i
            break
    if index == -1:
        await ctx.send("There is no plugin named " + plugin.lower() + ".")
        return
    index += 1
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute("UPDATE plugins SET plugin" + str(index) + " = 1 WHERE guild=" + str(ctx.guild.id) + ";")
    conn.commit()
    await ctx.send("Added the " + pluginList[index - 1][0] + " plugin.")


@client.command(aliases=["disable_plugin"])
@commands.has_permissions(manage_guild=True)
async def disablePlugin(ctx, *, plugin):
    index = -1
    for i in range(len(pluginList)):
        if plugin.lower() in pluginList[i]:
            index = i
            break
    if index == -1:
        await ctx.send("There is no plugin named " + plugin.lower() + ".")
        return
    index += 1
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute("UPDATE plugins SET plugin" + str(index) + " = 0 WHERE guild=" + str(ctx.guild.id) + ";")
    conn.commit()
    await ctx.send("Removed the " + pluginList[index - 1][0] + " plugin.")


@client.command(aliases=["change_prefix", "set_prefix", "setPrefix"])
@commands.has_permissions(manage_guild=True)
async def changePrefix(ctx, prefix: str):
    if ctx.guild == None:
        return
    conn = create_connection("fullDB.db")
    curr = conn.cursor()
    sql = "UPDATE prefixes SET prefix='"+prefix+"' WHERE guild=" + str(ctx.guild.id)
    curr.execute(sql)
    conn.commit()
    await ctx.send("Updated the server prefix to " + prefix)

@client.command(aliases=["close"])
async def shutdown(ctx):
    if ctx.author.id != programmerID:
        return
    print("Bot shutting off!")
    await ctx.send("Bot shutting off!")
    await asyncio.sleep(delay=2)
    for guild in client.guilds:
        try:
            await guild.voice_client.disconnect()
        except:
            continue
    await ctx.send("Bot closed.")
    embed = discord.Embed(color=discord.Colour.blue(), title=":stop_sign: Giorno Status - Shutting Down :stop_sign:",
                          description="The bot has shutdown.")
    embed.set_thumbnail(
        url="https://giantbomb1.cbsistatic.com/uploads/scale_small/46/462814/3181186-8832722279-af535.jpg")
    now = dt.datetime.now(tz=pytz.timezone("US/Central"))
    embed.set_footer(text=now.strftime("%b %d, %Y %I:%M %p"))
    await client.get_channel(logID).send(embed=embed)
    await client.close()
    print("Bot closed.")

@client.command(aliases=["msg"])
async def message(ctx, *, message):
    if ctx.author.id != programmerID:
        return
    messaged = []
    count = 0
    minusCount = 0
    conn = create_connection(r"fullDB.db")
    curr = conn.cursor()
    curr.execute("SELECT user FROM optout;")
    result = curr.fetchall()
    results = [i[0] for i in result]
    for guild in client.guilds:
        if guild.owner.id not in messaged and guild.owner.id not in results:
            try:
                await guild.owner.send(message+"\n This is a bot wide message. To opt out, reply with STOP. You can reopt in anytime by sending START.\n We recommend you either stay opted in or join our support server: https://discord.gg/YC9h8t3Kxb")
            except:
                count -= 1
                minusCount +=1
            count += 1
            messaged.append(guild.owner.id)
    await ctx.send("Sent message to " + str(count) + " owners and failed to send messages to " + str(minusCount) +" owners.")

@client.command(aliases=["update", "update_offline"])
async def updateOffline(ctx):
    if ctx.author.id != programmerID:
        return
    await ctx.invoke(client.get_command("start"))
    j = update()
    await ctx.send("Updated "+str(j)+" guilds.")

@client.command(aliases=["guilds"])
async def listGuilds(ctx):
    if ctx.author.id != programmerID:
        return
    embeds = []
    guilds = list(client.guilds)
    embed = discord.Embed()
    description = ""
    for i in range(len(guilds)):
        if (i) % 10 == 0:
            if i != 0:
                embed = discord.Embed(title="Guilds Page " + str(i // 10), description=description,
                                      colour=discord.Colour.blue(),
                                      width=1000)
                description = ""
                embeds.append(embed)
        description += str(i+1) +". "+str(guilds[i])+ "\n"
        if i == len(guilds) - 1:
            embed = discord.Embed(title="Guilds Page " + str(i // 10 + 1), description=description,
                                  colour=discord.Colour.blue(),
                                  width=1000)
            embeds.append(embed)
    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()



@help.error
@links.error
@information.error
@plugins.error
@enablePlugin.error
@disablePlugin.error
@changePrefix.error
async def general_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        return
    if (await error_helper(ctx, True)):
        return

try:
    client.run(token)
except:
    pass
