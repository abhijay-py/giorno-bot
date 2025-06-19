import discord
import random
import smtplib
import os
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
import sqlite3
import smtplib
from sqlite3 import Error

pluginList = [["moderation", "mod"],
              ["join/leave messages", "join", "leave", "join messages", "leaving messages", "welcome",
               "welcome messages", "welcome and leaving", "welcome and leaving messages"],
              ["utility", "util"], ["custom"], ["music"], ["leveling", "levels"]]

EMAIL_ADDRESS = "zerotwobotdiscord@gmail.com"
PASSWORD = "Darling1602"
botID = 785687696781737995
programmerID = 721170371826679841
messageBACK = [718234876075311245, programmerID]
client = []
def giveClient(cliented):
    client.append(cliented)

def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

async def pluginEnabled(plugin, guild):
    if guild == None:
        return
    index = -1
    for i in range(len(pluginList)):
        if plugin.lower() in pluginList[i]:
            index = i
            break
    if index == -1:
        return
    index += 1
    database = r"fullDB.db"
    conn = create_connection(database)
    with conn:
        curr = conn.cursor()
        curr.execute("SELECT plugin1, plugin2, plugin3, plugin4, plugin5, plugin6 FROM plugins WHERE guild="+str(guild.id))
        try:
            result = curr.fetchall()[0]
        except:
            await client[len(client)-1].get_user(programmerID).send("Please update guilds.")
            return
        if result[index-1] == 0:
            return False
        return True

async def error_helper(ctx, inCommandError):
    try:
        async for message in ctx.channel.history(limit=1):
            if message.author.id == botID:
                return
        await ctx.send(embed=discord.Embed(colour=discord.Colour.blue()))
        await ctx.channel.purge(limit=1)
        return False
    except:
        try:
            await ctx.send(".")
            await ctx.channel.purge(limit=1)
            if (inCommandError):
                await ctx.author.send("Please give the Giorno Bot the permission to send embeds.")
        except:
            if (inCommandError):
                try:
                    await ctx.author.send("Please give the Giorno Bot the permission to send messages.")
                except:
                    pass
        return True

async def emailing(message, author, client):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        subject = "Giorno DMS"
        body = str(author) + " sent: " + message +"\n"+"ID: "+str(author.id)

        msg = f'Subject: {subject}\n\n{body}'
        try:
            smtp.login(EMAIL_ADDRESS, PASSWORD)
        except:
            for i in messageBACK:
                await client.get_user(i).send(body)
            return

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)