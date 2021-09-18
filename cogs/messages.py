from discord.ext import commands


class Messages(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["clean", "c"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount:int):
        await ctx.channel.purge(limit=amount + 1)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = "Amount of messages must be integer number"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "Missing required argument"
            await ctx.send_help(self.clear)
        else:
            message = "Something went wrong"
        await ctx.send(message)


def setup(client):
    client.add_cog(Messages(client))