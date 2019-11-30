from anilist import *
from trello import *
from mangatown import *

from vk_botting.ext import bot
from credentials import vkRaccoonBotKey
from time import time
import asyncio

racc = bot.Bot(token=vkRaccoonBotKey, command_prefix=bot.when_mentioned_or('!'))


@racc.listen()
async def on_ready():
    print(f'Logged in as {racc.group.name}')
    loop = asyncio.get_event_loop()
    loop.create_task(update_manga())
    loop.create_task(al_check())
    loop.create_task(update_rss())
    loop.create_task(asyncio.start_server(trello_socket, '', 9083))


@racc.command(name='ping', pass_context=True, help='Команда для проверки жизнеспособности бота', usage='{}ping')
async def ping_(ctx):
    ts = time()
    msg = await ctx.reply('Pong!')
    tm = (time() - ts) * 1000
    return await msg.edit('{:.2f}ms'.format(tm))


racc.run()
