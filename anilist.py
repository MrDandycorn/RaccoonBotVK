from credentials import anilist_token
import requests


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
                yield f'Вышла {notif["episode"]} серия {notif["media"]["title"]["userPreferred"]}'
            elif notif['type'] == 'RELATED_MEDIA_ADDITION':
                s = 'На сайт добавлено новое аниме: {}\n{}' if notif['media']['type'] == 'ANIME' else 'На сайт добавлена новая манга/новелла: {}\n{}'
                yield s.format(notif['media']['title']['userPreferred'], notif['media']['siteUrl'].replace('\/', '/'))
    else:
        return None
