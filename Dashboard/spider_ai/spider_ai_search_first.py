import requests
from bs4 import BeautifulSoup
import re
from spider_ai_content_second import start

headers = {
    'Cookie': 'ALF=1736942111; SUB=_2A25KZGVPDeRhGeNG7VsV8SbFwz2IHXVpGPiHrDV8PUJbkNANLWrikW1NSzm19IqjANItdpQRJfS6vAZC0X4hCESk; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; PC_TOKEN=4d696b9fec; XSRF-TOKEN=smgh75Ey8z230dyxYS1RNQbL; _s_tentry=weibo.com; Apache=2278260953253.426.1734436246562; SINAGLOBAL=2278260953253.426.1734436246562; ULV=1734436246613:7:1:1:2278260953253.426.1734436246562:1731851135570; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbciA8deGx9L62h1QiAALi5vUAYuuViVmfOLbSFQFqvrv1nlBrNOKqXm7kBWeYGtmqcQKajDB9vpuSpOhL4x2LZ1KLPvIFnvGV0pOR0TFW94Qg==',
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
