### THIS COG IS FOR MACHIO AND KNITE TO PRACTICE AND MAKE THEIR OWN COMMANDS

import discord
import logging
import random
import requests
import pickle
import datetime
import asyncio
import time
import re
import os.path
from os import path
from discord.ext import commands
from discord.ext.commands import BucketType
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from matplotlib import pyplot

from internal.logs import logger
from internal.helpers import Helpers
from internal.databasemanager import dbm
from internal.enums import WhereType, CompareType

class cliffnet(commands.Cog):

    def __init__(self, client):
        self.client = client
              
    @commands.command(aliases=["Scramble"], help="scrambles word order")
    @commands.cooldown(rate=1, per=1, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()
    async def scramble(self, ctx):
        if ctx.guild.id == 107847342006226944:
            userInput = Helpers.CommandStrip(self, ctx.message.content)
            split_message = userInput.split(' ')
            if len(split_message) > 0:
                result = random.sample(split_message, len(split_message))
                stringResult= " "
                stringResult = stringResult.join(result)
                await ctx.send(f'{ctx.message.author.mention}: {stringResult}')
            else:
                await ctx.send(f'{ctx.message.author.mention}: Call tech support on Jims PM')


    @commands.command(aliases=["News", "n"], help="Search the recent news via a keyword! Powered by newsapi.org")  
    @commands.cooldown(rate=1, per=2, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()
    async def news(self, ctx):
        if ctx.guild.id == 107847342006226944:
            await ctx.trigger_typing()
            try:
                userInput = Helpers.CommandStrip(self, ctx.message.content)
                if userInput=="":
                    return await ctx.send(f'Enter a keyword to search')
                    
                source = (f'http://newsapi.org/v2/everything?q={userInput}&sortBy=top&apiKey=fec0d23dd26549a9a6d58a29a675e764')
                
                pull = requests.get(source)

                articles = pull.json()["totalResults"]

                if articles == 0:
                   return await ctx.send(f'{ctx.message.author.mention}: No results.')
                elif articles < 19:
                    randomId = random.randint(0,articles)
                else:
                    randomId = random.randint(0,19)
                    
                content = pull.json()["articles"][randomId]
                responseUrl = content["url"]
                if content:
                    await ctx.send(f'Result: {responseUrl}')
                else: 
                    await ctx.send(f'{ctx.message.author.mention}: No results.') 
            except Exception as ex:
                await ctx.send(f'Couldn\'t get the news! - {ex}')
                logger.LogPrint(f'Couldn\'t get the news! - {ex}', logging.ERROR)
                
    @commands.command(aliases=["Roulette"], help="Prove your barevery/ commit suicide. between 1-6 bullets")  
    @commands.cooldown(rate=1, per=2, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()

    async def russianroulette(self, ctx):
        if ctx.guild.id == 107847342006226944:
            await ctx.trigger_typing()
        try:
            #get_message_task = ctx.channel.fetch_message(ctx.channel.last_message_id)   
            bullets = Helpers.FuzzyIntegerSearch(self, ctx.message.content)
            if bullets != None:
                bullets = int(bullets)
            else:
                bullets = 0
            pick = 1 
            y= 6 #chambers left
            tension = 0 
            clicks=1
            message= ("..click..")
            
            if bullets <7 and bullets > 0:
            
                while bullets !=0:
                    pick = random.randint(1, int(y))
                    y-=1
                    tension += 1
                    await asyncio.sleep(1.5)
                    if tension > 3 and tension <5:
                        await ctx.send("AAAH AAH AAH", delete_after=1)
                        await asyncio.sleep(1)
                    if tension == 6: 
                        await ctx.send("... ... .... ...", delete_after=1)
                        await asyncio.sleep(3)
                    if pick == 1:
                        await ctx.send(":boom:")
                        break
                    elif pick!=1 and clicks==1:
                        task_one = asyncio.create_task(ctx.send(message))
                        await task_one
                        clicks+=1
                    else:
                        await asyncio.create_task(task_one.result().edit(content=message * clicks))
                        clicks+=1
                    bullets-=1
                    
                if pick != 1:
                    await asyncio.sleep(0.2)
                    await ctx.send("You made it!")
                    
            else:await ctx.send("Incorrect bullets.")
        
        except Exception as ex:
                        await ctx.send(f'gun failure. {ex}')
                        logger.LogPrint(f'wrong bullets bad! bad! {ex}', logging.ERROR)




    @commands.command(aliases=["Movie"], help="find a random movie based on avg score from bromovies")  
    @commands.cooldown(rate=1, per=2, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()
    async def movie(self, ctx):
        if ctx.guild.id == 107847342006226944:
            await ctx.trigger_typing()
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name('./internal/data/bromoviessearch.json', scope) # Your json file here
            
            gc = gspread.authorize(credentials)
            
            wks = gc.open_by_key("1MJivigtIomBZSWpTpYSCjyOuVq8XpScZ-CKdv1OOIM4") #opens sheetsfile
            worksheet = wks.worksheet("movies") #selects worksheet
            data = worksheet.get_all_values()
            headers = data.pop(0)
            
            df = pd.DataFrame(data, columns=headers)
            #all set up now the querry
            
            
            #print(df['avg'])
            #print(df.loc[8])
            df["avg"] = pd.to_numeric(df["avg"])

            try:
                goal = Helpers.CommandStrip(self, ctx.message.content)
                goal = float(goal)
                results=df.loc[(df['avg'] >= goal) & (df['avg'] < goal+1)]['Title'].values #prints whole row where avg == goal
                if len(results) > 0:
                   await ctx.send(f'{ctx.message.author.mention}:', random.choice(results))
                else:
                    await ctx.send(f'{ctx.message.author.mention}:No results, do not try again')
            except ValueError:
                await ctx.send('{ctx.message.author.mention}:You have to enter a number, for example: 5')

    @commands.command(aliases=["Days"], help="Long term timers. Add a timer with \"!days [entry]\". Reset \"!days zero [entry]\". Delete \"!days delete [entry]\".")  
    @commands.cooldown(rate=1, per=2, type=BucketType.channel)
    @commands.has_role("Bot Use")
    @commands.guild_only()
    async def days(self, ctx):
        filename = f"days{ctx.guild.id}"

        async def CheckAndCreateDatabase(self, ctx):
            #most of it shamelessly lifted from meme.py
            try:
                filename = f"days{ctx.guild.id}"
                daysPickleFile = f"./internal/data/databases/days{ctx.guild.id}.pk"
                pickleFileExists = os.path.isfile(daysPickleFile)
                if not path.exists(f'{"./internal/data/databases/"}{filename}.db'):
                    # Create days table
                    columns={
                    "Id":"INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                    "EntryName":"varchar(255) NOT NULL",
                    "CreationDate":"varchar(255) NOT NULL",
                    "CreatorId":"varchar(255)",
                    "LastDuration":"varchar(255)",
                    "LastResetDate":"varchar(255)",
                    "LastResetByName":"varchar(255)",
                    "RecordDuration":"varchar(255)",
                    "TimesReset":"INTEGER",}
                    dbm.CreateTable(filename, "days", columns)
                    # Create Creators table
                    columns ={
                        "Id":"INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
                        "CreatorName":"varchar(255)",
                        "CreatorId":"varchar(255)",
                    }
                    dbm.CreateTable(filename, "creator", columns)
                    # Create durations table
                    columns ={
                        "Id":"INTEGER",
                        "Duration":"varchar(255)",
                        "ResetDate":"varchar(255)",
                    }
                    dbm.CreateTable(filename, "durations", columns)

                if pickleFileExists:
                    await ConvertPickleToDatabase(self,ctx)

            except Exception as ex:
                logger.LogPrint(f'ERROR - Could not create table: {ex}',logging.ERROR)     
                return False
        async def ConvertPickleToDatabase(self, ctx):

            filename = f"days{ctx.guild.id}"
            try:
                daysPickleFile = f"./internal/data/databases/days{ctx.guild.id}.pk"
                daysDict = {}
                fileExists = os.path.isfile(daysPickleFile)
                contentExists = os.path.getsize(daysPickleFile) > 0
                if fileExists is False:
                    logger.LogPrint(f'ERROR ConvertPickleToDatabase - pickle file does not exist, conversion cancelled.', logging.ERROR)
                    return False
                else:
                    if contentExists:
                        legacyCreatorName = "Some Chunk"
                        legacyCreatorId = "<@676693645155631124>" #jimbot
                        legacyResetCount = 1

                        #fill creator table with legacy creator
                        dictForInsert = {
                        "CreatorId": legacyCreatorId,
                        "CreatorName": legacyCreatorName,}
                        dbm.Insert(f"{filename}","creator",dictForInsert)
                        
                        #populate database with pickle data
                        with open(daysPickleFile,"rb") as daysFileReader:           
                            daysDict = pickle.load(daysFileReader)
                        
                        #find legacy creator id
                        creatorId = dbm.Retrieve(f'{filename}', 'creator', [("CreatorName", legacyCreatorName)], where_type=WhereType.AND, column_data=["id"])

                        for key in daysDict.keys():
                            #convert timedelta objects to days / hours
                            lastDurationDays = Helpers.timeDeltaFormat(self, daysDict[key][1])[0]
                            lastDurationHours = Helpers.timeDeltaFormat(self, daysDict[key][1])[1]
                            recordDurationDays = Helpers.timeDeltaFormat(self, daysDict[key][2])[0]
                            recordDurationHours = Helpers.timeDeltaFormat(self, daysDict[key][2])[1]

                            #convert datetime objects to readable string dates + hours
                            creationDate = str(daysDict[key][0].strftime("%m/%d/%Y, %H:%M:%S"))
                            lastResetDate = str(daysDict[key][0].strftime("%m/%d/%Y, %H:%M:%S"))
                            lastDuration = str([lastDurationDays,lastDurationHours])
                            recordDuration = str([recordDurationDays,recordDurationHours])
                            
                            #set legacyresetcount to 0 if entry has never been reset
                            if lastDurationDays == 0 and lastDurationHours == 0:
                                legacyResetCount = 0
                            else:
                                legacyResetCount = 1

                            dictForInsert = {
                            "EntryName": key,
                            "CreationDate": creationDate,
                            "CreatorId": creatorId[0][0],
                            "LastResetDate": lastResetDate,
                            "LastDuration": lastDuration,
                            "TimesReset": legacyResetCount,
                            "LastResetByName": legacyCreatorName,
                            "RecordDuration": recordDuration,}
                            dbm.Insert(f"{filename}","days",dictForInsert)

                            #prevent 0 duration entries into the durations table
                            if legacyResetCount > 0: 
                                dictForInsert = {
                                "Id": dbm.Retrieve(f'{filename}', 'days', [("EntryName", key)], where_type=WhereType.AND, column_data=["id"])[0][0],
                                "Duration": lastDuration,
                                "ResetDate": lastResetDate,}
                                dbm.Insert(f"{filename}","durations",dictForInsert)
                            
                        #rename pickle file so it is not called anymore for imports maybe delete? jim would probably yell at me for deleting files on his server
                        os.rename(f"./internal/data/databases/days{ctx.guild.id}.pk",f"./internal/data/databases/days{ctx.guild.id}BACKUP.pk")
                    else: 
                        os.rename(f"./internal/data/databases/days{ctx.guild.id}.pk",f"./internal/data/databases/days{ctx.guild.id}BACKUP.pk")
                        logger.LogPrint(f'ERROR ConvertPickleToDatabase - pickle is empty, pickle renamed, conversion ended.', logging.ERROR)
                        return False
            except Exception as ex:
                logger.LogPrint(f"Error converting: {ex}",logging.ERROR)
        async def PrintDays(self,ctx):
            try:
                output = "```ini\n"
                tableImport = dbm.Retrieve(filename,"days",rows_required=1000)
                #days table -ID|ENTRYNAME|CREATIONDATE|CREATORID|LASTDURATION|LASTRESETDATE|LASTRESETBY|RECORDDURATION|TIMESRESET
                #creator table - ID|CREATORNAME|CREATORID
                #durations table - ID|DURATION|RESETDATE
                for row in tableImport:
                    newEntry = row[5] if row[5] is not None else row[2]
                    lastReset_DT_Object = datetime.datetime.strptime(newEntry, "%m/%d/%Y, %H:%M:%S")
                    timeDeltaDif = datetime.datetime.utcnow() - lastReset_DT_Object
                    currentLength = Helpers.timeDeltaFormat(self,timeDeltaDif)
                    #because the table cointains a str and not a list

                    if row[8] > 0:
                        recList = row[7].strip('][').split(', ')
                        output+=f"[{row[1].title()}] - {currentLength[0]}d {currentLength[1]}h | Record: {recList[0]}d {recList[1]}h \n"
                    else:
                        output+=f"[{row[1].title()}] - {currentLength[0]}d {currentLength[1]}h \n"
                output+="```"
                await ctx.send(output)

            except Exception as ex:
                logger.LogPrint(f"Print Days Error: {ex}",logging.ERROR)   
        async def DaysAdd(self,ctx,userInput):
            try:
                userName = ctx.message.author.name
                userId = (f"<@{ctx.message.author.id}>")
                creationDate = datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
                
                duplicateDays = dbm.Retrieve(filename,"days",[("EntryName",userInput)])
                duplicateCreator = dbm.Retrieve(filename,"creator",[("CreatorId",userId)])

                #if not found e.g. not exist e.g. not duplicate
                if len(duplicateDays) == 0:

                    if len(duplicateCreator) == 0:
                        dbm.Insert(filename,"creator",{"CreatorName":userName,"CreatorId":userId})
                        tableId = dbm.Retrieve(filename,"creator",["CreatorId",userId])
                    else:
                        tableId = duplicateCreator[0][0]

                    columns = {"EntryName":userInput, "CreationDate":creationDate, "CreatorId":tableId,"TimesReset":0}
                    dbm.Insert(filename,"days",columns)
                    await ctx.send(f"**{userInput}** added!")

                else:
                   await ctx.send("Duplicate Entry.")
                   #calls daysStats when that's done with the info of the duplicate

            except Exception as ex:
                logger.LogPrint(f"Error adding new Days entry: {ex}",logging.ERROR)   
        async def DaysDelete(self,ctx,userInput):
            try:
                pattern = "DELETE "
                userInput = re.split(pattern, userInput, 1)[1]
                tableImport = dbm.Retrieve(filename,"days",[("EntryName",userInput)])
                requester = ctx.message.author.id #check if format is same for elif statement
                isAdmin = ctx.message.author.permissions_in(ctx.channel).administrator == True
                isCreator = dbm.Retrieve(filename,"creator",[("Id",tableImport[0][3])]) == requester
                if not tableImport:
                    await ctx.send("Timer for deletion not found.")
                #check if creator and delete
                #i this will just find an entry with the requested id??
                elif isCreator or isAdmin:
                    deletionId = {"Id":tableImport[0][0]}
                    dbm.Delete(filename,"days", deletionId) 
                    dbm.Delete(filename,"durations", deletionId)
                    await ctx.send(f"**{userInput}** - Deleted")
                else:
                    await ctx.send("Can't delete entry - not creator or admin.")
                  
                
            except Exception as ex:
                logger.LogPrint(f"Days Delete Error: {ex}",logging.ERROR)
        async def DaysStats(self,ctx,userInput):
            await ctx.send(f"Coming Soon(tm)")

        async def DaysReset(self,ctx,id):
            try:
                userInput = Helpers.CommandStrip(self, ctx.message.content).upper()
                
                if userInput.startswith("ZERO"):
                    pattern = "ZERO "
                else:
                    pattern = "RESET "

                userInput = re.split(pattern, userInput, 1)[1]
                tableImport = dbm.Retrieve(filename,"days",[("EntryName",userInput)])
                if not tableImport:
                    await ctx.send("Timer for reset not found.")
                else:
                    #if entry has never been reset before pick creation date as last reset date and set record to 0
                    if tableImport[0][8] == 0:
                        lastReset = datetime.datetime.strptime(tableImport[0][2], "%m/%d/%Y, %H:%M:%S")
                        recordDuration = [0,0.0]
                    
                    else:
                        lastReset = datetime.datetime.strptime(tableImport[0][5], "%m/%d/%Y, %H:%M:%S")
                        recordDuration = tableImport[0][7].strip('][').split(', ')

                    currentDate = datetime.datetime.utcnow()
                    lastLength=currentDate-lastReset
                    lastLength = Helpers.timeDeltaFormat(self,lastLength)
                    #check if new record
                    if (int(lastLength[0])+float(lastLength[1])/24) >= (int(recordDuration[0])+float(recordDuration[1])/24):
                        recordDuration = lastLength
                        dbm.Update(filename, "days",{"RecordDuration": str(lastLength)}, {"id": tableImport[0][0]})
                    #check if LastResetByName is the same as current reset guy
                    currentResetter = ctx.message.author.name
                    if tableImport[0][6] is not currentResetter:
                        dbm.Update(filename, "days",{"LastResetByName": currentResetter}, {"id": tableImport[0][0]})
                    #update LastDuration and last reset date and insert new reset dates :^)
                    currentDate = currentDate.strftime("%m/%d/%Y, %H:%M:%S")
                    dbm.Update(filename, "days",{"LastResetDate": currentDate}, {"id": tableImport[0][0]})
                    dbm.Update(filename, "days",{"LastDuration": str(lastLength)}, {"id": tableImport[0][0]})
                    dictForInsert = {
                        "Id": tableImport[0][0],
                        "Duration": str(lastLength),
                        "ResetDate": currentDate,}
                    dbm.Insert(filename,"durations",dictForInsert)
                    dbm.Update(filename,"days", {"TimesReset": (tableImport[0][8]+1)}, {"id": tableImport[0][0]})
                    await ctx.send(f"```ini\n[{userInput}] - timer reset. {lastLength[0]}d {lastLength[1]}h. Record - {recordDuration[0]}d {recordDuration[1]}h.```")

            except Exception as ex:
                logger.LogPrint(f"Days Reset Error: {ex}",logging.ERROR) 

        try:
            
            await CheckAndCreateDatabase(self,ctx)

            userInput = Helpers.CommandStrip(self, ctx.message.content).upper()
            #print all entries
            if userInput == "":
               await PrintDays(self,ctx)
            #reset a timer
            elif userInput.startswith("ZERO") or userInput.startswith("RESET"):
                await DaysReset(self,ctx,userInput)
            #delete a timer and all connected entries except in creator
            elif userInput.startswith("DELETE"):
                await DaysDelete(self,ctx,userInput)            
            #print one entry with expanded stats
            elif userInput.startswith("STATS"):
                await DaysStats(self,ctx,userInput)
            #add new entry
            elif len(userInput) > 0:
                await DaysAdd(self,ctx,userInput) 
            else:
                await ctx.send(f"Ha Ha this must never be printed, if you see this yell at Jim")  

        except Exception as ex:
            logger.LogPrint(f"General Days Error: {ex}",logging.ERROR)    


def setup(client):
    client.add_cog(cliffnet(client))
