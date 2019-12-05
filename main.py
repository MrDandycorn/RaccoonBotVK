from anilist import *
from trello import *
from mangatown import *

from vk_botting import bot
from credentials import vkRaccoonBotKey
from time import time

racc = bot.Bot(token=vkRaccoonBotKey, command_prefix=bot.when_mentioned_or_pm_or('!'))


@racc.listen()
async def on_ready():
    print(f'Logged in as {racc.group.name}')
    mangatown_setup(racc)
    anilist_setup(racc)
    trello_setup(racc)


@racc.command(name='ping', pass_context=True, help='Команда для проверки жизнеспособности бота', usage='{}ping')
async def ping_(ctx):
    ts = time()
    msg = await ctx.reply('Pong!')
    tm = (time() - ts) * 1000
    return await msg.edit('{:.2f}ms'.format(tm))


racc.run()
