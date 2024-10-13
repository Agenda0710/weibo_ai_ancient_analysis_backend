from snownlp import SnowNLP
import csv
from Dashboard.utils.getPublicData import getAllCommentData


def targetFile():
    targetFile = 'target.csv'
    commentList = getAllCommentData()

    rateData = []
    good = 0
    bad = 0
    middle = 0

    for index, i in enumerate(commentList):
        value = SnowNLP(i[4]).sentiments
        if value > 0.5:
            good += 1
            rateData.append([i[4], '正面'])
        elif value == 0.5:
            middle += 1
            rateData.append([i[4], '中性']),
        elif value < 0.5:
            bad += 1
            rateData.append([i[4], '负面'])

    with open(targetFile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'comment',
            'judge'
        ])
        for i in rateData:
            writer.writerow(i)

        print(rateData)


def main():
    targetFile()


if __name__ == '__main__':
    main()
