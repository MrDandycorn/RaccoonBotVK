import requests
from credentials import vkRaccoonBotKey


def vkMsg(peer_id, msg=None, attach=None):
    payload = {'access_token': vkRaccoonBotKey, 'v': '5.80',
               'message': msg,
               'peer_id': peer_id,
               'attachment': attach}
    res = requests.post('https://api.vk.com/method/messages.send', data=payload).json()
    return res


