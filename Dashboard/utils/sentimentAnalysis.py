import jieba
from snownlp import SnowNLP
from collections import Counter
import re
import os
from transformers import BertForSequenceClassification, BertTokenizer
import torch

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 定义资源文件路径
stopwords_path = os.path.join(script_dir, '..', 'separate_sentences', 'cn_stopwords.txt')
bert_model_dir = os.path.join(script_dir, '..', 'bert-base-chinese')
model_weights_path = os.path.join(script_dir, '..', 'weibo_articles_content_analysis.pt')


# 加载停用词表
def load_stopwords():
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())
    return stopwords


# 获取前十个热词及其频率
def get_top_keywords(content_list, stopwords):
    all_words = []
    for content in content_list:
        words = jieba.cut(content)
        filtered_words = [word for word in words if
                          word not in stopwords and len(word) > 1 and re.match(r'^[\u4e00-\u9fa5]+$', word)]
        all_words.extend(filtered_words)

    word_counts = Counter(all_words)
    return word_counts.most_common(10)


# 情感分析
def analyze_sentiment(content_list):
    sentiment_data = {'positive': 0, 'neutral': 0, 'negative': 0}
    for content in content_list:
        s = SnowNLP(content)
        sentiment = s.sentiments
        if sentiment > 0.5:
            sentiment_data['positive'] += 1
        elif sentiment == 0.5:
            sentiment_data['neutral'] += 1
        else:
            sentiment_data['negative'] += 1
    return sentiment_data


# 加载BERT模型
tokenizer = BertTokenizer.from_pretrained(bert_model_dir)
model = BertForSequenceClassification.from_pretrained(bert_model_dir, num_labels=3)
if torch.cuda.is_available():
    model.cuda()
model.load_state_dict(torch.load(model_weights_path))
model.eval()


def analyze_article_sentiment(texts, batch_size=16):
    sentiment_labels = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        inputs = tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt', max_length=128)
        if torch.cuda.is_available():
            inputs = {key: value.cuda() for key, value in inputs.items()}

        with torch.no_grad(), torch.cuda.amp.autocast():
            outputs = model(**inputs)

        predictions = torch.argmax(outputs.logits, dim=1)
        for pred in predictions:
            if pred.item() == 2:
                sentiment_labels.append("正面")
            elif pred.item() == 0:
                sentiment_labels.append("中性")
            elif pred.item() == 1:
                sentiment_labels.append("负面")
        torch.cuda.empty_cache()
    return sentiment_labels


if __name__ == '__main__':
    load_stopwords()
