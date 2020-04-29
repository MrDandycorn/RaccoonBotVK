import asyncio
import re
from datetime import datetime
from time import time, mktime

import aiohttp
import feedparser as fp
from credentials import anilist_token, voron_anilist_token
from vk_botting import commands

tokens = {
    223823744: anilist_token,
    459278596: voron_anilist_token
}

q = dict([(user, []) for user in tokens])


async def graphql_request(query, uid):
    url = 'https://graphql.anilist.co'
    headers = {
        'Authorization': 'Bearer ' + tokens[uid]
    }
    data = {
        'query': query
    }
    async with aiohttp.ClientSession() as session:
        res = await session.post(url, headers=headers, data=data)
        return await res.json()


async def get_notifications(count, uid):
    query = 'query{Page(perPage: '+str(count)+') {notifications(type_in: [AIRING, ACTIVITY_MESSAGE, ACTIVITY_REPLY, FOLLOWING, ACTIVITY_MENTION, THREAD_COMMENT_MENTION, THREAD_SUBSCRIBED, THREAD_COMMENT_REPLY, ACTIVITY_LIKE, ACTIVITY_REPLY_LIKE, THREAD_LIKE, THREAD_COMMENT_LIKE, ACTIVITY_REPLY_SUBSCRIBED, RELATED_MEDIA_ADDITION], resetNotificationCount: true) {... on AiringNotification {type,episode,media {id,type,title {userPreferred}}}... on RelatedMediaAdditionNotification {type,media {id,type,title {userPreferred},siteUrl}}... on FollowingNotification {type}... on ActivityMessageNotification {type}... on ActivityMentionNotification {type}... on ActivityReplyNotification {type}... on ActivityReplySubscribedNotification {type}... on ActivityLikeNotification {type}... on ActivityReplyLikeNotification {type}... on ThreadCommentMentionNotification {type}... on ThreadCommentReplyNotification {type}... on ThreadCommentSubscribedNotification {type}... on ThreadCommentLikeNotification {type}... on ThreadLikeNotification {type}}}}'
    res = await graphql_request(query, uid)
    return res['data']['Page']['notifications']


async def update_notifications(uid):
    query = '{Viewer{unreadNotificationCount}}'
    ncnt = await graphql_request(query, uid)
    ncnt = ncnt['data']['Viewer']['unreadNotificationCount']
    if ncnt != 0:
        notifs = await get_notifications(ncnt, uid)
        for notif in notifs:
            if notif['type'] == 'AIRING':
                q[uid].append(notif['media']['title']['userPreferred'])
                yield f'Вышла {notif["episode"]} серия {notif["media"]["title"]["userPreferred"]}'
            elif notif['type'] == 'RELATED_MEDIA_ADDITION':
                s = 'На сайт добавлено новое аниме: {}\n{}' if notif['media']['type'] == 'ANIME' else 'На сайт добавлена новая манга/новелла: {}\n{}'
                yield s.format(notif['media']['title']['userPreferred'], notif['media']['siteUrl'].replace(r'\/', '/'))


async def search_anilist(title, uid):
    query = 'query{anime:Page(perPage: 20){results: media(type: ANIME, isAdult: false, search: "'+title+'"){title {userPreferred},nextAiringEpisode{episode},status, endDate{year,month,day}}}}'
    res = await graphql_request(query, uid)
    res = res['data']['anime']['results']
    if res:
        for anime in res:
            if anime['status'] == 'RELEASING':
                if anime['nextAiringEpisode']:
                    return anime['title']['userPreferred'], anime['nextAiringEpisode']['episode']
                return anime['title']['userPreferred'], 0
            else:
                if anime['endDate'] and anime['endDate']['day']:
                    date = anime['endDate']
                    dt = datetime(year=date['year'], month=date['month'], day=date['day'])
                    diff = datetime.today()-dt
                    if diff.days < 10:
                        if anime['nextAiringEpisode']:
                            return anime['title']['userPreferred'], anime['nextAiringEpisode']['episode']
                        return anime['title']['userPreferred'], 0
    return None


def scrape(title):
    group = 'HorribleSubs' if '[HorribleSubs]' in title else 'Erai-raws'
    res = re.sub(r'\[([^)]+?)]', '', title.replace('.mkv', ''))
    ep = re.search(r' [–|-] [0-9]+', res).group()
    res = res.replace(ep, '').strip()
    ep = re.search(r'[0-9]+', ep).group()
    return res, int(ep), group


class Anilist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.al_check())
        bot.loop.create_task(self.update_rss())

    @commands.command(aliases=['airing', 'air'])
    async def mine(self, ctx):
        if ctx.from_id not in tokens:
            return
        query = 'query{anime:Page(perPage:200){results:media(type:ANIME,status:RELEASING,onList:true){id,title{userPreferred},nextAiringEpisode{airingAt,timeUntilAiring,episode}}}}'
        res = await graphql_request(query, ctx.from_id)
        airing = res['data']['anime']['results']
        airing = sorted([anime for anime in airing if anime['nextAiringEpisode'] and 'airingAt' in anime['nextAiringEpisode']], key=lambda x: x['nextAiringEpisode']['airingAt'])
        msg = ''
        for air in airing:
            dt = datetime.fromtimestamp(air['nextAiringEpisode']['airingAt'])
            dtf = dt.strftime('%H:%M')
            if dt.date() == datetime.today().date():
                dtr = datetime.utcfromtimestamp(air['nextAiringEpisode']['timeUntilAiring']).time()
                dtrf = dtr.strftime('%H:%M:%S')
                msg += f'{air["title"]["userPreferred"]} | {dtf} | in {dtrf}\n'
        if not msg:
            msg = 'Не осталось аниме на сегодня :c'
        return await ctx.reply(msg)

    async def update_rss(self):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    hsubs = await session.get('http://www.horriblesubs.info/rss.php?res=1080')
                    esubs = await session.get('https://ru.erai-raws.info/rss-1080/')
                    hsubs = await hsubs.text()
                    esubs = await esubs.text()
                hsubs = fp.parse(hsubs)['entries']
                esubs = fp.parse(esubs)['entries']
                for uid in tokens:
                    try:
                        for sub in hsubs+esubs:
                            dt = sub['published_parsed']
                            if time() - mktime(dt) < 30000:
                                scraped = scrape(sub['title'])
                                info = await search_anilist(scraped[0], uid)
                                for _ in range(len(q[uid])):
                                    title = q[uid].pop(0)
                                    if info[0] == title:
                                        await self.bot.send_message(uid, f'{scraped[1]} серия {title} вышла в субтитрах от {scraped[2]}!')
                                    else:
                                        q[uid].append(title)
                    except Exception as e:
                        print(f'Exception in update_rss for {uid}: {e}')
            except Exception as e:
                print(f'Exception in update_rss: {e}')
            finally:
                await asyncio.sleep(60)

    async def al_check(self):
        while True:
            try:
                for uid in tokens:
                    notifs = update_notifications(uid)
                    if notifs:
                        async for notif in notifs:
                            await self.bot.send_message(uid, notif)
            except Exception as e:
                print(f'Exception in al_check: {e}')
            finally:
                await asyncio.sleep(60)


def anilist_setup(bot):
    bot.add_cog(Anilist(bot))
