from Dashboard.utils.get_ai_weibo_articles_and_comments_data import get_all_ai_comments_data
import jieba

targetText = './cutComments.txt'


def stopWordsList():
    stopWords = [line.strip() for line in open('./cn_stopwords.txt', 'r', encoding='utf-8').readlines()]
    return stopWords


def seg_depart(sentence):
    sentence_depart = jieba.cut(" ".join([x[4] for x in sentence]).strip())
    stopWords = stopWordsList()
    outStr = ''
    for word in sentence_depart:
        if word not in stopWords:
            if word != '\t':
                outStr += word
    return outStr


def write_comment_cuts():
    with open(targetText, 'w', encoding='utf-8') as targetFile:
        seg = jieba.cut(seg_depart(get_all_ai_comments_data()), cut_all=True)
        output = ' '.join(seg)
        targetFile.write(output)
        targetFile.write('\n')
        print('写入成功')


if __name__ == '__main__':
    write_comment_cuts()
