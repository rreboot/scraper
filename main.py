from itertools import chain
from multiprocessing import Pool
import os
from time import time
import urllib
import requests
from lxml import html

from db_actions import *


def get_pages():
    url = 'https://trinixy.ru/gif'
    r = requests.get(url)

    tree = html.fromstring(r.text)

    nav = tree.xpath('//div[@class="navigation-inner"]')[0]
    last = int(nav.getchildren()[-2].values()[0].split('/')[-2])

    return ['{}/page/{}/'.format(url, x) for x in range(1, last + 1)]


def get_articles(page_url):
    articles = []
    r = requests.get(page_url)
    tree = html.fromstring(r.text)
    posts = tree.xpath('//article[@class="typical"]')
    for post in posts:
        title_url = post.xpath('.//h2/a/@href')[0]
        post_id = title_url.split('/')[-1].split('-')[0]
        rating = int(post.xpath('.//span[contains(@class, "ignore-select")]')[-1].text)
        tags = post.xpath('.//div[@class="arttagss"]/a')
        if len(tags) != 0:
            tags = [x.text for x in tags]

        articles.append({'id': post_id,
                         'url': title_url,
                         'rating': rating,
                         'tags': tags})
    return articles


def make_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def get_gifs_info(article):
    r = requests.get(article['url'])
    tree = html.fromstring(r.text)
    newsarea = tree.xpath('//*[@id="newsarea"]')[0]
    gif_dict = {'article': int(article['id']),
                'urls': newsarea.xpath('.//img/@src')}
    return gif_dict


def download_gifs(article):
    if (article['rating'] >= 18) and (len(article['tags']) == 0):
        make_dir(article['id'])
        r = requests.get(article['url'])
        tree = html.fromstring(r.text)
        newsarea = tree.xpath('//*[@id="newsarea"]')[0]
        gifs_urls = newsarea.xpath('.//img/@src')
        for url in gifs_urls:
            name = url.split('/')[-1]
            s_path = os.path.join(article['id'], name)
            if not os.path.exists(s_path):
                urllib.request.urlretrieve(url, s_path)
            print('{} saved'.format(name))


if __name__ == '__main__':

    pages_urls = get_pages()

    print('Getting page urls...')
    with Pool(20) as p:
        articles = p.map(get_articles, pages_urls)

    articles = list(chain.from_iterable(articles))

    print('Getting gif urls...')
    time_start = time()
    with Pool(20) as p:
        gif_urls = p.map(get_gifs_info, articles)
    print('Done. Time: {:.2f}'.format(time() - time_start))

    print('Get from db and put new articles')
    conn = open_db()
    db_id_list = conn.execute("SELECT id FROM articles").fetchall()
    db_id_list = set(chain.from_iterable(db_id_list))

    ids = {int(x['id']) for x in articles}

    new_ids = ids - db_id_list
    print(new_ids)

    if new_ids:
        prepared_list = []
        for article in articles:
            if int(article['id']) in new_ids:
                prepared_list.append((int(article['id']),
                                      article['url'],
                                      article['rating']))
                '''
                if len(article['tags']) != 0:
                    insert to tags
                    insert to articles_tags
                insert to files (name, article_id)
                '''
        conn.executemany("INSERT INTO articles VALUES (?, ?, ?)", prepared_list)
        conn.commit()
    print('Done.')

    '''INSERT INTO tags ('''

"""
    + получить список страниц
    + получить список постов (id, url, rating, tags) с сайта
    + получить список постов из базы
    + для недостающих постов внести данные по файлам и тегам
    + внести в базу недостающие посты

    - получить список папок из database

    - скачать те, у которых в базе downoloaded == 0
    - обновить базу: 
        - поставить downloaded == 1 для тех, которые были скачаны
        !- указать пути к файлам

"""


    # time_end = time()
    # print('{} articles parsed. Time: {}'.format(
    #     len(articles), time_end - time_start))

    # time_start = time_end

    # with Pool(5) as p:
    #     p.map(download_gifs, articles)
    # print(time() - time_start)



    # for article in articles:
    #     if (article['rating'] >= 18) and (len(article['tags']) == 0):
    #         make_dir(article['id'])
    #         with Pool(20) as p:
    #             p.map(download_gifs, article)
    #         time_end = time()
    #         print('{} parsed. Time: {} s'.format(
    #             article['id'], time_end - time_start))
    
    # with open('test.txt', 'w') as f:
    #     json.dump(articles, f)