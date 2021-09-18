import discord
import bs4
import requests
from matplotlib import pyplot as plt
from discord.ext import commands

levels = {2: 801, 3: 951, 4: 1101, 5: 1251, 6: 1401, 7: 1551, 8: 1701, 9: 1851, 10: 2001}

class Faceit(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    def fclevel(self, elo: int):
        url = "https://eloboss.net/static/boost/ELO_"
        if elo <= 800:
            return url + "1.png"
        if elo >= 801 and elo <= 950:
            return url + "2.png"
        if elo >= 951 and elo <= 1100:
            return url + "3.png"
        if elo >= 1101 and elo <= 1250:
            return url + "4.png"
        if elo >= 1251 and elo <= 1400:
            return url + "5.png"
        if elo >= 1401 and elo <= 1550:
            return url + "6.png"
        if elo >= 1551 and elo <= 1700:
            return url + "7.png"
        if elo >= 1701 and elo <= 1850:
            return url + "8.png"
        if elo >= 1851 and elo <= 2000:
            return url + "9.png"
        if elo >= 2001:
            return url + "10.png"
    
    def levelcolor(self, elo: int):
        if elo <= 800:
            return 0xEEEEEE
        if elo >= 801 and elo <= 1100:
            return 0x1CE400
        if elo >= 1101 and elo <= 1700:
            return 0xFFC800
        if elo >= 1701 and elo <= 2000:
            return 0xFF6309
        if elo >= 2001:
            return 0xFE1F00

    def lastmatches(self, lm: list):
        green_circle = "\U0001F7E2"
        red_circle = "\U0001F534"
        output = [green_circle if letter == "W" else red_circle for letter in lm][1:-1]
        return " ".join(output)
    
    def graph(self, elo_list: list):
        output = []
        for level, elo in levels.items():
            if len(elo_list) != 0:
                if min(elo_list) <= elo <= max(elo_list):
                    output.append((level, elo))
        return output

    def bs(self, player):
        res = requests.get(f"https://faceitstats.com/player/{player}")
        soup = bs4.BeautifulSoup(res.text, "lxml")
        faceitlink = soup.find("a", text="Details").get("href")
        res = requests.get(f"https://faceitstats.com{faceitlink}")
        soup1 = bs4.BeautifulSoup(res.text, "lxml")
        a_tags = soup1.find_all("a")
        for tag in a_tags:
            if tag.get_text().lower() == player.lower():
                faceitnick = tag.get_text()
        return soup, faceitnick

    @commands.command()
    async def faceit(self, ctx, player: str):
        with ctx.channel.typing():
            soup, faceitnick = await self.client.loop.run_in_executor(None, self.bs, player)
            stats = soup.select("h5")
            elo = int(stats[0].get_text()) 
            steamlink = soup.find("a", rel="noopener noreferrer").get("href")
            pic_url = soup.find("img", class_="rounded").get("src")
            ranks = soup.find_all("span", class_="badge-primary", limit=2)
            country_rank = ranks[0].get_text()
            country_rank_emoji = ranks[0].find("img").get("src")[-6:-4]
            region_rank = ranks[1].get_text()
            region_rank_emoji = ranks[1].find("img").get("src")[-6:-4]
            match_history = soup.find("tbody").find_all("tr")
            wl = soup.find("span", class_= "recentLW").get_text().split("\n")
            elo_history = [match.find_all("td")[-2].get_text().strip().split()[0]
                            for match in match_history]
            elo_history = [int(value) for value in elo_history if value.isdigit()][::-1]
            embed = discord.Embed(
                title=(f":flag_{country_rank_emoji}: {faceitnick}"),
                color=self.levelcolor(elo),
                description=f"[Steam profile]({steamlink})      \
                    [Faceit profile](https://faceit.com/en/players/{faceitnick})"
            )
            embed.add_field(name="Matches/Won/Lost:", value=stats[1].get_text())
            embed.add_field(name="Win rate:", value=stats[2].get_text())
            embed.add_field(name="K/D:", value=stats[3].get_text())
            embed.add_field(name="Avg HS%:", value=stats[4].get_text())
            embed.add_field(name="Last 5 Games:", value=self.lastmatches(wl))
            embed.add_field(name="Current win streak:", value=stats[-1].get_text())
            embed.add_field(name="Longest win streak:", value=stats[5].get_text())
            embed.add_field(name="Country rank:", value=f":flag_{country_rank_emoji}: {country_rank}")
            embed.add_field(name="Region rank:", value=f":flag_{region_rank_emoji}: {region_rank}")
            embed.set_footer(text=f"ELO: {elo}", icon_url=self.fclevel(elo))
            embed.set_thumbnail(url=pic_url)
            if len(elo_history) >= 2:
                plt.plot(list(range(len(elo_history))), elo_history, color="#FFA500", marker=".")
                plt.title(f"Last {len(elo_history)} matches")
                plt.ylabel("ELO")
                plt.grid(True)
                cax = plt.gca()
                cax.axes.xaxis.set_ticklabels([])
                for item in self.graph(elo_history):
                    plt.axhline(item[1], color="green", label=f"level {item[0]}", linewidth=2, alpha=0.6)
                plt.legend(loc="upper left")
                plt.savefig("additional_items/faceit.png")
                plt.cla()
                file = discord.File("additional_items/faceit.png")
            else:
                file = None
            if file:
                await ctx.send(embed=embed, file=discord.File("additional_items/faceit.png"))
            else:
                await ctx.send(embed=embed)
    
    @faceit.error
    async def faceit_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.CommandInvokeError):
            message = "Player not found"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "Missing required argument"
            await ctx.send_help(self.faceit)
        else:
            message = "Something went wrong"
        await ctx.send(message)
        

def setup(client):
    client.add_cog(Faceit(client))