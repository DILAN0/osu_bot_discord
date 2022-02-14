import requests
import discord
from discord.ext import commands
import sqlite3, sys
from discord_components import Button,ButtonStyle
import time
from Token import key
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.' , intents = intents)

token = key

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
#----data()
#     ^
#     |
#     |
#Remove comment if there is no database

def get_token():
    data = {
        'client_id': '10055',
        'client_secret': 'S1q6W4jw3LQF5plV5bnxtSTXL9x3wy705BSL76hy',
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
            await ctx.send(f"[LOG] ADD OSU PROFILE")
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
        embed.add_field(name="URL", value=f"https://osu.ppy.sh/users/{row[3]}", inline=False)

        await ctx.send(
            embed = embed,
        )

@bot.command()
#информация о игроке
async def info_player(ctx, id):
    #Создаем экземпляр token который забирает в себя функцию
    token = get_token()
    #.....
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'mode': 'osu',#https://osu.ppy.sh/docs/index.html #gamemode
        'limit': 5 #Maximum number of results
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

@bot.event
async def on_member_update(prev, cur):
    role = discord.utils.get(cur.guild.roles, name="Gamer")
    games = ["osu!"]

    if cur.activity.name in games and cur.activity.details:
        channel = bot.get_channel(792491223495606352)
        embed = discord.Embed(title=f"Changed status")
        embed.add_field(name='User', value=cur.activity.assets['large_text'].split('(', 1)[0])
        embed.add_field(name='Play', value=cur.activity.details)

        await channel.send(embed=embed)
    elif prev.activity and prev.activity.name.lower() in games and not cur.activity:
            if role in cur.roles:
                await cur.remove_roles(role)



# @bot.event
# async def on_member_update(ctx,cur):
#     games = ["osu!"]
#     uid = cur.id
#     id_osu=cur.activity.assets['large_text'].split('(', 1)[0]
#
#     if search and cur.activity.name in games and cur.activity.details:
#         if cursor.execute(f"UPDATE users SET osu=? where id=?", (id_osu, uid)):
#             await cur.send("ADD ID OSU")
#         else:
#             await cur.send('ERROR')
#     else:
#         pass

@bot.event
async def osu_data(ctx,cur):
    try:
       uid = cur.id

       id_osu=cur.activity.assets['large_text'].split('(', 1)[0]

       for row in cursor.execute(f"SELECT nickname,pp,account,osu FROM users where id={cur.id}"):
            queue = []
            if row[3] != 'S':
                break
            else:
               games = ["osu!"]
               if cur.activity.name in games and cur.activity.details:
                   if cursor.execute(f"UPDATE users SET osu=? where id=?", (id_osu, uid)):
                       queue.append(row[3])
                       await cur.send("ADD ID OSU")

                       conn.commit()
                   else:
                       await cur.send('ERROR')
            conn.commit()
    except:
        print("[log] AttributeError")

@bot.event
async def osu_submit(ctx,cur):

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    params = (
        ('mode', 'voluptas'),
        ('mods', 'sed'),
    )

    response = requests.get('https://osu.ppy.sh/api/v2/beatmaps/869019/scores/users/23764407', headers=headers, params=params)
    channel = bot.get_channel(792491223495606352)
    await channel.send(response)




# @bot.event
# async def on_member_update(before, after):
#     if before.status != after.status:  # работать только на статусе
#         embed = discord.Embed(title=f"Changed status")
#         embed.add_field(name='User', value=before.mention)
#         embed.add_field(name='Before', value=before.status)
#         embed.add_field(name='After', value=after.status)
#         channel = bot.get_channel(792491223495606352)  # id канала для уведомлениях изменений в профиле
#         await channel.send(embed=embed)
#         admin = bot.get_user(332932417520402434)  # id пользователя (выполнение проверки по id)
#         await admin.send(embed=embed)

bot.run(token)
