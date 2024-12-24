import requests
import csv
import numpy as np
import os
from Dashboard.config import WEIBO_COOKIE

def init():
    if not os.path.exists('./navData.csv'):
        with open('./navData.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'navName',
                'gid',
                'containerid',
            ])


def writeRow(row):
    with open('./navData.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def getNavData(url):
    headers = {
        'Cookie': WEIBO_COOKIE,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }
    params = {
        'is_new_segment': 1,
        'fetch_hot': 1
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def parse_json(response):
    navList = np.append(response['groups'][3]['group'], response['groups'][4]['group'])
    print(navList)
    for nav in navList:
        navName = nav['title']
        gid = nav['gid']
        containerid = nav['containerid']
        writeRow([
            navName, gid, containerid
        ])


if __name__ == '__main__':
    init()
    url = 'https://weibo.com/ajax/feed/allGroups'
    response = getNavData(url)
    parse_json(response)
