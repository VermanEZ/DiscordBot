import discord
from discord.ext import commands
from datetime import datetime
import sqlite3

class Users(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    def status(self, status):
        if str(status) == "online":
            return "https://emoji.gg/assets/emoji/9166_online.png"
        if str(status) == "offline":
            return "https://emoji.gg/assets/emoji/3191_invisible.png"
        if str(status) == "dnd":
            return "https://emoji.gg/assets/emoji/7907_DND.png"
        if str(status) == "idle":
            return "https://emoji.gg/assets/emoji/3929_idle.png"

    @commands.command()
    async def user(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author
        roles = ", ".join([role.name for role in user.roles[1::]][::-1])
        embed = discord.Embed(
            title = "{}#{}".format(user.name, user.discriminator),
            color = user.roles[-1].color
        )
        embed.set_thumbnail(url=user.avatar_url)
        if len(roles) != 0:
            embed.add_field(name="Roles:", value=roles)
        else:
            embed.add_field(name="Roles:", value="No roles")
        for activity in user.activities:
            if str(activity.type) == "ActivityType.playing":
                embed.add_field(name="Playing:", value=activity.name, inline=False)
            if str(activity.type) == "ActivityType.listening":
                embed.add_field(name="Listening to:", value=f"{activity.title} - {activity.artist}", inline=False)
        embed.set_footer(text=f"Status: {str(user.status).capitalize()}", icon_url=self.status(user.status))
        await ctx.send(embed=embed)
    
    @user.error
    async def user_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            print(error)

    @commands.command()
    async def lastonline(self, ctx, *, member: discord.Member):
        if str(member.status) != "offline":
            await ctx.send(f"{member} is currently online")
        else:
            db = sqlite3.connect("additional_items/users.db")
            cursor = db.cursor()
            output = list(cursor.execute(f"SELECT name, discriminator, lastonline FROM users WHERE id = '{member.id}'"))
            if output:
                name, discriminator, lastonline = output[0]
                await ctx.send(f"{name}#{discriminator} was online at {lastonline}")
            else:
                raise Exception
    
    @lastonline.error
    async def lastonline_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            message = error
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "Missing required argument"
            await ctx.send_help(self.lastonline)
        elif isinstance(error, Exception):
            message = "User hasn't been online for too long"
        else:
            message = "Something went wrong"
        await ctx.send(message)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if str(after.status) == "offline" and str(before.status) != "offline":
            db = sqlite3.connect("additional_items/users.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT id FROM users WHERE id = {after.id}")
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", 
                              (after.name, after.discriminator, str(after.id), str(datetime.now())[:-7])
                )
                db.commit()
                print("Added new user", after.name)
            else:
                cursor.execute(f"UPDATE users SET lastonline = '{str(datetime.now())[:-7]}' WHERE id = '{after.id}'")
                db.commit()
                print("Updated", after.name)
        if str(after.status) != "offline" and str(before.status) == "offline":
            db = sqlite3.connect("additional_items/users.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT id FROM users WHERE id = {after.id}")
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", 
                              (after.name, after.discriminator, str(after.id), "online")
                )
                db.commit()
                print("Added new user", after.name)
            else:
                cursor.execute(f"UPDATE users SET lastonline = 'online' WHERE id = '{after.id}'")
                db.commit()
                print("Updated", after.name)


    @commands.command()
    async def avatar(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(member.avatar_url)
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} has joined a server ({member.guild})")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f"{member} has left a server ({member.guild})")

def setup(client):
	client.add_cog(Users(client))