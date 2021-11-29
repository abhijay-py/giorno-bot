import discord
from discord.ext import commands, tasks
from discord.utils import get
from mal import *
from disputils import *
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from helper import error_helper

def retrieveTitles(user:str):
    req_limit = 300
    i = 0
    listOfAnime = []
    while True:
        req = requests.get(
            "https://myanimelist.net/animelist/" + user + "/load.json?offset=" + str(i) + "&limit=" + str(
                req_limit)).json()
        if req == []:
            break
        for anime in req:
            listOfAnime.append(anime)
        i += req_limit
    return listOfAnime

def retrieveTitlesManga(user:str):
    req_limit = 300
    i = 0
    listOfAnime = []
    while True:
        req = requests.get(
            "https://myanimelist.net/mangalist/" + user + "/load.json?offset=" + str(i) + "&limit=" + str(
                req_limit)).json()
        if req == []:
            break
        for anime in req:
            listOfAnime.append(anime)
        i += req_limit
    return listOfAnime

def retrieveAnimeProfile(user:str, anime):

    url = "https://myanimelist.net/profile/"+user
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    listed =soup.text.split("\n")
    animeIndex = -1
    mangaIndex = -1
    for i in range(len(listed)):
        if listed[i] == 'Anime Stats':
            animeIndex = i
        elif listed[i] == 'Manga Stats':
            mangaIndex = i
            break
    if anime:
        anime1 = listed[animeIndex+2:animeIndex+11]
    else:
        anime1 = listed[mangaIndex+2:mangaIndex+11]
    holder = []
    for i in range(len(anime1)):
        if i == 0:
            holder.append(anime1[i].split(" ")[1])
        elif i == 3:
            holder.append(anime1[i])
        elif i == 8:
            test = list(anime1[i])
            number = False
            j = 0
            while j < len(test):
                if test[j].isdigit():
                    number = True
                elif test[j] == ",":
                    del test[j]
                    j -= 1
                elif not test[j].isdigit() and number:
                    number = False
                    test[j] = " "
                else:
                    del test[j]
                    j -= 1
                j += 1
            holdered = ""
            for k in range(len(test)):
                if test[k] != " ":
                    holdered += test[k]
                else:
                    holder.append(holdered)
                    holdered = ""
    return holder


