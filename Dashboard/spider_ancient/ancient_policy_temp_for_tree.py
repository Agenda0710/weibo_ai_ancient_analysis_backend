import csv
import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'athenaappname': '%E5%9B%BD%E7%BD%91%E6%90%9C%E7%B4%A2',
    'athenaappkey': 'gnFvwq4i4EdIs6HsXe%2FNUNgmsf%2Fqf8AfCR5FsTfrxPzKnTnNJfaNqgxscibjY8aOG5mTCwXelZ9QWhFofNklU5Gbj0jAtIIsvKZDJy2YPXr8FfGQ%2BC%2B%2FaL6J%2F7ehImM1ZW97aVVqJO8XnoD0e4NUzeL1cQogXInl46PbGB7AJrs%3D'
}

url = 'https://sousuoht.www.gov.cn/athena/forward/2A40CF891850CF7ED2F0FA6369ECBB88?t=zhengce_zy_gw&timetype=timezd&mintime=&maxtime=2025-03-12&pcodeJiguan=&puborg=&pcodeYear=&pcodeNum=&filetype=&n=5&sort=score'

policies_information = []


def get_ai_policies_information():
    for j in range(1, 10):
        params = {
            "q": '文化',
            "searchfield": "title",
            "p": j,
        }

        response = requests.get(url, headers=headers, params=params)
        response.encoding = 'utf-8'
        try:
            data = response.json()
            # 打印返回的数据结构，方便调试
            data_list = data.get('result', {}).get('data', {}).get('searchVO', {}).get('catMap', {}).get('gongwen', {}).get('listVO', [])
            for item in data_list:
                time = item.get('pubtimeStr')
                title = item.get('title')
                if time and title:
                    policies_information.append({'time': time, 'title': title})
        except (KeyError, ValueError):
            print(f"请求第 {j} 页时出现错误，响应内容: {response.text}")

    return policies_information


def save_to_csv(data, filename='policies_information.csv'):
    """
    将数据保存为 CSV 文件
    :param data: 数据列表，每个元素是一个字典
    :param filename: 输出的 CSV 文件名
    """
    # 定义 CSV 文件的列名
    fieldnames = ['time', 'title']

    # 写入 CSV 文件
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 写入数据
        writer.writerows(data)


if __name__ == '__main__':
    # 获取政策信息
    result_list = get_ai_policies_information()

    # 打印结果
    print(result_list)

    # 将结果保存为 CSV 文件
    save_to_csv(result_list)
    print("数据已成功保存为 CSV 文件！")