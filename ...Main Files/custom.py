import discord
from discord.ext import commands, tasks
from discord.utils import get
from helper import pluginEnabled
import pytz
import datetime
import asyncio
import random

programmerID = 721170371826679841
flirts = ["Are you a cornfield? Cause I'm stalking you, ",
          "Are you a 30 degree angle, because you're aCUTIE, ",
          "Are you a 90 degree angle cause I think you're the RIGHT one for me, ",
          "Are you a book? Cause I'm checking you out, ",
          "Are you from Tennessee, cause you're the only 10 I see, ",
          "I lost my teddy bear, will you sleep with me instead, ",
          "Are you a transformer? Cause you're Optimus fine, ",
          "Are you a shovel? Because I'm digging you, ",
          "Do you work at subway? Because I want to share a footlong, ",
          "If you were a vegetable you'd be a cute-cumber, ",
          "Are you Little Cesars? Because you're hot and I'm ready, ",
          "Those are some nice legs. What time do they open, ",
          "Are you Medusa? Because you make me rock hard, "]

insults =  ["You're an uneducated sack of garbage ",
            "You're a waste of oxygen ",
            "I'd prefer a battle of wits but you appear unarmed ",
            ", you absolute buffoon!",
            "It is impossible to underestimate you ",
            "Brains aren't everything. In your case, they're nothing, ",
            "Your words are a waste of storage on discord's servers, "]
inviteInfo = []
insultsIndexs = [3]

async def lastMessage(users_id: int, channel):
    oldestMessage = None
    newMessageFound = False
    async for i in channel.history():
        if i.author.id == users_id:
            if not newMessageFound:
                newMessageFound = True
            else:
                oldestMessage = i
                break
    return oldestMessage

async def last(users_id: int, channel):
    newMessage = None
    try:
        async for i in channel.history():
            if i.author.id == users_id:
                return i.created_at
    except:
        pass
    return newMessage

