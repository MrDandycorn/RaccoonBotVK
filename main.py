from anilist import *
from trello import *
from multiprocessing import Process
from credentials import vkRaccoonBotID, vkPersUserID
from time import sleep

server = ''
key = ''
token = ''


def handleUpdate(update):
    if update['type'] == 'message_new':
        if update['object']['from_id'] == int(vkPersUserID):
            pass


def getLongPollServer():
    global server, key
    url = 'https://api.vk.com/method/groups.getLongPollServer'
    payload = {'access_token': vkRaccoonBotKey, 'v': '5.80',
               'group_id': vkRaccoonBotID}
    res = requests.get(url, params=payload).json()
    print('Запущена сессия LongPoll')
    tempdict = res['response']
    key = tempdict['key']
    server = tempdict['server'].replace('\/', '/')
    ts = tempdict['ts']
    return ts


def longPoll(ts):
    payload = {'key': key, 'act': 'a_check',
               'ts': ts, 'wait': '10'}
    res = requests.get(server, params=payload, timeout=20).json()
    if 'ts' in res.keys():
        ts = res['ts']
    else:
        ts = getLongPollServer()
    if 'updates' in res.keys():
        updates = res['updates']
        for update in updates:
            Process(target=handleUpdate, args=[update]).start()
        return ts


def al_check():
    while True:
        notifs = update_notifications()
        if notifs:
            for notif in notifs:
                vkMsg(vkPersUserID, notif)
        print('Notifications Checked!')
        sleep(150)


def main():
    global token
    while True:
        try:
            token = getLongPollServer()
            while True:
                token = longPoll(token)
        except Exception as e:
            token = ''
            print('Ошибка: ' + str(e))


if __name__ == '__main__':
    Process(target=main).start()
    Process(target=al_check).start()
    Process(target=trello_socket).start()
