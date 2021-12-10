import sqlite3
from sqlite3 import Error

pluginList = [["moderation", "mod"],
              ["join/leave messages", "join", "leave", "join messages", "leaving messages", "welcome",
               "welcome messages", "welcome and leaving", "welcome and leaving messages"],
              ["utility", "util"], ["custom"], ["music"], ["leveling", "levels"]]
botID = 785687696781737995
programmerID = 721170371826679841
client = []

class Queue():
    def __init__(self):
        self.queue = []

    def enqueue(self, data):
        self.queue.append(data)

    def dequeue(self, data):
        return self.queue.pop(0)

    def latency(self):
        return len(self.queue)

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