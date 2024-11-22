from snownlp import SnowNLP
import csv
from Dashboard.utils.getPublicData import getAllCommentData


def targetFile():
    targetFile = r'Dashboard/learning_model/target.csv'
    commentList = getAllCommentData()

    rateData = []
    good = 0
    bad = 0
    middle = 0

    for index, i in enumerate(commentList):
        # 先检查 i[5] 是否为 None 或者空字符串，避免错误
        if i[5] is not None and i[5].strip():  # strip() 用于排除空白字符
            value = SnowNLP(i[5]).sentiments
            if value > 0.5:
                good += 1
                rateData.append([i[5], '正面'])
            elif value == 0.5:
                middle += 1
                rateData.append([i[5], '中性'])
            elif value < 0.5:
                bad += 1
                rateData.append([i[5], '负面'])
        else:
            print(f"第 {index + 1} 行评论为空，跳过该条记录。")

    with open(targetFile, 'w', newline='', encoding='utf-8', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow([
            'comment',
            'judge'
        ])
        for i in rateData:
            writer.writerow(i)


def main():
    targetFile()


if __name__ == '__main__':
    main()
