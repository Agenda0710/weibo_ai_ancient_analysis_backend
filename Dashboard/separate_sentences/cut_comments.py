import jieba

from Dashboard.separate_sentences.get_ancient_weibo_articles_and_comments_data import get_all_ancient_comments_data

# 分词结果保存路径
targetText = './cut_ancient_comments.txt'


def stop_words_list():
    """加载停用词列表"""
    return [line.strip() for line in open('./cn_stopwords.txt', 'r', encoding='utf-8').readlines()]


def seg_depart(sentence_list):
    """分词并去除停用词"""
    stop_words = stop_words_list()
    processed_sentences = []

    for sentence in sentence_list:
        # 分词
        words = jieba.cut(sentence.strip())
        # 去停用词
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        processed_sentences.append(" ".join(filtered_words))

    return "\n".join(processed_sentences)


def write_ancient_articles_cuts():
    """从评论中分词并写入目标文件"""
    comments = get_all_ancient_comments_data()  # 获取所有评论数据

    # 假设评论内容在第五列
    comments_content = [comment[5] for comment in comments if len(comment) > 5 and comment[5]]

    # 分词并过滤停用词
    segmented_text = seg_depart(comments_content)

    # 写入文件
    with open(targetText, 'w', encoding='utf-8') as targetFile:
        targetFile.write(segmented_text)
        print('写入成功')
