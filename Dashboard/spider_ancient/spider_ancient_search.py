import re
import requests
from Dashboard.config import WEIBO_COOKIE

headers = {
    'Cookie': WEIBO_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
}


def clean_html_tags(text):
    """
    清理HTML标签并去除多余空白
    :param text: 待清理的文本
    :return: 清理后的文本
    """
    text = re.sub(r'<.*?>', '', text)  # 去掉HTML标签
    return text.strip().replace('\n', '').replace('\xa0', '')


def get_weibo_search_hot_query(q):
    url = r'https://weibo.com/ajax/side/search?'
    params = {
        'q': q
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()['data']['hotquery']
    hot_query_list = []
    for i in range(len(data)):
        hot_query = data[i]['suggestion']
        hot_query_list.append(hot_query)
    return hot_query_list


def get_weibo_search_text(q):
    """
    根据关键词和页数范围，爬取微博搜索结果中的完整文本内容
    :param q: 搜索关键词
    :return: 包含提取并清理后的微博完整文本内容的列表
    """
    all_texts = []
    base_url = 'https://s.weibo.com/weibo?'

    for page in range(1, 11):
        params = {
            'q': q,
            'nodup': 1,
            'page': page,
        }

        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()  # 检查请求是否成功，若不成功则抛出异常

            # 获取网页内容
            html_content = response.text

            # 定义正则提取规则
            full_text_pattern = re.compile(
                r'<p class="txt" node-type="feed_list_content_full".*?>(.*?)<a href="javascript:void\(0\);"', re.S
            )

            # 提取完整文本
            full_text_matches = full_text_pattern.findall(html_content)
            full_texts = [clean_html_tags(text) for text in full_text_matches]
            all_texts.extend(full_texts)

        except requests.RequestException as e:
            print(f"请求第 {page} 页失败: {e}")

    return all_texts


if __name__ == '__main__':
    # 用户输入关键词和爬取页数
    keyword = input("请输入搜索关键词：").strip()

    # 调用爬取函数
    results = get_weibo_search_text(keyword)
    get_weibo_search_hot_query(keyword)

    # 打印结果
    print("\n提取的完整文本：")
    for i, text in enumerate(results, 1):
        print(f"{i}: {text}")
