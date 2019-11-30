import aiohttp
from json import load, dump
from bs4 import BeautifulSoup
from utils import vkMsg
from credentials import vkPersUserID
import asyncio


async def getChapters(url):
    async with aiohttp.ClientSession() as session:
        res = await session.get(url)
        res = await res.text()
    bs = BeautifulSoup(res, features='lxml')
    chaps = bs.find('ul', {'class': 'chapter_list'}).findAll('li')
    chaps = [(chap.a.text.strip(), chap.find('span', {'class': 'time'}).text) for chap in chaps]
    return chaps


async def initManga(manga):
    chaps = await getChapters(manga['url'])
    manga['latest'] = chaps[0][0]


async def checkManga(manga):
    chaps = await getChapters(manga['url'])
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
            await vkMsg(vkPersUserID, new)


async def update_manga():
    while True:
        try:
            mangas = load(open('resources/mangas.json', 'r'))
            for manga in mangas:
                if list(manga.keys()) == ['url']:
                    await initManga(manga)
                else:
                    await checkManga(manga)
            dump(mangas, open('resources/mangas.json', 'w+'))
        finally:
            await asyncio.sleep(60)
