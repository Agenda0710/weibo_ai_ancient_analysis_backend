import csv
import os
from datetime import datetime
from Dashboard.config import WEIBO_COOKIE

import requests

headers = {
    'Cookie': WEIBO_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
}

url = 'https://weibo.com/ajax/statuses/show?'


def init():
    if not os.path.exists(r'D:\PythonProjects\weibo_django\Dashboard\spider_ancient\ancient_weibo_content.csv'):
        with open(r'D:\PythonProjects\weibo_django\Dashboard\spider_ancient\ancient_weibo_content.csv', 'w', newline='',
                  encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id',
                'likeNum',  # 点赞
                'commentNum',  # 评论量
                'reposts_count',  # 转发量
                'region',  # 地区
                'content',  # 内容
                'contentLength',  # 内容字数
                'create_at',  # 创作时间
                'detailUrl',  # 详情地址
                'authorName',
                'authorDetail',
            ])


def write_row(row):
    with open(r'D:\PythonProjects\weibo_django\Dashboard\spider_ancient\ancient_weibo_content.csv', 'a', newline='',
              encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def parse_json(response):
    id = response['id']
    likeNum = response['attitudes_count']
    commentNum = response['comments_count']
    reposts_count = response['reposts_count']
    try:
        region = response['region_name'].replace('发布于', '')
    except:
        region = ''
    content = response['text_raw']
    try:
        contentLength = response['textLength']
    except:
        contentLength = len(content)
    create_at = datetime.strptime(response['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
    try:
        detailUrl = 'https://weibo.com/' + str(response['id']) + '/' + response['mblogid']
    except:
        detailUrl = ''
    authorName = response['user']['screen_name']
    authorDetail = 'https://weibo.com/' + str(response['user']['id'])
    write_row(
        [
            id,
            likeNum,  # 点赞
            commentNum,  # 评论量
            reposts_count,  # 转发量
            region,  # 地区
            content,  # 内容
            contentLength,  # 内容字数
            create_at,
            detailUrl,  # 详情地址
            authorName,
            authorDetail,
        ]
    )


def start(ids=None):
    init()
    if ids is None:
        ids = ['P5CVkebkG', 'P5C2ZrycT']
    for index in range(len(ids)):
        params = {
            'id': ids[index],
            'locale': 'zh-CN',
            'isGetLongText': 'true',
        }
        response = requests.get(url=url, headers=headers, params=params)
        parse_json(response.json())


if __name__ == '__main__':
    start()
