from json import load, dump
from bs4 import BeautifulSoup
from vk_botting import Cog
from credentials import vkPersUserID
import asyncio


class mangatown(Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.update_manga())

    async def getChapters(self, url):
        res = await self.bot.general_request(url)
        bs = BeautifulSoup(res, features='lxml')
        chaps = bs.find('ul', {'class': 'chapter_list'}).findAll('li')
        chaps = [(chap.a.text.strip(), chap.find('span', {'class': 'time'}).text) for chap in chaps]
        return chaps

    async def initManga(self, manga):
        chaps = await self.getChapters(manga['url'])
        manga['latest'] = chaps[0][0]

    async def checkManga(self, manga):
        chaps = await self.getChapters(manga['url'])
        if chaps[0][0] != manga['latest']:
            news = []
            for chap in chaps:
                if chap[0] == manga['latest']:
                    break
                if chap[1] == 'Today':
                    news.append(f'Новая глава: {chap[0]}')
                else:
                    break
            manga['latest'] = chaps[0][0]
            for new in reversed(news):
                await self.bot.send_message(vkPersUserID, new)

    async def update_manga(self):
        while True:
            try:
                mangas = load(open('resources/mangas.json', 'r'))
                for manga in mangas:
                    if list(manga.keys()) == ['url']:
                        await self.initManga(manga)
                    else:
                        await self.checkManga(manga)
                dump(mangas, open('resources/mangas.json', 'w+'))
            except Exception as e:
                print(f'Exception in update_manga: {e}')
            finally:
                await asyncio.sleep(60)


def mangatown_setup(bot):
    bot.add_cog(mangatown(bot))
