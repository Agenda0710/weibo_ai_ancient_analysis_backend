from Dashboard.utils.query import query


def getAllCommentData():
    commenList = query('select * from weibo.comments', [])
    return commenList


def getAllArticleData():
    articleList = query('select * from weibo.article', [])
    return articleList
