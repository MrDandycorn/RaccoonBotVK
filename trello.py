import socket
from json import loads
from credentials import trello_key, trello_token, vkPersUserID
from utils import *


def get_list(lid):
    params = {
        'key': trello_key,
        'token': trello_token
    }
    lst = requests.get(f'https://api.trello.com/1/lists/{lid}/name', params=params).json()
    return lst['_value']


def trello_socket():
    while True:
        try:
            s = socket.socket()
            s.bind(('', 9083))
            print('Trello socket running!')
            s.listen(5)
            while True:
                try:
                    c, (client_host, client_port) = s.accept()
                    if client_host in ['107.23.104.115', '107.23.149.70', '54.152.166.250', '54.164.77.56', '54.209.149.230']:
                        data = c.recv(1024)
                        while not data.endswith(b'}'):
                            data += c.recv(1024)
                        c.send(b'HTTP/1.1 200 OK\n')
                        c.send(b'Content-Type: text/html\n')
                        c.send(b'\n')
                        data, json = data.decode("utf-8").split('{', 1)
                        json = loads('{'+json)
                        action = json['action']
                        name = action['memberCreator']['fullName']
                        if action['type'] == 'updateCard':
                            data = action['data']
                            changed = list(data["old"].keys())[0]
                            old = data["old"][changed]
                            card = data["card"]
                            cname = card['name']
                            if changed == 'idList':
                                msg = f'{name} переместил карту "{cname}" из списка {get_list(old)} в {get_list(card[changed])}'
                            elif changed == 'name':
                                msg = f'{name} изменил название карты "{old}" на "{card[changed]}"'
                            elif changed == 'closed':
                                msg = f'{name} архивировал карту "{old}"' if card[changed] else f'{name} деархивировал карту "{old}"'
                            else:
                                msg = f'{name} изменил поле {changed} карты "{cname}" на {card[changed]}'
                        elif action['type'] == 'deleteCard':
                            ents = action["display"]["entities"]
                            msg = f'{name} удалил карту №{ents["idCard"]["text"]} из списка {ents["list"]["text"]}'
                        elif action['type'] == 'commentCard':
                            data = action['data']
                            msg = f'{name} Оставил комментарий на карте "{data["card"]["name"]}":\n{data["text"]}'
                        else:
                            msg = f'Новое уведомление из Trello:\nТип: {action["type"]}\nJson: {str(action["display"])}'
                        vkMsg(vkPersUserID, msg)
                    c.close()
                except Exception as e:
                    print(f'Произошла ошибка: {e}')
        except Exception as e:
            print(f'Произошла ошибка: {e}')

