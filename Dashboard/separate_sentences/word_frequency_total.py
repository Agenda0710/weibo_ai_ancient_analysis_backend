import jieba
import re
import csv
from collections import Counter
import os


def load_stop_words(stopwords_path='./cn_stopwords.txt', extra_stopwords=None, remove_words=None):
    """加载停用词列表并支持扩展和移除"""
    if not os.path.exists(stopwords_path):
        raise FileNotFoundError(f"停用词文件未找到: {stopwords_path}")

    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stop_words = set(line.strip() for line in f if line.strip())

    # 添加额外停用词
    if extra_stopwords:
        stop_words.update(extra_stopwords)

    # 移除指定词汇
    if remove_words:
        stop_words.difference_update(remove_words)

    return stop_words


def process_text(input_file, stop_words):
    """处理分词文本并统计词频"""
    with open(input_file, 'r', encoding='utf-8') as reader:
        text = reader.read()

    # 分词（使用精准模式）
    word_list = jieba.cut(text, cut_all=False)

    # 正则匹配中文，并去除停用词
    filtered_words = [
        word for word in word_list
        if re.match(r'^[\u4e00-\u9fa5]+$', word) and len(word) > 1 and word not in stop_words
    ]

    # 使用 Counter 统计词频
    return Counter(filtered_words)


def save_word_frequency(word_counter, output_file, top_n=100):
    """保存词频结果到 CSV 文件"""
    with open(output_file, 'w', encoding='utf-8', newline='') as result_file:
        writer = csv.writer(result_file)
        writer.writerow(['word', 'frequency'])

        # 写入前 top_n 个高频词
        for word, frequency in word_counter.most_common(top_n):
            writer.writerow([word, frequency])


def main():
    # 加载停用词（支持扩展和移除）
    extra_stopwords = []
    remove_words = ['知道']
    stop_words = load_stop_words('./cn_stopwords.txt', extra_stopwords=extra_stopwords, remove_words=remove_words)

    # 处理文本并统计词频
    word_counter = process_text('./cut_ancient_comments.txt', stop_words)

    # 保存词频结果
    save_word_frequency(word_counter, './word_frequency_ancient.csv')

