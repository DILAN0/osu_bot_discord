import requests
import discord
from discord.ext import commands
import sqlite3
from Token import key
from res.token_func import get_token, response
from res.create_data import check_file
import os

check_file()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.' , intents = intents)

token = key

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

conn = sqlite3.connect("osubot.db")
cursor = conn.cursor()


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
        pp,id,avatar = response(id = row[3])
        embed = discord.Embed(title="Данные:", color=discord.Color.from_rgb(255,102,170))
        embed.add_field(name=ctx.author.name,value=ctx.author.id,inline=False)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="OSU", value=f"https://osu.ppy.sh/users/{id}", inline=False)
        embed.add_field(name="PP", value=pp, inline=False)
        await ctx.send(embed = embed)

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
    embed = discord.Embed(title='osu', color=discord.Color.from_rgb(255,102,170))
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
async def on_member_update(ctx,cur):
    try:
        uid = cur.id

        id_osu=cur.activity.assets['large_text'].split('(', 1)[0]

        for row in cursor.execute(f"SELECT nickname,pp,account,osu FROM users where id={cur.id}"):
                if row[3] != 'S':
                    break
                else:
                    games = ["osu!"]
                    if cur.activity.name in games and cur.activity.details:
                        if cursor.execute(f"UPDATE users SET osu=? where id=?", (id_osu, uid)):

                            await cur.send(f"✔ Your OSU Account Add {cur.activity.assets['large_text']}")

                        else:
                            await cur.send('ERROR')
        conn.commit()

    except AttributeError:
        print(f"[log] AttributeError {cur.name}")
    except:
        print(f"[log] Other ERROR {cur.name}")


@bot.command()
async def score(ctx,type,offset):
    for row in cursor.execute(f"SELECT nickname,pp,account,osu FROM users where id={ctx.author.id}"):
        token = get_token()
        pp,id,avatar = response(id = row[3])
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        params = (
            ('include_fails', '0'),
            ('mode', 'osu'),
            ('limit', '1'),
            ('offset', f'{offset}'),
        )

        res = requests.get(f'https://osu.ppy.sh/api/v2/users/{id}/scores/{type}', headers=headers, params=params)
        score_assets = res.json()

        pp = score_assets[0]["pp"]
        if score_assets[0]['rank'] == 'D':
            image_rank = "https://i.ppy.sh/7fd069c3993d08d4fbdb8c80c7357faf417c5444/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d442e706e67"
        if score_assets[0]['rank'] == 'A':
            image_rank = "https://i.ppy.sh/8b9333010fbabc4d8b8c70631f64f380f945d72c/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d412e706e67"
        if score_assets[0]['rank'] == 'S':
            image_rank = "https://i.ppy.sh/c38cbe3dfb6c777952a0d72a6c20ea99d7e59273/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d532e706e67"
        if score_assets[0]['rank'] == 'B':
            image_rank = "https://i.ppy.sh/92d05e580ff9e91a11eddce8628fda602f2fab45/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d422e706e67"
        if score_assets[0]['rank'] == 'C':
            image_rank = "https://i.ppy.sh/9c365dc75bb0aefcd1c00d63eac9058111b07c80/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d432e706e67"
        if score_assets[0]['rank'] == 'X':
            image_rank = "https://i.ppy.sh/3d368b40d15d55a0e737ac16c48b4cb2928c6af8/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d582e706e67"
        if score_assets[0]['rank'] == 'SH':
            image_rank = "https://i.ppy.sh/69da4fffac88a4c6183477d4df33e14f8173fab4/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d53482e706e67"
        if score_assets[0]['rank'] == 'XH':
            image_rank = "https://i.ppy.sh/77981a1d357411d2e3f5cb0d04d232010d51ecbd/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f536b696e6e696e672f496e746572666163652f696d672f72616e6b696e672d58482e706e67"

        embed = discord.Embed(title=f"{score_assets[0]['beatmapset']['title']} ({score_assets[0]['beatmap']['version']}) {score_assets[0]['mods']}", url=score_assets[0]['beatmap']['url'] ,color=discord.Color.from_rgb(255, 102, 170))
        embed.set_image(url=f"{score_assets[0]['beatmapset']['covers']['cover']}")
        embed.set_thumbnail(url=image_rank)
        embed.add_field(name="►Score:", value=f"https://osu.ppy.sh/scores/osu/{score_assets[0]['best_id']}", inline=False)
        embed.set_author(name=f"{score_assets[0]['user']['username']}",icon_url=avatar,url=f"https://osu.ppy.sh/users/{id}")
        embed.add_field(name=f'►Accuracy: ',value=f"{float(round((score_assets[0]['accuracy']) * 100)) }%", inline=True)
        if score_assets[0]['perfect'] == True:
            embed.add_field(name='►Combo:', value="FC", inline=True)
        else:
            embed.add_field(name='►Combo:',value=score_assets[0]['max_combo'],inline=True)

        embed.add_field(name='►Performance:' ,value=f"{pp} pp", inline=True)

        embed.set_footer(text=f"{score_assets[0]['created_at']}", icon_url='https://img.icons8.com/clouds/344/osu.png')


        await ctx.send(embed = embed)

@bot.command()
async def replay(ctx):
    os.system('D:\Project\osu-discord-bot\danser--go\danser.exe -t="Ashes of the Dawn" -d="Expert" -replay="D:\GAmes\osu!\Replays\DILAN_NAXUY - DragonForce - Ashes of the Dawn [Expert] (2022-03-08) Osu.osr" -record')

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
