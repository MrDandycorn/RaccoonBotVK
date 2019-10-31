from credentials import anilist_token, vkPersUserID
import requests
from utils import vkMsg
from time import time, mktime
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
    query = 'query{Page(perPage: '+str(count)+') {notifications(type_in: [AIRING, ACTIVITY_MESSAGE, ACTIVITY_REPLY, FOLLOWING, ACTIVITY_MENTION, THREAD_COMMENT_MENTION, THREAD_SUBSCRIBED, THREAD_COMMENT_REPLY, ACTIVITY_LIKE, ACTIVITY_REPLY_LIKE, THREAD_LIKE, THREAD_COMMENT_LIKE, ACTIVITY_REPLY_SUBSCRIBED, RELATED_MEDIA_ADDITION], resetNotificationCount: true) {... on AiringNotification {type,episode,media {id,type,title {userPreferred}}}... on RelatedMediaAdditionNotification {type,media {id,type,title {userPreferred},siteUrl}}... on FollowingNotification {type}... on ActivityMessageNotification {type}... on ActivityMentionNotification {type}... on ActivityReplyNotification {type}... on ActivityReplySubscribedNotification {type}... on ActivityLikeNotification {type}... on ActivityReplyLikeNotification {type}... on ThreadCommentMentionNotification {type}... on ThreadCommentReplyNotification {type}... on ThreadCommentSubscribedNotification {type}... on ThreadCommentLikeNotification {type}... on ThreadLikeNotification {type}}}}'
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


def update_rss():
    hsubs = fp.parse('http://www.horriblesubs.info/rss.php?res=1080')['entries']
    for sub in hsubs:
        dt = sub['published_parsed']
        if time() - mktime(dt) < 24000:
            for _ in range(len(q)):
                title = q.pop(0)
                if title.split(' ')[0] in sub['title']:
                    vkMsg(vkPersUserID, f'Новая серия {title} вышла в субтитрах от HorribleSubs!')
                else:
                    q.append(title)


def al_check():
    notifs = update_notifications()
    if notifs:
        for notif in notifs:
            vkMsg(vkPersUserID, notif)
