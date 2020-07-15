from credentials import vk_raccoon_bot_token, vk_personal_audio_token, discord_user_token
from vk_botting import bot

from anilist import *
# from mangatown import *
from trello import *
from todo import *

racc = bot.Bot(command_prefix=bot.when_mentioned_or_pm_or('!'), case_insensitive=True)


@racc.listen()
async def on_ready():
    print(f'Logged in as {racc.group.name}')
    # mangatown_setup(racc)
    anilist_setup(racc)
    trello_setup(racc)
    todo_setup(racc)
    await racc.attach_user_token(vk_personal_audio_token)


@racc.command(name='ping')
async def ping_(ctx):
    ts = time()
    msg = await ctx.reply('Pong!')
    tm = (time() - ts) * 1000
    return await msg.edit('{:.2f}ms'.format(tm))


@racc.command(name='status', aliases=['s'])
@in_user_list(vk_personal_user_id)
async def change_status(ctx, *, status):
    headers = {'Authorization': discord_user_token, 'Content-Type': 'application/json'}
    body = f"""{{"custom_status": {{"text": "{status}",
"expires_at": null,
"emoji_id": null,
"emoji_name": null}}}}"""
    await racc.session.patch('https://discordapp.com/api/v6/users/@me/settings', headers=headers, data=body.encode('utf-8'))
    await racc.user_vk_request('status.set', text=status)
    return await ctx.reply(f'Статус "{status}" установлен!')


@racc.command(name='return', aliases=['reset', 'r'])
@in_user_list(vk_personal_user_id)
async def reset_status(ctx):
    headers = {'Authorization': discord_user_token, 'Content-Type': 'application/json'}
    body = f"""{{"custom_status": {{"text": null,
"expires_at": null,
"emoji_id": null,
"emoji_name": null}}}}"""
    await racc.session.patch('https://discordapp.com/api/v6/users/@me/settings', headers=headers, data=body.encode('utf-8'))
    await racc.user_vk_request('status.set', text='В активном поиске тайтлов')
    return await ctx.reply(f'Статусы сброшены!')


@racc.command(name='выполни', aliases=['eval', 'exec'])
@in_user_list(vk_personal_user_id)
async def exec_(ctx, *, code):
    exec(
        f'async def __ex(ctx): ' +
        ''.join(f'\n    {line}' for line in code.split('\n'))
    )
    result = await locals()['__ex'](ctx)
    if result is None:
        result = ':)'
    return await ctx.send(result)


racc.run(vk_raccoon_bot_token)
