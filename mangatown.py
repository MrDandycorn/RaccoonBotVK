import requests
from json import load, dump
from bs4 import BeautifulSoup
from utils import vkMsg
from credentials import vkPersUserID


def getChapters(url):
    res = requests.get(url).text
    bs = BeautifulSoup(res, features='lxml')
    chaps = bs.find('ul', {'class': 'chapter_list'}).findAll('li')
    chaps = [(chap.a.text.strip(), chap.find('span', {'class': 'time'}).text) for chap in chaps]
    return chaps


def initManga(manga):
    chaps = getChapters(manga['url'])
    manga['latest'] = chaps[0][0]


def checkManga(manga):
    chaps = getChapters(manga['url'])
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
            vkMsg(vkPersUserID, new)


def update_manga():
    mangas = load(open('resources/mangas.json', 'r'))
    for manga in mangas:
        if list(manga.keys()) == ['url']:
            initManga(manga)
        else:
            checkManga(manga)
    dump(mangas, open('resources/mangas.json', 'w+'))
