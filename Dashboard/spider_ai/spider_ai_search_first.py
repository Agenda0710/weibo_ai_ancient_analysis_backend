import requests
from bs4 import BeautifulSoup
import re
from spider_ai_content_second import start
from Dashboard.config import WEIBO_COOKIE

headers = {
    'Cookie': WEIBO_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
}

url = 'https://s.weibo.com/weibo?'


def get_ai_article_ids():
    ids = []
    for i in range(1, 10):
        params = {
            'q': '大模型',
            'page': i
        }
        # 发起请求
        response = requests.get(url, headers=headers, params=params)

        # 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 找到所有 from 的 div 标签
        from_divs = soup.find_all('div', class_='from')
        # 提取链接和时间
        for div in from_divs:
            link_tag = div.find('a', href=True)
            if link_tag:
                link = link_tag['href']
                match = re.search(r'/([^/?]+)\?', link)
                ids.append(match.group(1))

    return ids
