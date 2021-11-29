import discord
from discord.ext import commands, tasks
from discord.utils import get
from mal import *
from disputils import *
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from helper import error_helper, create_connection

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

def retrieveTAni(user:str):
    query = '''
                query ($name: String){ 
                    User (name: $name) { 
                        id
                    }
                }
                '''
    variables = {
        'name': user
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    try:
        id = response.json()['data']['User']['id']
    except:
        return []
    morePages = True
    pagenum = 0
    animeList = [[] for i in range(5)]
    while morePages:
        query = '''
        query ($page: Int, $perPage: Int, $userId: Int) {
            Page(page: $page, perPage: $perPage) {
                pageInfo{
                        total
                        hasNextPage
                }
                mediaList(type: ANIME, sort:[SCORE_DESC], userId: $userId) {
                    status
                    score(format: POINT_10)
                    media {
                        title {
                            romaji
                        }
                    }
                }
            }
        }'''
        variables = {
            'page' : pagenum,
            'userId': id,
            'perPage': 10
        }
        response = requests.post(url, json={'query': query, 'variables': variables})
        json = response.json()['data']['Page']
        morePages = json['pageInfo']['hasNextPage']
        animeListPage = json['mediaList']
        for entry in animeListPage:
            if entry['status'] == "COMPLETED":
                if entry['score'] == 0:
                    animeList[0].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[0].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "CURRENT":
                if entry['score'] == 0:
                    animeList[1].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[1].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "PAUSED":
                if entry['score'] == 0:
                    animeList[2].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[2].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "DROPPED":
                if entry['score'] == 0:
                    animeList[3].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[3].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "PLANNING":
                if entry['score'] == 0:
                    animeList[4].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[4].append((entry['media']['title']['romaji'],entry['score']))
        pagenum+=1
    return animeList

def retrieveTAniM(user:str):
    query = '''
                query ($name: String){ 
                    User (name: $name) { 
                        id
                    }
                }
                '''
    variables = {
        'name': user
    }
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    try:
        id = response.json()['data']['User']['id']
    except:
        return []
    morePages = True
    pagenum = 0
    animeList = [[] for i in range(5)]
    while morePages:
        query = '''
        query ($page: Int, $perPage: Int, $userId: Int) {
            Page(page: $page, perPage: $perPage) {
                pageInfo{
                        total
                        hasNextPage
                }
                mediaList(type: MANGA, sort:[SCORE_DESC], userId: $userId) {
                    status
                    score(format: POINT_10)
                    media {
                        title {
                            romaji
                        }
                    }
                }
            }
        }'''
        variables = {
            'page' : pagenum,
            'userId': id,
            'perPage': 10
        }
        response = requests.post(url, json={'query': query, 'variables': variables})
        json = response.json()['data']['Page']
        morePages = json['pageInfo']['hasNextPage']
        animeListPage = json['mediaList']
        for entry in animeListPage:
            if entry['status'] == "COMPLETED":
                if entry['score'] == 0:
                    animeList[0].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[0].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "CURRENT":
                if entry['score'] == 0:
                    animeList[1].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[1].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "PAUSED":
                if entry['score'] == 0:
                    animeList[2].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[2].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "DROPPED":
                if entry['score'] == 0:
                    animeList[3].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[3].append((entry['media']['title']['romaji'],entry['score']))
            elif entry['status'] == "PLANNING":
                if entry['score'] == 0:
                    animeList[4].append((entry['media']['title']['romaji'], "-"))
                else:
                    animeList[4].append((entry['media']['title']['romaji'],entry['score']))
        pagenum+=1
    return animeList

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
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM mal WHERE user =" + str(ctx.author.id) + ";")
        listed = curr.fetchall()
        scoreList = [[], [], [], [], []]
        completedList = []
        watchingList = []
        onHoldList = []
        droppedList = []
        planToWatchList = []
        betterAnimeList = []
        if len(listed) == 0:
            try:
                listOfAnime = retrieveTitles(user)
            except:
                await ctx.send("Please enter a valid MAL username.\n"+"(Go to this link if you think you entered your username correctly and click submit: https://myanimelist.net/animelist/" + user )
                return

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
        else:
            query = '''
                        query ($name: String){ 
                          User (name: $name) { 
                                id
                            }
                          }
                        }
                        '''
            variables = {
                'name': user
            }
            url = 'https://graphql.anilist.co'
            response = requests.post(url, json={'query': query, 'variables': variables})
            try:
                json = response.json()['data']['User']
            except:
                await ctx.send("Please enter a valid anilist username.")
                return
            anilist = retrieveTAniM(user)
            tempHolder = anilist[0]
            anilist[0] = anilist[1]
            anilist[1] = anilist[0]
            scoreList = [[score for anime, score in lists] for lists in anilist]
            betterAnimeList = [[anime for anime, score in lists] for lists in anilist]
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
            titleString = titleList[i] + " Page " + str(i + 1 - lastIndex)

            if len(listed) == 0:
                titleString += " (MAL)"
            else:
                titleString += " (Anilist)"
            embeds.append(discord.Embed(title=titleString, description=holder, color=0x5599ff))
            title = titleList[i]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(aliases = ["manga_list"])
    async def mangaList(self, ctx, *, user:str):
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM mal WHERE user =" + str(ctx.author.id) + ";")
        listed = curr.fetchall()
        scoreList = [[], [], [], [], []]
        completedList = []
        watchingList = []
        onHoldList = []
        droppedList = []
        planToWatchList = []
        betterAnimeList = []
        if len(listed) == 0:
            try:
                listOfAnime = retrieveTitlesManga(user)
            except:
                await ctx.send("Please enter a valid MAL username.\n"+"Go to this link if you entered your username correctly and click submit: https://myanimelist.net/mangalist/" + user   )
                return


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
        else:
            query = '''
                        query ($name: String){ 
                          User (name: $name) { 
                                id
                            }
                          }
                        }
                        '''
            variables = {
                'name': user
            }
            url = 'https://graphql.anilist.co'
            response = requests.post(url, json={'query': query, 'variables': variables})
            try:
                json = response.json()['data']['User']
            except:
                await ctx.send("Please enter a valid anilist username.")
                return
            anilist = retrieveTAniM(user)
            tempHolder = anilist[0]
            anilist[0] = anilist[1]
            anilist[1] = anilist[0]
            scoreList = [[score for anime, score in lists] for lists in anilist]
            betterAnimeList = [[anime for anime, score in lists] for lists in anilist]

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
            titleString = titleList[i]+" Page "+str(i+1-lastIndex)

            if len(listed) == 0:
                titleString += " (MAL)"
            else:
                titleString+= " (Anilist)"
            embeds.append(discord.Embed(title= titleString, description=holder, color=0x5599ff))
            title = titleList[i]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()


    @commands.command(aliases = ["anime_stats"])
    async def animeStats(self, ctx, *, user:str):
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM mal WHERE user ="+str(ctx.author.id)+";")
        listed = curr.fetchall()
        if len(listed)==0:
            try:
                listed = retrieveAnimeProfile(user, True)
            except:
                await ctx.send("Please enter a valid MAL username.\n"+"Go to this link if you entered your username correctly and click submit: https://myanimelist.net/profile/" + user )
                return

            embed = discord.Embed(title=user + "'s Anime Stats (MAL)", color=0x5599ff)
            embed.add_field(name = "Days Watched", value = listed[0], inline = True)
            embed.add_field(name="Mean Score", value=listed[1], inline=False)
            embed.add_field(name="Watching", value=listed[2], inline=True)
            embed.add_field(name="Completed", value=listed[3], inline=True)
            embed.add_field(name="Plan to Watch", value=listed[6], inline=True)
            embed.add_field(name="On-Hold", value=listed[4], inline=True)
            embed.add_field(name="Dropped", value=listed[5], inline=True)
            embed.add_field(name="Total Entries", value=listed[7], inline=True)
            embed.add_field(name="Total Number of Episodes", value=listed[9], inline=True)
            await ctx.send(embed=embed)
        else:
            query = '''
            query ($name: String){ 
              User (name: $name) { 
                statistics {
                  	anime {
                      count
                      meanScore
                      minutesWatched
                      episodesWatched

                    }

                }
              }
            }
            '''
            variables = {
                'name': user
            }
            url = 'https://graphql.anilist.co'
            response = requests.post(url, json={'query': query, 'variables': variables})
            try:
                json = response.json()['data']['User']['statistics']['anime']
                listed = []
                listed.append(json['minutesWatched'])
                listed.append(json['meanScore'])
                listed.append(0)
                listed.append(0)
                listed.append(0)
                listed.append(0)
                listed.append(0)
                listed.append(json['count'])
                listed.append(0)
                listed.append(json['episodesWatched'])
            except:
                await ctx.send("Please enter a valid anilist username.")
                return
            anilist = retrieveTAni(user)
            embed = discord.Embed(title=user + "'s Anime Stats (Anilist)", color=0x5599ff)
            embed.add_field(name="Minutes Watched", value=listed[0], inline=True)
            embed.add_field(name="Mean Score", value=listed[1], inline=False)
            embed.add_field(name="Watching", value=len(anilist[1]), inline=True)
            embed.add_field(name="Completed", value=len(anilist[0]), inline=True)
            embed.add_field(name="Plan to Watch", value=len(anilist[4]), inline=True)
            embed.add_field(name="On-Hold", value=len(anilist[2]), inline=True)
            embed.add_field(name="Dropped", value=len(anilist[3]), inline=True)
            embed.add_field(name="Total Entries", value=listed[7], inline=True)
            embed.add_field(name="Total Number of Episodes", value=listed[9], inline=True)
            await ctx.send(embed=embed)

    @commands.command(aliases = ["manga_stats"])
    async def mangaStats(self, ctx, *, user:str):
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM mal WHERE user =" + str(ctx.author.id) + ";")
        listed = curr.fetchall()
        if len(listed) == 0:
            try:
                listed = retrieveAnimeProfile(user, False)
            except:
                await ctx.send("Please enter a valid MAL username.\n"+"(Go to this link if you entered your username correctly and click submit: https://myanimelist.net/profile/" + user )
                return
            embed = discord.Embed(title=user + "'s Manga Stats (MAL)", color=0x5599ff)
            embed.add_field(name="Days Read", value=listed[0], inline=True)
            embed.add_field(name="Mean Score", value=listed[1], inline=False)
            embed.add_field(name="Reading", value=listed[2], inline=True)
            embed.add_field(name="Completed", value=listed[3], inline=True)
            embed.add_field(name="Plan to Read", value=listed[6], inline=True)
            embed.add_field(name="On-Hold", value=listed[4], inline=True)
            embed.add_field(name="Dropped", value=listed[5], inline=True)
            embed.add_field(name="Total Entries", value=listed[7], inline=True)
            embed.add_field(name="Total Number of Chapters", value=listed[9], inline=True)
            embed.add_field(name="Total Number of Volumes", value=listed[10], inline=True)
            await ctx.send(embed=embed)
        else:
            query = '''
                query ($name: String){ 
                  User (name: $name) { 
                    statistics {
                      	manga {
                          count
                          meanScore
                          chaptersRead
                          volumesRead

                        }

                    }
                  }
                }
                '''
            variables = {
                'name': user
            }
            url = 'https://graphql.anilist.co'
            response = requests.post(url, json={'query': query, 'variables': variables})
            try:
                json = response.json()['data']['User']['statistics']['manga']
                listed = []
                listed.append(0)
                listed.append(json['meanScore'])
                listed.append(0)
                listed.append(0)
                listed.append(0)
                listed.append(0)
                listed.append(0)
                listed.append(json['count'])
                listed.append(0)
                listed.append(json['chaptersRead'])
                listed.append(json['volumesRead'])
            except:
                await ctx.send("Please enter a valid anilist username.")
                return
            anilist = retrieveTAniM(user)

            embed = discord.Embed(title=user + "'s Manga Stats (Anilist)", color=0x5599ff)
            #embed.add_field(name="Days Read", value=listed[0], inline=True)
            embed.add_field(name="Mean Score", value=listed[1], inline=False)
            embed.add_field(name="Reading", value=len(anilist[1]), inline=True)
            embed.add_field(name="Completed", value=len(anilist[0]), inline=True)
            embed.add_field(name="Plan to Read", value=len(anilist[4]), inline=True)
            embed.add_field(name="On-Hold", value=len(anilist[2]), inline=True)
            embed.add_field(name="Dropped", value=len(anilist[3]), inline=True)
            embed.add_field(name="Total Entries", value=listed[7], inline=True)
            embed.add_field(name="Total Number of Chapters", value=listed[9], inline=True)
            embed.add_field(name="Total Number of Volumes", value=listed[10], inline=True)
            await ctx.send(embed=embed)

    @commands.command()
    async def changeList(self, ctx):
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM mal WHERE user =" + str(ctx.author.id) + ";")
        listed = curr.fetchall()
        if len(listed) == 0:
            sql = ''' INSERT INTO mal(user, ani) 
                            VALUES(?,?);'''
            curr.execute(sql, (ctx.author.id, 1))
            conn.commit()
            await ctx.send("Set your source for anime/manga lists to anilist. ")
        else:
            curr.execute("DELETE FROM mal WHERE user =" + str(ctx.author.id) + ";")
            conn.commit()
            await ctx.send("Set your source anime/manga list to myanimelist. ")

    @commands.command()
    async def animeSettings(self, ctx):
        conn = create_connection("fullDB.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM mal WHERE user =" + str(ctx.author.id) + ";")
        listed = curr.fetchall()
        if len(listed) == 0:
            await ctx.send("Your set anime/manga list source is currently myanimelist. ")
        else:
            curr.execute("DELETE FROM mal WHERE user =" + str(ctx.author.id) + ";")
            conn.commit()
            await ctx.send("Your set anime/manga list source is currently anilist. ")

    @animeList.error
    @mangaList.error
    @animeStats.error
    @mangaStats.error
    @anime.error
    @manga.error
    async def anime_error(self, ctx, error):
        if (await error_helper(ctx, True)):
            return
