import requests
import discord
from discord.ext import commands
import sqlite3
from discord_components import Button,DiscordComponents,ButtonStyle

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.' , intents = intents)

token = ''

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

conn = sqlite3.connect("osubot.db")
cursor = conn.cursor()

def data():
    cursor.execute("""CREATE TABLE "users" (
                "id"	INT,
                "nickname"	TEXT,
                "mention"	TEXT,
                "account"	TEXT,
                "steam"  TEXT,
                "osu"  TEXT,
                "pp"  INT
            )""")
    conn.commit()
#---data()---
#     ^
#     |
#     |
#Remove comment if there is no database

def get_token():
    data = {
        'client_id': '',
        'client_secret': '',
        'grant_type': 'client_credentials',
        'scope': 'public'
    }

    response = requests.post(TOKEN_URL, data=data)

    return response.json().get('access_token')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        print(guild.id)
        serv=guild
        for member in guild.members:
            cursor.execute(f"SELECT id FROM users where id={member.id}")
            if cursor.fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>','S','S','S',0)")
            else:
                pass
            conn.commit()

@bot.command()
async def add(ctx ,service,teg):
    uid = ctx.author.id

    if service == "osu":
        if cursor.execute(f"UPDATE users SET osu=? where id=?", (teg,uid)):
            await ctx.send(f"[LOG] ADD osu PROFILE")
        else:
            await ctx.send(f"[LOG] NOT ADD ACCOUNT")
    else:
        await ctx.send(f"[LOG] ШО ЗА ХУЙНЯ ???")
    conn.commit()

@bot.command()
async def account(ctx):

    for row in cursor.execute(f"SELECT nickname,pp,account,osu FROM users where id={ctx.author.id}"):
        embed = discord.Embed(title="Данные:", color=discord.Color.red())
        embed.add_field(name=ctx.author.name,value=ctx.author.id,inline=False)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(
            embed = embed,
            components = [
                Button(style=ButtonStyle.URL, label="OSU", url="https://osu.ppy.sh/users/" + row[3])
            ]
        )

@bot.command()
async def info_players(ctx, id):
    token = get_token()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'mode': 'osu',
        'limit': 5
    }

    response = requests.get(f'{API_URL}/users/{id}', params=params, headers=headers)

    beatmapset_data = response.json()
    avatar = beatmapset_data['avatar_url']
    pp = beatmapset_data['statistics']['pp']
    id = beatmapset_data['id']
    embed = discord.Embed(title='osu', color=discord.Color.red())
    embed.add_field(name='URL', value=f'https://osu.ppy.sh/users/{id}', inline=False)
    embed.add_field(name='PP', value=pp, inline=False)
    embed.set_thumbnail(url=avatar)
    await ctx.send(embed=embed)

bot.run(token)
