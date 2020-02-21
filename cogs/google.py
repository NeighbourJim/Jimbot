import discord
import random
import asyncio
import logging
from discord.ext import commands
from discord.ext.commands import BucketType
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Internal Imports
from internal.logs import logger
from internal.helpers import Helper
from bot import current_settings



class Google(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.cse_service = build('customsearch', 'v1', developerKey=current_settings["keys"]["google"])
        self.yt_service = build('youtube', 'v3', developerKey=current_settings["keys"]["google"])

    #region --------------- Google Search ---------------
    async def GetSearchResult(self, message):
        query = Helper.CommandStrip(message)
        results = self.cse_service.cse().list(q=query, cx=current_settings["keys"]["cse"]).execute()
        if "items" in results:
            final_results = []
            i = 0
            for item in results["items"]:
                if(i < 3):
                    final_results.append(item)
                    i += 1
                else:
                    break
            return final_results
        else:
            return None

    async def GetSafeSearchResult(self, message):
        query = Helper.CommandStrip(message)
        results = self.cse_service.cse().list(q=query, cx=current_settings["keys"]["cse"], safe="active").execute()
        if "items" in results:
            final_results = []
            i = 0
            for item in results["items"]:
                if(i < 3):
                    final_results.append(item)
                    i += 1
                else:
                    break
            return final_results
        else:
            return None

    @commands.command(aliases=["g", "gs", "G", "Gs", "Google"], help="Searches Google and returns up to the first 3 results.\nUsage: !google funny dog.")    
    @commands.cooldown(rate=1, per=5, type=BucketType.channel)
    @commands.guild_only()
    async def google(self,ctx):
        try:
            if ctx.message.channel.is_nsfw():
                task = asyncio.create_task(self.GetSearchResult(ctx.message.content))
            else:
                task = asyncio.create_task(self.GetSafeSearchResult(ctx.message.content))
            await task
            if(task.result() != None):
                fields = []
                for item in task.result():
                    fields.append({"name": item['title'], "value": item['link'], "inline": False })        
                result_dict = {
                    "author": {"name": "Search Results for '{}'".format(Helper.CommandStrip(ctx.message.content))}, 
                    "footer": {"text": "Searched for by {}".format(ctx.message.author)}, 
                    "fields": fields,
                    "thumbnail": {"url": "https://cdn.discordapp.com/attachments/144073497939935232/677385165462568970/500px-Google_G_Logo.svg.png"}
                    }
                result_embed = discord.Embed.from_dict(result_dict)
                await ctx.send(embed=result_embed)
            else:
                await ctx.send(f'{ctx.message.author.mention}: No results found for that query.')
        except Exception as ex:
            print(ex)
            await self.client.close()

            
            
    #endregion

    #region --------------- Image Search ---------------
    async def GetImageResult(self, message):
        query = Helper.CommandStrip(message)
        results = self.cse_service.cse().list(q=query, cx=current_settings["keys"]["cse"], searchType="image").execute()
        if "items" in results:
            return random.choice(list(results["items"]))
        else:
            return None

    async def GetSafeImageResult(self, message):
        query = Helper.CommandStrip(message)
        results = self.cse_service.cse().list(q=query, cx=current_settings["keys"]["cse"], searchType="image", safe="active").execute()
        if "items" in results:
            return random.choice(list(results["items"]))
        else:
            return None

    @commands.command(aliases=["i", "gi", "I", "GI", "Image", "IMAGE"], help="Searches Google for an image from a query.\nGives a random result from the front page. Safe-Search is enabled for SFW channels, and disabled for NSFW ones.\nUsage: !image funny dog\n")    
    @commands.cooldown(rate=1, per=15, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()
    async def image(self, ctx):
        try:
            if ctx.message.channel.is_nsfw():
                task = asyncio.create_task(self.GetImageResult(ctx.message.content))
            else:
                task = asyncio.create_task(self.GetSafeImageResult(ctx.message.content))
            await task
            if(task.result() != None):
                await ctx.send(f'{ctx.message.author.mention}: **{task.result()["title"]}**\n{task.result()["link"]}')
            else:
                await ctx.send(f'{ctx.message.author.mention}: No results found for that query. Note that Safe Search is on if the channel is not marked as NSFW!')
        except Exception as ex:
            logger.LogPrint("IMAGE ERROR", logging.CRITICAL, ex)
            await ctx.send(f'ERROR: {ex}.')
    #endregion

    #region --------------- Youtube Search ---------------
    async def GetYoutubeVideo(self, message):
        query = Helper.CommandStrip(message)
        results = self.yt_service.search().list(q=query, part='id,snippet', maxResults=10).execute()
        videos = []
        if "items" in results:
            for item in results.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    videos.append(item)
            if len(videos) > 0:
                return videos[0]
            else:
                return None
        else:
            return None

    @commands.command(aliases=["yt", "YT", "Youtube", "YouTube"], help="Searches Youtube for a query and returns the first video result.\nUsage: !yt funny dog.")
    @commands.cooldown(rate=1, per=15, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()
    async def youtube(self, ctx):
        try:
            task = asyncio.create_task(self.GetYoutubeVideo(ctx.message.content))
            await task
            if task.result() != None:
                await ctx.send(f'{ctx.message.author.mention}: http://youtu.be/{task.result()["id"]["videoId"]}')
            else:
                await ctx.send(f'{ctx.message.author.mention}: No results found.')
        except Exception as ex:
            logger.LogPrint("YOUTUBE ERROR", logging.CRITICAL, ex)
            await ctx.send(f'ERROR: {ex}.')
    #endregion

def setup(client):
    client.add_cog(Google(client))