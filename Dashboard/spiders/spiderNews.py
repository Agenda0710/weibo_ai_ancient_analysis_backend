import requests
import torch
from transformers import BertTokenizer
from torch import nn
from transformers import BertModel
from datetime import datetime
from Dashboard.config import WEIBO_COOKIE


# 定义标签字典
def get_label_string(label):
    labels = {
        '民生': 0, '文化': 1, '娱乐': 2, '体育': 3, '财经': 4, '家具': 5,
        '汽车': 6, '教育': 7, '科技': 8, '军事': 9, '旅游': 10, '时政': 11,
        '股票': 12, '农业': 13, '电竞': 14
    }
    for key, value in labels.items():
        if value == label:
            return key
    return None


# 定义BERT分类模型
class BertClassifier(nn.Module):
    def __init__(self, dropout=0.5):
        super(BertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(r'D:\PythonProjects\weibo_django\Dashboard\bert-base-chinese',
                                              num_labels=15)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 15)
        self.relu = nn.ReLU()

    def forward(self, input_id, mask):
        _, pooled_output = self.bert(input_ids=input_id, attention_mask=mask, return_dict=False)
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_layer = self.relu(linear_output)
        return final_layer


# 加载已训练的模型和分词器
model = BertClassifier()
model.load_state_dict(torch.load(r'D:\PythonProjects\weibo_django\Dashboard\BERT-toutiao.pt'))
model.eval()
tokenizer = BertTokenizer.from_pretrained(r'D:\PythonProjects\weibo_django\Dashboard\bert-base-chinese')
if torch.cuda.is_available():
    model.cuda()


def classify_news(news_data):
    # 对新闻数据进行分词和编码
    text_input = tokenizer(news_data, padding='max_length', max_length=512, truncation=True, return_tensors="pt")
    if torch.cuda.is_available():
        text_input = {key: value.cuda() for key, value in text_input.items()}
    mask = text_input['attention_mask']
    input_id = text_input['input_ids']

    # 预测新闻分类

    with torch.no_grad():
        output = model(input_id, mask)
        label_index = output.argmax(dim=1).item()

    # 获取标签名称
    label_string = get_label_string(label_index)

    torch.cuda.empty_cache()  # 清理未使用的显存
    return label_string


# 获取微博内容并分类
def getContentData():
    news_data_analysis = []
    for i in (1, 3):
        url = 'https://weibo.com/ajax/statuses/searchProfile?'
        headers = {
            'Cookie': WEIBO_COOKIE,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
        }
        params = {
            'uid': 2656274875,
            'page': i,
            'q': '古代文化',
        }
        response = requests.get(url, headers=headers, params=params)

        data_list = response.json().get('data', {}).get('list', [])

        for j in range(len(data_list)):
            # 获取新闻内容和时间
            news_data = data_list[j]['text_raw'].strip()
            news_create_time = data_list[j]['created_at']
            news_blog_id = data_list[j]['mblogid']

            news_detail_url = r'https://weibo.com/' + str(params.get('uid')) + '/' + str(news_blog_id)
            # 格式化时间为 YYYY-MM-DD
            formatted_time = datetime.strptime(news_create_time, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d")

            # 调用分类函数对新闻分类
            label = classify_news(news_data)

            # 添加到结果列表
            news_data_analysis.append({
                'news_data': news_data,
                'news_create_time': formatted_time,
                'news_detail_url': news_detail_url,
                'label': label
            })
    return news_data_analysis


if __name__ == '__main__':
    getContentData()
