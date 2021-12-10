import discord
from discord.ext import commands, tasks
from discord.utils import get

class Leveling(commands.Cog):
    def __init__(self, client):
        self.client = client
