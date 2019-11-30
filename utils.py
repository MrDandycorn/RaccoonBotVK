import aiohttp
from credentials import vkRaccoonBotKey


async def vkMsg(peer_id, msg=None, attach=None):
    payload = {'access_token': vkRaccoonBotKey, 'v': '5.80',
               'message': msg,
               'peer_id': peer_id,
               'attachment': attach}
    async with aiohttp.ClientSession() as session:
        res = await session.post('https://api.vk.com/method/messages.send', data=payload)
        return await res.json()
