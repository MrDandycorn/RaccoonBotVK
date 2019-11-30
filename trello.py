from json import loads
from credentials import trello_key, trello_token, vkPersUserID
from utils import *
import httpx


async def get_list(lid):
    params = {
        'key': trello_key,
        'token': trello_token
    }
    async with httpx.AsyncClient() as client:
        lst = await client.get(f'https://api.trello.com/1/lists/{lid}/name', params=params)
        lst = lst.json()
    return lst['_value']


async def trello_socket(reader, writer):
    while True:
        data = await reader.read(1024)
        while not data.endswith(b'}'):
            data += await reader.read(1024)
        if data:
            sock = writer.get_extra_info('socket')
            client_host, client_port = sock.getpeername()
            if client_host in ['107.23.104.115', '107.23.149.70', '54.152.166.250', '54.164.77.56', '54.209.149.230']:
                writer.writelines([b'HTTP/1.1 200 OK\n', b'Content-Type: text/html\n', b'\n'])
                data, json = data.decode("utf-8").split('{', 1)
                json = loads('{' + json)
                action = json['action']
                name = action['memberCreator']['fullName']
                if action['type'] == 'updateCard':
                    data = action['data']
                    changed = list(data["old"].keys())[0]
                    old = data["old"][changed]
                    card = data["card"]
                    cname = card['name']
                    if changed == 'idList':
                        old = await get_list(old)
                        new = await get_list(card[changed])
                        msg = f'{name} переместил карту "{cname}" из списка {old} в {new}'
                    elif changed == 'name':
                        msg = f'{name} изменил название карты "{old}" на "{card[changed]}"'
                    elif changed == 'closed':
                        msg = f'{name} архивировал карту "{old}"' if card[changed] else f'{name} деархивировал карту "{old}"'
                    else:
                        msg = f'{name} изменил поле {changed} карты "{cname}" на {card[changed]}'
                elif action['type'] == 'deleteCard':
                    ents = action['display']['entities']
                    msg = f'{name} удалил карту №{ents["idCard"]["text"]} из списка {ents["list"]["text"]}'
                elif action['type'] == 'commentCard':
                    data = action['data']
                    msg = f'{name} оставил комментарий на карте "{data["card"]["name"]}":\n{data["text"]}'
                elif action['type'] == 'createCard':
                    ents = action['display']['entities']
                    msg = f'{name} создал карту "{ents["card"]["text"]}" в списке {ents["list"]["text"]}'
                elif action['type'] == 'addMemberToBoard':
                    ents = action['display']['entities']
                    msg = f'{ents["memberInviter"]["text"]} пригласил {ents["memberCreator"]["text"]} в доску'
                elif action['type'] == 'makeAdminOfBoard':
                    ents = action['display']['entities']
                    msg = f'{ents["memberCreator"]["text"]} назначил {ents["member"]["text"]} администратором доски'
                elif action['type'] == 'makeNormalMemberOfBoard':
                    ents = action['display']['entities']
                    msg = f'{ents["memberCreator"]["text"]} назначил {ents["member"]["text"]} обычным участником доски'
                else:
                    msg = f'Новое уведомление из Trello:\nТип: {action["type"]}\nJson: {str(action["display"])}'
                await vkMsg(vkPersUserID, msg)
