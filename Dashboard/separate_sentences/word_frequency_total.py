import jieba
import re
import csv
from collections import Counter


def load_stop_words():
    """加载停用词列表"""
    with open('./cn_stopwords.txt', 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)


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
    stop_words = load_stop_words()
    word_counter = process_text('./cut_ancient_comments.txt', stop_words)
    save_word_frequency(word_counter, './word_frequency_ancient.csv')


if __name__ == '__main__':
    main()
