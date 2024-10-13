import jieba
import re
import csv


def main():
    # 读取分词文件
    reader = open('./cutComments.txt', 'r', encoding='utf8')
    text = reader.read()
    reader.close()

    # 打开结果文件用于保存
    result = open('./cipingTotal.csv', 'w', encoding='utf8', newline='')

    # 分词
    word_list = jieba.cut(text, cut_all=True)

    new_words = []
    # 正则表达式匹配中文字符
    for word in word_list:
        # 匹配中文字符，排除数字和英文字符
        if re.match(r'^[\u4e00-\u9fa5]+$', word) and len(word) > 1:
            new_words.append(word)

    word_count = {}

    for i in set(new_words):
        word_count[i] = new_words.count(i)

    # 格式整理
    list_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    writer = csv.writer(result)
    writer.writerow([
        'word',
        'frequency'
    ])

    for i in range(100):
        word, frequency = list_count[i]
        writer.writerow([word, frequency])


if __name__ == '__main__':
    main()
