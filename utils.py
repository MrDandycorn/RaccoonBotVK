import httpx
from credentials import vkRaccoonBotKey


async def vkMsg(peer_id, msg=None, attach=None):
    payload = {'access_token': vkRaccoonBotKey, 'v': '5.80',
               'message': msg,
               'peer_id': peer_id,
               'attachment': attach}
    async with httpx.AsyncClient() as client:
        res = await client.post('https://api.vk.com/method/messages.send', data=payload)
    return res.json()
