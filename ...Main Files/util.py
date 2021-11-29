import discord
from discord.ext import commands, tasks
from discord.utils import get
from helper import pluginEnabled, error_helper
import matplotlib.pyplot as plt
import matplotlib as mpl
import sympy as sym
from sympy import diff
from sympy import integrate
import os
import asyncio
import random


mpl.rcParams['text.color'] = 'white'

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["random_num"])
    async def randomNum(self, ctx,lowerBound : int, upperBound: int):
        if not await pluginEnabled("utility", ctx.guild):
            return
        if lowerBound >= upperBound:
            await ctx.send("Your lower bound is greater than or equal to your upper bound!")
            return
        rand = random.randint(lowerBound, upperBound)
        await ctx.send("The number was "+str(rand)+".")

    @commands.command(aliases = ["coin_flip"])
    async def coinFlip(self, ctx):
        if not await pluginEnabled("utility", ctx.guild):
            return
        rand = random.randint(0, 1)
        if rand == 0:
            await ctx.send("Heads!")
            return
        await ctx.send("Tails!")

    @commands.command(aliases=["avatar", "profile", "pfp"])
    async def getpfp(self, ctx, member: discord.Member = None):
        if not await pluginEnabled("utility", ctx.guild):
            return
        if not member:
            member = ctx.author
        await ctx.send(member.avatar_url)

    @commands.command(aliases=["calculate", "evaluate"])
    async def solve(self, ctx, *,  expression:str = ""):
        correct = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", " ", "^", "+", "/", "*", "+", "-", "x", "m", "o", "d", "(", ")"]
        if not await pluginEnabled("utility", ctx.guild):
            return
        if expression == "":
            await ctx.send("Please enter a valid expression.")
            return
        checker = list(expression)
        for i in checker:
            if i not in correct:
                await ctx.send("Please enter a valid expression.")
                return
        expression = expression.replace("mod", "%")
        expression = expression.replace(" ", "")
        expression = expression.replace("x", "*")
        expression = expression.replace("^", "**")
        try:
            await ctx.send("The answer is " + str(eval(expression))+".")
        except:
            await ctx.send("Please enter a valid expression.")

    @commands.command(aliases = ["d", "derv"])
    async def derivative(self, ctx, var, function):
        await ctx.send("Derivative of "+function+":")
        function = function.replace("1" + var, "1*" + var)
        function = function.replace("2" + var, "2*" + var)
        function = function.replace("3" + var, "3*" + var)
        function = function.replace("4" + var, "4*" + var)
        function = function.replace("5" + var, "5*" + var)
        function = function.replace("6" + var, "6*" + var)
        function = function.replace("7" + var, "7*" + var)
        function = function.replace("8" + var, "8*" + var)
        function = function.replace("9" + var, "9*" + var)
        function = function.replace("0" + var, "0*" + var)
        function = function.replace("cot^-1", "acot")
        function = function.replace("sec^-1", "asec")
        function = function.replace("csc^-1", "acsc")
        function = function.replace("cos^-1", "acos")
        function = function.replace("sin^-1", "asin")
        function = function.replace("tan^-1", "atan")
        function = function.replace("^", "**")
        function = function.replace("arc", "a")
        x = sym.symbols(var)
        try:
            result = str(diff(function, x))
        except:
            await ctx.send("Please enter a valid function.")
            return
        if result == "cow":
            await ctx.send("Please enter a valid function.")
            return
        result = result.replace("**", "^")
        result = result.replace("*log(e)*", "")
        result = result.replace("*log(e)", "")
        result = result.replace("log(e)*", "")
        result = result.replace("1*" + var, "1" + var)
        result = result.replace("2*" + var, "2" + var)
        result = result.replace("3*" + var, "3" + var)
        result = result.replace("4*" + var, "4" + var)
        result = result.replace("5*" + var, "5" + var)
        result = result.replace("6*" + var, "6" + var)
        result = result.replace("7*" + var, "7" + var)
        result = result.replace("8*" + var, "8" + var)
        result = result.replace("9*" + var, "9" + var)
        result = result.replace("0*" + var, "0" + var)
        result = result.replace("log(", "ln")
        result = result.replace("atan", "arctan")
        result = result.replace("acot", "arccot")
        result = result.replace("acsc", "arccsc")
        result = result.replace("asec", "arcsec")
        result = result.replace("acos", "arccos")
        result = result.replace("asin", "arcsin")
        await ctx.send("Answer: " + result)

    @commands.command(aliases = ["ii", "iinteg"])
    async def iintegral(self, ctx, var, function):
        await ctx.send("Integral of " + function + ":")
        function = function.replace("1"+var, "1*"+var)
        function = function.replace("2"+var, "2*"+var)
        function = function.replace("3"+var, "3*"+var)
        function = function.replace("4"+var, "4*"+var)
        function = function.replace("5"+var, "5*"+var)
        function = function.replace("6"+var, "6*"+var)
        function = function.replace("7"+var, "7*"+var)
        function = function.replace("8"+var, "8*"+var)
        function = function.replace("9"+var, "9*"+var)
        function = function.replace("0"+var, "0*"+var)
        function = function.replace("cot^-1", "acot")
        function = function.replace("sec^-1", "asec")
        function = function.replace("csc^-1", "acsc")
        function = function.replace("cos^-1", "acos")
        function = function.replace("sin^-1", "asin")
        function = function.replace("tan^-1", "atan")
        function = function.replace("^", "**")
        function = function.replace("arc", "a")
        x = sym.symbols(var)
        try:
            result = str(integrate(function, x))
        except:
            await ctx.send("Please enter a valid function.")
            return
        if result == "cow":
            await ctx.send("Please enter a valid function.")
            return
        result = result.replace("**", "^")
        result = result.replace("*log(e)*", "")
        result = result.replace("*log(e)", "")
        result = result.replace("log(e)*", "")
        result = result.replace("1*"+var, "1"+var)
        result = result.replace("2*"+var, "2"+var)
        result = result.replace("3*"+var, "3"+var)
        result = result.replace("4*"+var, "4"+var)
        result = result.replace("5*"+var, "5"+var)
        result = result.replace("6*"+var, "6"+var)
        result = result.replace("7*"+var, "7"+var)
        result = result.replace("8*"+var, "8"+var)
        result = result.replace("9*"+var, "9"+var)
        result = result.replace("0*"+var, "0"+var)
        result = result.replace("log", "ln")
        result = result.replace("atan", "arctan")
        result = result.replace("acot", "arccot")
        result = result.replace("acsc", "arccsc")
        result = result.replace("asec", "arcsec")
        result = result.replace("acos", "arccos")
        result = result.replace("asin", "arcsin")
        if "Piecewise" in result.split("("):
            x = "Answer: "
            listed = list(result)
            for i in range(len(listed)):
                if listed[i] == ",":
                    await ctx.send(x+" + C")
                    break
                elif i > 10:
                    x+=listed[i]
            return
        elif "Integral" in result.split("("):
            await ctx.send("We were unable to solve this integral.")
            return
        await ctx.send("Answer: "+result+" + C")



    @solve.error
    @randomNum.error
    @coinFlip.error
    @getpfp.error
    @derivative.error
    @iintegral.error
    async def util_error(self, ctx, error):
        if (await error_helper(ctx, True)):
            return