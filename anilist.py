from credentials import anilist_token, vkPersUserID
import requests
from utils import vkMsg
from time import sleep, time, mktime
import feedparser as fp

q = []


def graphql_request(query):
    url = 'https://graphql.anilist.co'
    headers = {
        'Authorization': 'Bearer '+anilist_token
    }
    data = {
        'query': query
    }
    res = requests.post(url, headers=headers, data=data).json()
    return res


def get_notifications(count):
    query = '{Page(perPage:'+str(count)+'){notifications(type_in:[AIRING,RELATED_MEDIA_ADDITION],resetNotificationCount:true){...on AiringNotification{type,episode,media{id,type,title{userPreferred},siteUrl}createdAt}...on RelatedMediaAdditionNotification {type,media{id,type,title{userPreferred},siteUrl}createdAt}}}}'
    return graphql_request(query)['data']['Page']['notifications']


def update_notifications():
    query = '{Viewer{unreadNotificationCount}}'
    ncnt = graphql_request(query)['data']['Viewer']['unreadNotificationCount']
    if ncnt != 0:
        notifs = get_notifications(ncnt)
        for notif in notifs:
            if notif['type'] == 'AIRING':
                q.append(notif['media']['title']['userPreferred'])
                yield f'Вышла {notif["episode"]} серия {notif["media"]["title"]["userPreferred"]}'
            elif notif['type'] == 'RELATED_MEDIA_ADDITION':
                s = 'На сайт добавлено новое аниме: {}\n{}' if notif['media']['type'] == 'ANIME' else 'На сайт добавлена новая манга/новелла: {}\n{}'
                yield s.format(notif['media']['title']['userPreferred'], notif['media']['siteUrl'].replace('\/', '/'))
    else:
        return None


def update_rss():
    while True:
        try:
            hsubs = fp.parse('http://www.horriblesubs.info/rss.php?res=1080')['entries']
            for sub in hsubs:
                dt = sub['published_parsed']
                if time() - mktime(dt) < 12000:
                    for _ in range(len(q)):
                        title = q.pop(0)
                        if ' '.join(title.split(' ')[0]) in sub['title']:
                            vkMsg(vkPersUserID, f'Новая серия {title} вышла в субтитрах от HorribleSubs!')
                        else:
                            q.append(title)
            sleep(60)
        except Exception as e:
            print(f'Ошибка: {e}')


def al_check():
    while True:
        notifs = update_notifications()
        if notifs:
            for notif in notifs:
                vkMsg(vkPersUserID, notif)
        update_rss()
        sleep(150)
