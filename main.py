import discord
import os
from discord.ext import commands
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionNotLoaded

intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents)

TOKEN = "<Your discord bot token>"
OWNER_ID = "<Your discord id>"

@client.event
async def on_ready():
    print("Bot is online")

async def is_owner(ctx):
    return ctx.author.id == OWNER_ID

@client.command()
@commands.check(is_owner)
async def load(ctx, extension):
    try:
        client.load_extension(f"cogs.{extension}")
        print(f"Loaded {extension}")
    except ExtensionAlreadyLoaded as e:
        print(e)

@client.command()
@commands.check(is_owner)
async def unload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        print(f"Unloaded {extension}")
    except ExtensionNotLoaded as e:
        print(e)
    
@client.command()
@commands.check(is_owner)
async def reload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        print(f"Reloaded {extension}")
    except ExtensionNotLoaded as e:
        print(e)

@client.command(aliases= ["r"])
@commands.check(is_owner)
async def reload_all(ctx):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.unload_extension(f"cogs.{filename[:-3]}")
            client.load_extension(f"cogs.{filename[:-3]}")
    print("Reloaded all extensions")

@client.command()
@commands.check(is_owner)
async def cls(ctx):
    os.system("cls" if os.name == "nt" else "clear")

@client.command()
@commands.check(is_owner)
async def extensions(ctx):
    extensions = [extension[5:] for extension in client.extensions.keys()]
    await ctx.send("Available extensions: \n" + "\n".join(extensions))


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")
        print(f"Cog: {filename[:-3]} loaded")

client.run(TOKEN)