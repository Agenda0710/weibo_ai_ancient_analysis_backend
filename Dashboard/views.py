from django.core.paginator import Paginator
from django.db.models.functions import Cast
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import requests
from django.db.models import Count, Max
from collections import Counter, defaultdict
import jieba
from snownlp import SnowNLP
from Dashboard.utils.sentimentAnalysis import *


# Create your views here.
def get_article_statistics(request):
    # 获取文章总数
    total_articles = Article.objects.count()

    # 获取点赞量最高的文章的作者
    top_liked_article = Article.objects.order_by('-likenum').first()
    top_liked_author = top_liked_article.authorname if top_liked_article else None

    # 获取发表文章最多的城市，跳过 region 为 null 的值
    top_cities = Article.objects.exclude(region__isnull=True).values('region').annotate(
        article_count=Count('id')).order_by('-article_count')[:2]

    # 将 create_at 转换为日期，假设你的日期格式为 'YYYY-MM-DD'
    article_counts = Article.objects.annotate(
        date=Cast('create_at', output_field=models.DateField())  # Cast 只能用于格式化正确的日期
    ).values('date').annotate(count=Count('id')).order_by('date')

    # 获取不同文章类型的占比
    article_type_data = Article.objects.values('type').annotate(type_count=Count('id'))

    # 获取评论区的用户名
    usernames = Comments.objects.values_list('authorname', flat=True)

    # 定义要删除的高频词列表
    stop_words = ['我', '你', '他', '的', '是', '啊']

    # 对用户名进行分词并统计词频
    words = []
    for username in usernames:
        for word in jieba.cut(username):
            if word not in stop_words:
                words.append(word)

    # 对词语进行统计
    word_counts = Counter(words)

    # 只取前十五条数据
    top_fifteen = dict(word_counts.most_common(15))

    # 准备词云图数据，转换成字典数据
    wordcloud_data = [{'name': word, 'value': count} for word, count in top_fifteen.items()]

    # 准备数据
    dates = [item['date'].strftime('%Y-%m-%d') for item in article_counts]
    counts = [item['count'] for item in article_counts]
    article_type_list = [{'value': entry['type_count'], 'name': entry['type']} for entry in article_type_data]

    if top_cities:
        top_city_name = top_cities[0]['region']
    else:
        top_city_name = None

    # 如果第一名是 null，取第二名
    if top_city_name is None and len(top_cities) > 1:
        top_city_name = top_cities[1]['region']

    # 获取点赞量最多的前四条评论
    top_comments_list = Comments.objects.order_by('-like_counts')[:4].values('authorname', 'content', 'like_counts')

    # 将 QuerySet 转换为列表
    top_comments_list = list(top_comments_list)

    data = {
        'total_articles': total_articles,
        'top_liked_author': top_liked_author,
        'top_city': top_city_name,
        'top_comments_list': top_comments_list,
        'dates': dates,
        'counts': counts,
        'article_type_data': article_type_list,
        'wordcloud_data': wordcloud_data,
    }

    return JsonResponse(data)


def get_hot_words_statistics(request):
    word_frequency_data = WordFrequency.objects.all()

    # 处理词频数据并进行情感分析
    hot_words_list = []
    for word_frequency in word_frequency_data:
        word = word_frequency.word
        frequency = word_frequency.frequency
        sentiment_score = SnowNLP(word).sentiments

        # 确定情感类型
        if sentiment_score > 0.5:
            sentiment = "正面"
        elif sentiment_score < 0.5:
            sentiment = "负面"
        else:
            sentiment = "中性"

        hot_words_list.append({
            'word': word,
            'frequency': frequency,
            'sentiment': sentiment,
        })

        # 处理分页查询
        selected_word = request.GET.get('selectedWord', '')
        page = request.GET.get('page', 1)  # 获取当前页码，默认第1页
        page_size = request.GET.get('pageSize', 10)  # 每页显示多少数据，默认10条

        # 查询评论内容中包含 selectedWord 的评论
        comments_query = Comments.objects.filter(content__icontains=selected_word)
        # 分页处理
        paginator = Paginator(comments_query, page_size)
        comments_page = paginator.get_page(page)

        # 将查询结果转换为字典列表，方便返回前端
        comments_list = [{
            'articleId': comment.articleid_id,
            'authorName': comment.authorname,
            'authorGender': comment.authorgender,
            'authorAddress': comment.authoraddress,
            'content': comment.content,
            'like_counts': comment.like_counts,
        } for comment in comments_page]

    # 返回 JSON 响应
    return JsonResponse({'hot_words_data': hot_words_list,
                         'total': paginator.count,
                         'currentPage': comments_page.number,
                         'pageSize': paginator.per_page,
                         'allComments': comments_list
                         })


