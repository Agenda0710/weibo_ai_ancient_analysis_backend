import re
import requests
from Dashboard.config import WEIBO_COOKIE
import redis

headers = {
    'Cookie': WEIBO_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
}

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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
    使用Redis分布式锁确保同一时间只有一个请求能执行爬取
    """
    lock_key = f"weibo_crawler_lock:{q}"  # 基于关键词的锁
    lock_timeout = 60  # 锁的超时时间(秒)
    all_texts = []
    base_url = 'https://s.weibo.com/weibo?'

    # 尝试获取锁
    acquired = r.set(lock_key, "locked", nx=True, ex=lock_timeout)
    if not acquired:
        print("当前已有其他请求在处理相同关键词的爬取，请稍后再试")
        raise Exception("当前已有其他请求在处理相同关键词的爬取，请稍后再试")

    try:
        for page in range(1, 11):
            try:
                # 每次循环检查锁是否仍然持有
                if not r.exists(lock_key):
                    print("锁已过期，爬取中断")
                    raise Exception("锁已过期，爬取中断")

                # 刷新锁的过期时间
                r.expire(lock_key, lock_timeout)

                # 爬取逻辑不变
                params = {'q': q, 'nodup': 1, 'page': page}
                response = requests.get(base_url, headers=headers, params=params)
                response.raise_for_status()

                html_content = response.text
                full_text_pattern = re.compile(
                    r'<p class="txt" node-type="feed_list_content_full".*?>(.*?)<a href="javascript:void\(0\);"', re.S
                )
                full_text_matches = full_text_pattern.findall(html_content)
                full_texts = [clean_html_tags(text) for text in full_text_matches]
                all_texts.extend(full_texts)

            except requests.RequestException as e:
                print(f"请求第 {page} 页失败: {e}")

    finally:
        # 确保最终释放锁
        r.delete(lock_key)

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
