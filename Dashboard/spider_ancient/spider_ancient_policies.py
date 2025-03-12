import csv
import requests
from transformers import BertTokenizer, BertForSequenceClassification
import torch

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'athenaappname': '%E5%9B%BD%E7%BD%91%E6%90%9C%E7%B4%A2',
    'athenaappkey': 'gnFvwq4i4EdIs6HsXe%2FNUNgmsf%2Fqf8AfCR5FsTfrxPzKnTnNJfaNqgxscibjY8aOG5mTCwXelZ9QWhFofNklU5Gbj0jAtIIsvKZDJy2YPXr8FfGQ%2BC%2B%2FaL6J%2F7ehImM1ZW97aVVqJO8XnoD0e4NUzeL1cQogXInl46PbGB7AJrs%3D'
}

url = 'https://sousuoht.www.gov.cn/athena/forward/2A40CF891850CF7ED2F0FA6369ECBB88?t=zhengce&timetype=timeqb&mintime=&maxtime=&sort=score&searchfield=&pcodeJiguan=&childtype=&subchildtype=&tsbq=&pubtimeyear=&puborg=&pcodeYear=&pcodeNum=&filetype=&n=5&inpro='

policies_information = []
# 类别映射
category_map = {
    0: '经济',
    1: '国土规划与管理',
    2: '教育',
    3: '民生',
    4: '生态环境',
    5: '政治与行政',
    6: '卫生健康',
    7: '文化与社会',
    8: '科技与创新',
    9: '国防与安全',
    10: '市场监管与法治'
}

# 加载预训练的中文 BERT 分词器和模型
tokenizer = BertTokenizer.from_pretrained(r"D:\PythonProjects\weibo_django\Dashboard\bert-policy-category")
model = BertForSequenceClassification.from_pretrained(r"D:\PythonProjects\weibo_django\Dashboard\bert-policy-category")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def get_ancient_policies_information():
    for j in range(1, 5):
        params = {
            'sortType': 1,
            'p': j,
            'q': '非物质文化遗产',
        }

        response = requests.get(url, headers=headers, params=params)
        response.encoding = 'utf-8'
        data_list = response.json()['result']['data']['searchVO']['catMap']['zhongyangfile']['listVO']

        for i in range(len(data_list)):
            time = data_list[i]['pubtimeStr']
            title = data_list[i]['title']
            # 调用bert-policy-category进行预测
            category = predict_category(title)
            policies_information.append({'time': time, 'title': title, 'category': category})

    return policies_information


def predict_category(text):
    # 对文本进行分词和编码
    inputs = tokenizer(text, padding='max_length', truncation=True, max_length=256, return_tensors='pt').to(device)

    # 进行预测
    with torch.no_grad():
        outputs = model(**inputs)

    # 获取预测结果
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits, dim=1).item()

    # 返回类别名称
    return category_map.get(predicted_class_id, '未知')


if __name__ == '__main__':
    get_ancient_policies_information()