class Custom(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def start(self, ctx):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 741466814885658665:
            return
        self.client.loop.create_task(self.daily_react())
        await ctx.send("Started daily reactions.")

    @commands.command(aliases=["best_girl"])
    async def bestGirl(self, ctx):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 778381933628620852:
            return
        await ctx.send("You talking abt 02?")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await pluginEnabled("custom", message.guild):
            return
        if message.guild.id == 741466814885658665:
            timezone = pytz.timezone("US/Central")
            if message.channel.id == 763565878661873694:
                previousMessage = await lastMessage(message.author.id, message.channel)
                if previousMessage == None:
                    return
                previousMessage = previousMessage.created_at
                lastMessageDT = previousMessage.replace(tzinfo=timezone)
                now = datetime.datetime.now(timezone)
                if now.year == lastMessageDT.year and now.month == lastMessageDT.month and (
                        now.day == lastMessageDT.day and lastMessageDT.hour >= 6) or (
                        now.day == (lastMessageDT - datetime.timedelta(days=1)).day and lastMessageDT.hour < 6):
                    await message.delete()
                return
            elif message.channel.id == 775459817362817084:
                pMessage = await lastMessage(message.author.id, message.channel)
                if pMessage == None:
                    return
                await message.delete()
                return
    @commands.command(aliases = ["02"])
    async def zeroTwo(self, ctx):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 778381933628620852:
            return
        await ctx.send("You talking abt the #1 waifu?")

    @commands.command(aliases=["best_girl"])
    async def bestGirl(self, ctx):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 778381933628620852:
            return
        await ctx.send("You talking abt 02?")

    @commands.command()
    async def mai(self, ctx):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 778381933628620852:
            return
        await ctx.send("You talking abt the #2 waifu?")

    async def daily_react(self):
        dailyGifs = ["https://cdn.discordapp.com/attachments/725015549020471346/760850539876843530/walter-1.mp4",
                     "https://cdn.discordapp.com/attachments/741466814885658669/798707066226999326/video0.mp4",
                     "https://cdn.discordapp.com/attachments/725015549020471346/760850539876843530/walter-1.mp4",
                     "https://tenor.com/view/monkey-sinners-thursday-gif-18797091",
                     "https://youtu.be/r3XKylB1tIM",
                     "https://cdn.discordapp.com/attachments/741466814885658669/774769621667414026/5fa726381ece8927103602.gif",
                     "https://cdn.discordapp.com/attachments/741466814885658669/774767336019460156/5fa72419293ed107289741.gif"]
        restarted = True
        timezone = pytz.timezone("US/Central")
        schedule_time = datetime.datetime(year=2020, month=11, day=8, hour=00, minute=10, second=00,
                                          microsecond=000000, tzinfo=timezone)
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            now = datetime.datetime.now(timezone)
            if schedule_time <= now:
                if not restarted:
                    guild = self.client.get_guild(741466814885658665)
                    for channel in guild.channels:
                        if channel.id == 741466814885658669:
                            await channel.send(dailyGifs[now.weekday()])
                schedule_time += datetime.timedelta(days=1)
                if schedule_time > now:
                    restarted = False
            await asyncio.sleep(20)

    @commands.command(aliases=["diss", "bully", "roast"])
    async def insult(self, ctx, member: discord.Member):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 403253647435104256:
            return
        if member.id == ctx.author.id:
            await ctx.send("Stop that. Get some help.")
            return
        randomPicker = random.randint(0, len(insults) - 1)
        if randomPicker in insultsIndexs:
            await ctx.send(member.mention + insults[randomPicker])
        else:
            await ctx.send(insults[randomPicker] + member.mention + ".")

    @commands.command()
    async def flirt(self, ctx, member: discord.Member):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 403253647435104256:
            return
        randomPicker = random.randint(0, len(flirts) - 1)
        await ctx.send(flirts[randomPicker] + member.mention + ".")



    @commands.command()
    @commands.has_role("Cow Herders")
    async def pen(self, ctx, member:discord.Member):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 403253647435104256:
            return
        role = get(member.guild.roles, name="cow pen")
        await member.add_roles(role)
        await ctx.send(f'{member.mention} was penned!')

    @commands.command()
    @commands.has_role("Cow Herders")
    async def unpen(self, ctx, member: discord.Member):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 403253647435104256:
            return
        role = get(member.guild.roles, name="cow pen")
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} was unpenned!')

    @commands.command()
    async def up(self, ctx):
        if not await pluginEnabled("custom", ctx.guild):
            return
        if ctx.guild.id != 403253647435104256:
            return
        if ctx.author.id != programmerID:
            return
        role = get(ctx.guild.roles, name="cow pen")
        await ctx.author.remove_roles(role)
        await ctx.send(f'{ctx.author.mention} was unpenned!')

    @commands.command()
    async def tamsUpdate(self, ctx):
        if not await pluginEnabled("custom",ctx.guild):
            return
        if ctx.guild.id != 403253647435104256:
            return
        if ctx.author.id != programmerID and ctx.author.id != 358408465665884160:
            return
        role = get(ctx.guild.roles, name="CO'22")
        if role == None:
            await ctx.guild.create_role(name="CO'22", color=discord.Colour.green())
            role = get(ctx.guild.roles, name="CO'22")
        role2 = get(ctx.guild.roles, name="CO'23")
        tams =  get(ctx.guild.roles, name="TAMS")
        x = False
        for i in ctx.guild.members:
            if tams in i.roles and not role2 in i.roles:
                try:
                    await i.add_roles(role)
                except:
                    x = True
                    break
        if x:
            await ctx.send(ctx.guild.owner.mention+" give the bot perms smh")
            return

        overwrite = discord.PermissionOverwrite(view_channel=False)
        overwrite2 = discord.PermissionOverwrite(view_channel=True)
        for channel in ctx.guild.channels:
            if channel.id == 761417269800075275:
                await channel.set_permissions(role2, overwrite=overwrite)
                await channel.set_permissions(tams, overwrite=overwrite)
                await channel.set_permissions(role, overwrite=overwrite2)
        await ctx.send("TAMS student data was updated.")