class Weeb(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command()
    async def anime(self, ctx, *, title:str):
        await ctx.trigger_typing()
        try:
            search = AnimeSearch(title)
        except ValueError:
            await ctx.send("Sorry, no results were found.")
            return

        result = search.results[0]
        anime = Anime(result.mal_id)
        generes = ""
        embed = discord.Embed(title = result.title, description=result.url,colour=discord.Colour.blue())
        embed.set_thumbnail(url= result.image_url)
        embed.add_field(name = "Status", value = anime.status, inline = True)
        embed.add_field(name = "Type", value = result.type, inline=True)
        if "Ecchi" in anime.genres or "Hentai" in anime .genres:
            await ctx.send("Please enter a non-Ecchi (non-NSFW) anime.")
            return
        for i in range(len(anime.genres)):
            if i != len(anime.genres)-1:
                generes += anime.genres[i]+", "
            else:
                generes += anime.genres[i]
        embed.add_field(name = "Genres", value = generes, inline = False)
        embed.add_field(name= "Synopsis", value=result.synopsis, inline=False)
        embed.add_field(name="Aired", value = anime.aired, inline=False)
        if (result.episodes == None):
            embed.add_field(name="Duration", value="Unknown", inline=True)
            embed.add_field(name="Episodes", value="Unknown", inline=True)
        else:
            embed.add_field(name="Duration", value=anime.duration, inline=True)
            embed.add_field(name="Episodes", value=result.episodes, inline=True)
        embed.add_field(name="Score", value=result.score, inline=True)
        await ctx.send(embed = embed)
    
    @commands.command()
    async def manga(self, ctx, *, title:str):
        await ctx.trigger_typing()
        try:
            search = MangaSearch(title)
        except ValueError:
            await ctx.send("Sorry, no results were found.")
            return

        result = search.results[0]
        embed = discord.Embed(title = result.title, description=result.url,colour=discord.Colour.blue())
        manga = Manga(result.mal_id)
        generes = ""
        if "Ecchi" in manga.genres or "Hentai" in manga.genres:
            await ctx.send("Please enter a non-Ecchi (non-NSFW) manga.")
            return
        embed.set_thumbnail(url= result.image_url)
        embed.add_field(name="Status", value=manga.status, inline=True)
        embed.add_field(name="Type", value=result.type, inline=True)
        embed.add_field(name= "Synopsis", value=result.synopsis, inline=False)
        for i in range(len(manga.genres)):
            if i != len(manga.genres)-1:
                generes += manga.genres[i]+", "
            else:
                generes += manga.genres[i]
        if (result.volumes == None):
            embed.add_field(name="Chapters", value="Unknown", inline=True)
            embed.add_field(name="Volumes", value="Unknown", inline=True)
        else:
            embed.add_field(name="Chapters", value=manga.chapters, inline=True)
            embed.add_field(name="Volumes", value=result.volumes, inline=True)
        embed.add_field(name="Score", value=result.score, inline=True)
        await ctx.send(embed = embed)


    @commands.command(aliases = ["anime_list"])
    async def animeList(self, ctx, *, user:str):
        try:
            listOfAnime = retrieveTitles(user)
        except:
            await ctx.send("Please enter a valid MAL username.\n"+"(Go to this link if you think you entered your username correctly and click submit: https://myanimelist.net/animelist/" + user )
            return
        scoreList = [[],[],[],[],[]]
        completedList = []
        watchingList = []
        onHoldList = []
        droppedList = []
        planToWatchList = []
        betterAnimeList = []

        for anime in listOfAnime:
            score = anime['score']
            if anime['status'] == 2:
                completedList.append(anime)
            elif anime['status'] == 1:
                watchingList.append(anime)
            elif anime['status'] == 3:
                onHoldList.append(anime)
            elif anime['status'] == 4:
                droppedList.append(anime)
            elif anime['status'] == 6:
                planToWatchList.append(anime)
            if anime['status'] == 6:
                scoreList[4].append(score)
            else:
                scoreList[anime['status']-1].append(score)

        betterAnimeList.append(watchingList)
        betterAnimeList.append(completedList)
        betterAnimeList.append(onHoldList)
        betterAnimeList.append(droppedList)
        betterAnimeList.append(planToWatchList)

        for j in range(len(scoreList)):
            category = scoreList[j]
            changed = True
            while changed:
                changed = False
                for i in range(len(category)-1):
                    if category[i] < category[i+1]:
                        temp = category[i+1]
                        category[i+1] = category[i]
                        category[i] = temp
                        temp = betterAnimeList[j][i + 1]
                        betterAnimeList[j][i + 1] = betterAnimeList[j][i]
                        betterAnimeList[j][i] = temp
                        changed = True

        stringList = []
        for j in range(len(betterAnimeList)):
            category = betterAnimeList[j]
            holder = []
            for i in range(len(category)):
                score = str(category[i]["score"])
                if score == "0":
                    score = "-"
                title = category[i]["anime_title"]
                holder.append(str(title) + "\nScore: "+str(score))
            stringList.append(holder)
        descriptionList = []
        titles = ["Watching", "Completed", "On Hold", "Dropped", "Plan to Watch"]
        titleList = []
        for k in range(len(stringList)):
            category = stringList[k]
            title = titles[k]
            numberOfPages = len(category)//10 + 1
            lastPageEntries = len(category) % 10


            for i in range(numberOfPages-1):
                holder = []
                for j in range(10):
                    holder.append(category[i*10 + j])
                descriptionList.append(holder)
                titleList.append(title)
            if lastPageEntries == 0:
                lastPageEntries = 10
            holder = []
            for i in range(lastPageEntries):

                if ((numberOfPages-1)*10 + i > len(category)-1):
                    break
                holder.append(category[(numberOfPages-1)*10 + i])
            descriptionList.append(holder)
            titleList.append(title)

        embeds = []
        title = ""
        lastIndex = 0
        for i in range(len(descriptionList)):
            if i != 0 and title != titleList[i]:
                lastIndex = i
            holder = ""
            for j in range(len(descriptionList[i])):
                holder += str(descriptionList[i][j])+"\n"
            embeds.append(discord.Embed(title= titleList[i]+" Page "+str(i+1-lastIndex), description=holder, color=0x5599ff))
            title = titleList[i]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(aliases = ["manga_list"])
    async def mangaList(self, ctx, *, user:str):
        try:
            listOfAnime = retrieveTitlesManga(user)
        except:
            await ctx.send("Please enter a valid MAL username.\n"+"(Go to this link if you entered your username correctly and click submit: https://myanimelist.net/mangalist/" + user )
            return
        scoreList = [[],[],[],[],[]]
        completedList = []
        watchingList = []
        onHoldList = []
        droppedList = []
        planToWatchList = []
        betterAnimeList = []

        for anime in listOfAnime:
            score = anime['score']
            if anime['status'] == 2:
                completedList.append(anime)
            elif anime['status'] == 1:
                watchingList.append(anime)
            elif anime['status'] == 3:
                onHoldList.append(anime)
            elif anime['status'] == 4:
                droppedList.append(anime)
            elif anime['status'] == 6:
                planToWatchList.append(anime)
            if anime['status'] == 6:
                scoreList[4].append(score)
            else:
                scoreList[anime['status']-1].append(score)

        betterAnimeList.append(watchingList)
        betterAnimeList.append(completedList)
        betterAnimeList.append(onHoldList)
        betterAnimeList.append(droppedList)
        betterAnimeList.append(planToWatchList)

        for j in range(len(scoreList)):
            category = scoreList[j]
            changed = True
            while changed:
                changed = False
                for i in range(len(category)-1):
                    if category[i] < category[i+1]:
                        temp = category[i+1]
                        category[i+1] = category[i]
                        category[i] = temp
                        temp = betterAnimeList[j][i + 1]
                        betterAnimeList[j][i + 1] = betterAnimeList[j][i]
                        betterAnimeList[j][i] = temp
                        changed = True

        stringList = []
        for j in range(len(betterAnimeList)):
            category = betterAnimeList[j]
            holder = []
            for i in range(len(category)):
                score = str(category[i]["score"])
                if score == "0":
                    score = "-"
                title = category[i]["manga_title"]
                holder.append(str(title) + "\nScore: "+str(score))
            stringList.append(holder)
        descriptionList = []
        titles = ["Reading", "Completed", "On Hold", "Dropped", "Plan to Read"]
        titleList = []
        for k in range(len(stringList)):
            category = stringList[k]
            title = titles[k]
            numberOfPages = len(category)//10 + 1
            lastPageEntries = len(category) % 10


            for i in range(numberOfPages-1):
                holder = []
                for j in range(10):
                    holder.append(category[i*10 + j])
                descriptionList.append(holder)
                titleList.append(title)
            if lastPageEntries == 0:
                lastPageEntries = 10
            holder = []
            for i in range(lastPageEntries):

                if ((numberOfPages-1)*10 + i > len(category)-1):
                    break
                holder.append(category[(numberOfPages-1)*10 + i])
            descriptionList.append(holder)
            titleList.append(title)

        embeds = []
        title = ""
        lastIndex = 0
        for i in range(len(descriptionList)):
            if i != 0 and title != titleList[i]:
                lastIndex = i
            holder = ""
            for j in range(len(descriptionList[i])):
                holder += str(descriptionList[i][j])+"\n"
            embeds.append(discord.Embed(title= titleList[i]+" Page "+str(i+1-lastIndex), description=holder, color=0x5599ff))
            title = titleList[i]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(aliases = ["anime_stats"])
    async def animeStats(self, ctx, *, user:str):
        try:
            listed = retrieveAnimeProfile(user, True)
        except:
            await ctx.send("Please enter a valid MAL username.\n"+"(Go to this link if you entered your username correctly and click submit: https://myanimelist.net/profile/" + user )
            return

        embed = discord.Embed(title=user + "'s Anime Stats", color=0x5599ff)
        embed.add_field(name = "Days Watched", value = listed[0], inline = True)
        embed.add_field(name="Mean Score", value=listed[1], inline=False)
        embed.add_field(name="Watching", value=listed[2], inline=True)
        embed.add_field(name="Completed", value=listed[3], inline=True)
        embed.add_field(name="Rewatched", value=listed[8], inline=True)
        embed.add_field(name="Plan to Watch", value=listed[6], inline=True)
        embed.add_field(name="On-Hold", value=listed[4], inline=True)
        embed.add_field(name="Dropped", value=listed[5], inline=True)
        embed.add_field(name="Total Entries", value=listed[7], inline=True)
        embed.add_field(name="Total Number of Episodes", value=listed[9], inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases = ["manga_stats"])
    async def mangaStats(self, ctx, *, user:str):
        try:
            listed = retrieveAnimeProfile(user, False)
        except:
            await ctx.send("Please enter a valid MAL username.\n"+"(Go to this link if you entered your username correctly and click submit: https://myanimelist.net/profile/" + user )
            return
        embed = discord.Embed(title=user + "'s Manga Stats", color=0x5599ff)
        embed.add_field(name="Days Read", value=listed[0], inline=True)
        embed.add_field(name="Mean Score", value=listed[1], inline=False)
        embed.add_field(name="Reading", value=listed[2], inline=True)
        embed.add_field(name="Completed", value=listed[3], inline=True)
        embed.add_field(name="Reread", value=listed[8], inline=True)
        embed.add_field(name="Plan to Read", value=listed[6], inline=True)
        embed.add_field(name="On-Hold", value=listed[4], inline=True)
        embed.add_field(name="Dropped", value=listed[5], inline=True)
        embed.add_field(name="Total Entries", value=listed[7], inline=True)
        embed.add_field(name="Total Number of Chapters", value=listed[9], inline=True)
        embed.add_field(name="Total Number of Volumes", value=listed[10], inline=True)
        await ctx.send(embed=embed)


    @animeList.error
    @mangaList.error
    @animeStats.error
    @mangaStats.error
    @anime.error
    @manga.error
    async def anime_error(self, ctx, error):
        if (await error_helper(ctx, True)):
            return
