import time
from datetime import datetime
import requests
import os
import csv


def init():
    if not os.path.exists('./commentData.csv'):
        with open('./commentData.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'articleId',
                'created_at',
                'like_counts',
                'region',
                'content',
                'authorName',
                'authorGender',
                'authorAddress',
                'authorAvatar'
            ])


def writeRow(row):
    with open('./commentData.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def getCommentData(url, params, retries=5, timeout=10):
    headers = {
        'Cookie': 'SINAGLOBAL=1984169755402.2407.1630424811319; SCF=AnamYq1gZv9LGPDy7XY42aNFXwRyLUhVSKbNMdmglCAKxYm16jLRNZI7OcctnpFCCXqbiCdLISYkdImnKYxvk6I.; ULV=1730175311306:5:5:1:4321409565696.8564.1730175311246:1729781733548; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbe9i6eO82u54wwcJr8D8MOnsaLoGqsVXy6vwKsj2mIZzTKemW_V4HvEdt04g_WBDoqxZ-V4m7FgjYKqOKtag01MrhBvS3tqRtbB8xNwFOmkxA==; PC_TOKEN=2b0b6853dc; ALF=1732869297; SUB=_2A25KJZ_hDeRhGeNG7VsV8SbFwz2IHXVpWp0prDV8PUJbkNANLRbAkW1NSzm19JDIpR8uObJ80qV3uRnjJawVYfHt; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; XSRF-TOKEN=WJlFLUvyRLqDe6Vtq2QCmE1v',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            time.sleep(1)  # 延迟1秒防止请求过快
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    return json_data['data']  # 确保返回的内容包含 'data'
                except ValueError as e:  # 捕获 JSON 解码错误
                    print(f"JSON 解码错误: {e}, 返回的内容: {response.text[:200]}...")  # 打印部分返回内容帮助调试
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}, 返回的内容: {response.text[:200]}...")
                return None
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误: {e}, 正在进行重试 ({attempt + 1}/{retries})...")
            time.sleep(2 ** attempt)  # 指数级回退等待时间
        except requests.exceptions.Timeout as e:
            print(f"请求超时: {e}, 正在进行重试 ({attempt + 1}/{retries})...")
        except Exception as e:
            print(f"发生未知错误: {e}, 返回的内容: {response.text[:200]}...")  # 捕获其他未知错误并输出部分内容
            return None
    return None


def getArticleList():
    articleList = []
    with open('./contentData.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            articleList.append(row)
    return articleList


def parse_json(response, articleId):
    if response:
        for comment in response:
            create_at = datetime.strptime(comment['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
            like_counts = comment['like_counts']
            try:
                region = comment['source'].replace('来自', '')
            except:
                region = ''
            content = comment['text_raw']
            authorName = comment['user']['screen_name']
            authorGender = comment['user']['gender']
            authorAddress = comment['user']['location']
            authorAvatar = comment['user']['avatar_large']
            writeRow([
                articleId,
                create_at,
                like_counts,
                region,
                content,
                authorName,
                authorGender,
                authorAddress,
                authorAvatar
            ])


def start(typeNum=3, pageNum=2):
    contentUrl = 'https://weibo.com/ajax/statuses/buildComments'
    init()
    articleList = getArticleList()
    for article in articleList:
        print(f'正在爬取id值为{article[0]}的文章')
        time.sleep(2)
        articleId = article[0]
        params = {
            'id': int(articleId),
            'is_show_bulletin': 2,
        }
        response = getCommentData(contentUrl, params)
        if response:
            parse_json(response, articleId)


if __name__ == '__main__':
    start()
