import asyncio
import discord
from discord import message
from discord.ext import commands
from dotenv import load_dotenv
import os


# load Environment variables
load_dotenv()


# Define connection to discord
client = commands.Bot(command_prefix="!")


# Scores keeps track of the highest count guilds have reached
scores = {}


# When the bot is connected to discord it will print that it has logged in
@client.event
async def on_ready():
    print(f"{client.user} has logged in")


async def count_restart(message, messages):

    # from the message server the announcement channel is found
    channel = discord.utils.get(message.guild.channels, name="count")
    if channel is None:
        channel = await message.guild.create_text_channel("count")

    # all the messages are deleted
    await message.channel.purge()
    await asyncio.sleep(1)

    # We find the author of the user that lost the count
    author = message.author

    # In the announcements channel we tell the server where and who lost the count
    await channel.send(
        f"@everyone {author.mention} has messed up the count bot at {messages[-1].content}!",
    )
    await channel.send("~")

    # Then to start the count the bot send one in to th channel
    # Otherwise when anyone types one the bot would delete it
    await message.channel.send("1")

    # Updates high score for guild
    if (f"{channel.guild.name}") in scores:
        if messages[-1].content > scores[f"{message.guild.name}"]:
            scores[f"{message.guild.name}"] = messages[-1].content

    else:
        scores[f"{message.guild.name}"] = messages[-1].content


# This code is ran when discord detects a message
@client.event
async def on_message(message):

    # If the name of the channel is count we search for mistakes
    if message.channel.name.startswith("count"):

        # Creates a list of the last two messages in the count channel history
        messages = await message.channel.history(limit=2).flatten()

        # If the last message was from the bot itself nothing will happen
        if message.author == client.user:
            pass

        # If the message is not numeric the count restarts
        elif not str(message.content).isnumeric():
            await count_restart(message, messages)

        # If the last message author is the same as second last author the count restarts
        elif message.author == messages[-1].author:
            await count_restart(message, messages)

        # If the new message is not one more than the second last message the count restarts
        elif int(message.content) - 1 != int(messages[-1].content):
            await count_restart(message, messages)

            scores[messages[-1].author] = int(messages[-1].content)

    # If the message is not in the count channel, This checks if it is a command
    else:
        await client.process_commands(message)


# This code is ran when a message is edited
@client.event
async def on_message_edit(before, after):

    # If the name of the channel is count we search for mistakes
    if str(after.channel) == "count":
        messages = await message.channel.history(limit=2).flatten()
        await count_restart(after, messages)


# When the command !startcount is called it will create a channel count
@client.command()
async def start_count(ctx):

    channel = await ctx.guild.create_text_channel("count")

    # To setup the channel the bot sends a one and makes sure users can only message every ten seconds
    await channel.send("1")
    await channel.edit(slowmode_delay=10)


@client.command()
async def all_server_highscore(ctx):

    keys = list(scores.keys())
    values = list(scores.values())
    score = max(values)
    guild = keys[values.index(score)]
    await ctx.send(f"{guild}: {score}")


@client.command()
async def server_highscore(ctx):

    # this returns the guilds high score
    await ctx.send(f"Your guilds highest count was {scores[ctx.guild.name]}")


@client.command()
async def countbothelp(ctx):

    await ctx.send("!start_count, !server_highscore, !all_server_highscore")


client.run(os.getenv("TOKEN"))
