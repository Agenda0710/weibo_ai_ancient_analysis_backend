import time
from datetime import datetime
from Dashboard.config import WEIBO_COOKIE
import requests
import os
import csv


def init():
    if not os.path.exists(r'Dashboard/spiders/contentData.csv'):
        with open(r'Dashboard/spiders/contentData.csv', 'w', newline='', encoding='utf-8') as f:
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
                'type',  # 类型
                'detailUrl',  # 详情地址
                'authorAvatar',  # 头像
                'authorName',
                'authorDetail',
                'isVip',
            ])


def writeRow(row):
    with open(r'Dashboard/spiders/contentData.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def getContentData(url, params):
    headers = {
        'Cookie': WEIBO_COOKIE,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['statuses']
    else:
        return None


def getTypeList():
    typeList = []
    with open(r'D:\PythonProjects\weibo_django\Dashboard\spiders\navData.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            typeList.append(row)
    return typeList


def parse_json(response, type):
    for artcile in response:
        id = artcile['id']
        likeNum = artcile['attitudes_count']
        commentNum = artcile['comments_count']
        reposts_count = artcile['reposts_count']
        try:
            region = artcile['region_name'].replace('发布于', '')
        except:
            region = ''
        content = artcile['text_raw']
        try:
            contentLength = artcile['textLength']
        except:
            contentLength = len(content)
        create_at = datetime.strptime(artcile['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
        type = type
        try:
            detailUrl = 'https://weibo.com/' + str(artcile['id']) + '/' + artcile['mblogid']
        except:
            detailUrl = ''
        authorAvatar = artcile['user']['avatar_large']
        authorName = artcile['user']['screen_name']
        authorDetail = 'https://weibo.com/' + str(artcile['user']['id'])
        isVip = artcile['user']['v_plus']
        writeRow(
            [
                id,
                likeNum,  # 点赞
                commentNum,  # 评论量
                reposts_count,  # 转发量
                region,  # 地区
                content,  # 内容
                contentLength,  # 内容字数
                create_at,
                type,
                detailUrl,  # 详情地址
                authorAvatar,  # 头像
                authorName,
                authorDetail,
                isVip,
            ]
        )


def start(typeNum=3, pageNum=2):
    articleUrl = 'https://weibo.com/ajax/feed/hottimeline'
    init()
    typeList = getTypeList()
    typeNumCount = 1
    for type in typeList:
        if typeNumCount > typeNum:
            return
        time.sleep(2)
        for page in range(0, pageNum):
            print('正在爬取的类型:{}中的第{}页'.format(type[0], page + 1))
            time.sleep(1)
            params = {
                'group_id': type[1],
                'containerid': type[2],
                'max_id': page,
                'counot': 10,
                'extparam': 'discover|new_feed'
            }
            response = getContentData(articleUrl, params)
            parse_json(response, type[0])
            typeNumCount += 1


if __name__ == '__main__':
    start()