def get_articles_with_comments(request):
    # 获取分页参数
    page = request.GET.get('page', 1)  # 默认为第一页
    page_size = request.GET.get('page_size', 6)  # 默认为每页6条数据

    # 获取所有文章并计算评论量
    articles = Article.objects.annotate(comment_count=Count('comments'))

    # 使用Paginator进行分页
    paginator = Paginator(articles, page_size)
    paginated_articles = paginator.get_page(page)

    # 创建一个结果列表，包含文章信息和评论量
    results = []
    for article in paginated_articles:
        # 使用 SnowNLP 进行情感分析
        s = SnowNLP(article.content)
        if s.sentiments > 0.5:
            sentiment = "正面"
        elif s.sentiments == 0.5:
            sentiment = "中性"
        else:
            sentiment = "负面"

        results.append({
            'articleId': article.id,
            'region': article.region,
            'reposts_count': article.reposts_count,
            'comment_count': article.comment_count,  # 评论量
            'like_count': article.likenum,
            'type': article.type,
            'content': article.content,
            'create_at': article.create_at,
            'detailUrl': article.detailurl,  # 文章详情页
            'judge': sentiment,  # 情感分类
        })

    # 返回分页结果和总条数
    return JsonResponse({
        'data': results,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': paginated_articles.number
    })


def article_analysis(request):
    # 查询所有文章的类型并去重
    article_types = Article.objects.values_list('type', flat=True).distinct()
    selected_type = request.GET.get('type', None)

    # 查询筛选后的文章
    if selected_type:
        articles = Article.objects.filter(type=selected_type)
    else:
        articles = Article.objects.all()

    # 定义统计区间
    like_intervals = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 5000), (5000, 10000), (10000, float('inf'))]
    comment_intervals = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 5000), (5000, float('inf'))]
    repost_intervals = [(0, 1000), (1000, 2000), (2000, 3000), (3000, 5000), (5000, float('inf'))]

    # 统计点赞量、评论量、转发量
    def get_interval_count(articles, field, intervals):
        interval_count = defaultdict(int)
        for article in articles:
            value = getattr(article, field)
            for start, end in intervals:
                if start <= value < end:
                    interval_count[f"{start}-{end}"] += 1
                    break
        return interval_count

    like_counts = get_interval_count(articles, 'likenum', like_intervals)
    comment_counts = get_interval_count(articles, 'commentnum', comment_intervals)
    repost_counts = get_interval_count(articles, 'reposts_count', repost_intervals)

    # 返回类型列表
    return JsonResponse({'types': list(article_types),
                         'like_counts': like_counts,
                         'comment_counts': comment_counts,
                         'repost_counts': repost_counts})


def region_analysis(request):
    # 统计每个地区的文章数
    article_counts = (
        Article.objects.values('region')  # 以地区分组
        .annotate(article_count=Count('id'))  # 统计每个地区的文章数
        .order_by('region')  # 排序
    )

    # 统计每个地区的评论数
    comment_counts = (
        Comments.objects.values('region')  # 以地区分组
        .annotate(comment_count=Count('articleid'))  # 统计每个地区的评论数
        .order_by('region')  # 排序
    )

    # 将结果组合成一个列表，以便返回给前端
    article_data_list = [
        {'region': item['region'], 'article_count': item['article_count']}
        for item in article_counts
    ]

    comment_data_list = [
        {'region': item['region'], 'comment_count': item['comment_count']}
        for item in comment_counts
    ]

    # 返回给前端的 JSON 数据
    return JsonResponse({
        'articleDataList': article_data_list,
        'commentDataList': comment_data_list
    })


def comments_analysis(request):
    # 定义点赞数区间为每 20 个一组
    interval = 20

    # 统计每个区间的评论数
    like_bins = Comments.objects.values('like_counts').annotate(count=Count('id'))

    # 整理数据到区间中
    bins = {}
    for item in like_bins:
        like_count = item['like_counts'] if item['like_counts'] is not None else 0
        bin_index = (like_count // interval) * interval
        if bin_index in bins:
            bins[bin_index] += item['count']
        else:
            bins[bin_index] = item['count']

    # 构建前端需要的数据格式
    response_data = []
    for bin_start, count in sorted(bins.items()):
        response_data.append({
            'like_range': f"{bin_start}-{bin_start + interval}",
            'comment_count': count
        })

    # 性别数据
    gender_counts = Comments.objects.values_list('authorgender', flat=True)
    gender_counter = Counter(gender_counts)

    # 获取词频数据
    word_frequencies = WordFrequency.objects.all().values('word', 'frequency')
    word_data = [{'name': wf['word'], 'value': wf['frequency']} for wf in word_frequencies]

    return JsonResponse({
        'data': response_data,
        'gender_data': [{'name': gender, 'value': count} for gender, count in gender_counter.items()],
        'word_data': word_data
    })


def sentiment_analysis(request):
    # 获取所有文章内容和评论内容
    articles = Article.objects.all().values_list('content', flat=True)
    comments = Comments.objects.all().values_list('content', flat=True)

    stopwords = load_stopwords()

    # 1. 获取文章热词分析（前十个词以及它们的频率）
    top_keywords = get_top_keywords(articles, stopwords)

    # 2. 统计文章内容的情感
    article_sentiment = analyze_sentiment(articles)

    # 3. 统计文章和评论内容的情感
    comment_sentiment = analyze_sentiment(comments)

    # 4.统计热词的情感
    all_words = []
    for content in articles:
        # 使用jieba进行分词
        words = jieba.cut(content)
        # 过滤掉停用词和单个字的词
        filtered_words = [word for word in words if
                          word not in stopwords and len(word) > 1 and re.match(r'^[\u4e00-\u9fa5]+$', word)]
        all_words.extend(filtered_words)

    keywords_sentiment = analyze_sentiment(all_words)

    # 返回结果
    return JsonResponse({
        'top_keywords': top_keywords,
        'article_sentiment': article_sentiment,
        'comment_sentiment': comment_sentiment,
        'keywords_sentiment': keywords_sentiment
    })


def article_content_word_cloud(request):
    stopwords = load_stopwords()

    # 获取文章内容 (假设文章存在数据库中)
    articles = Article.objects.values_list('content', flat=True)
    full_text = ' '.join(articles)  # 将所有文章合并为一个字符串

    # 使用jieba进行分词
    words = jieba.lcut(full_text)

    # 只保留中文词语，并去掉停用词
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1 and word.isalpha() and all(
        '\u4e00' <= char <= '\u9fff' for char in word)]

    # 统计词频
    word_freq = Counter(filtered_words).most_common(100)  # 取前100个词语

    # 返回词语和词频数据
    return JsonResponse({'word_cloud': word_freq})


def get_hot_search_data(request):
    # 获取请求中的分页参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))

    url = 'https://weibo.com/ajax/statuses/mineBand'
    headers = {
        'Cookie': 'SINAGLOBAL=1984169755402.2407.1630424811319; SCF=AnamYq1gZv9LGPDy7XY42aNFXwRyLUhVSKbNMdmglCAKxYm16jLRNZI7OcctnpFCCXqbiCdLISYkdImnKYxvk6I.; WBPSESS=tBnnI-QNHYIH4eVw5OhdtioMLcDqMwhNG_1HxdYfBbe9i6eO82u54wwcJr8D8MOnsaLoGqsVXy6vwKsj2mIZzd-UAmI7T_vqc1YHRl2Bdmp_M8tZdv4HGIKRwOVc9d1N_-38koOLeOCm84dGbLOOzA==; ULV=1728978218115:2:2:2:4342820146727.9526.1728978218077:1728390722842; ALF=1731572878; SUB=_2A25KClfcDeRhGeNG7VsV8SbFwz2IHXVpZtUUrDV8PUJbkNAGLUrMkW1NSzm19AyWoBzzmfJy2e6MweeaUz79tXIk; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhrU4fuzK4QyW-e0q8Y2ddg5JpX5KMhUgL.Fo-RSo.XeKn41h22dJLoIXnLxKBLBonL122LxKqLBo-LBoMLxK-LBKBLBKMLxK-LB-BLBKqLxKML1KBL1-qLxKqL1heLBoeLxK.L1h2L1-zLxKML12zL1KMt; PC_TOKEN=5a03a8b4ee; XSRF-TOKEN=Cn-jVsw3EAcNXZKoZJPAxZ2T',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    }
    response = requests.get(url, headers=headers)
    hot_search_list = []

    if response.status_code == 200:
        for item in response.json()['data']['realtime']:
            word = item.get('word')  # 使用 get 方法来安全获取字段
            description = item.get('description', '无描述')  # 如果没有 description，默认显示 '无描述'
            s = SnowNLP(word)
            sentiment_score = s.sentiments  # 获取情感得分，范围为0到1
            if sentiment_score > 0.51:
                sentiment = '正面'
            elif sentiment_score < 0.50:
                sentiment = '负面'
            elif 0.50 < sentiment_score < 0.51:
                sentiment = '中性'
            hot_search_list.append({'content': word, 'sentiment': sentiment, 'description': description})

    # 分页处理
    paginator = Paginator(hot_search_list, page_size)
    current_page_data = paginator.get_page(page)

    # 统计情感数量
    sentiment_count = {
        '正面': sum(1 for item in hot_search_list if item['sentiment'] == '正面'),
        '中性': sum(1 for item in hot_search_list if item['sentiment'] == '中性'),
        '负面': sum(1 for item in hot_search_list if item['sentiment'] == '负面')
    }

    return JsonResponse({
        'total': paginator.count,  # 数据总数
        'page': page,
        'page_size': page_size,
        'hot_search_data': list(current_page_data),  # 当前页的数据
        'sentiment_count': sentiment_count,  # 情感统计数量
    })
