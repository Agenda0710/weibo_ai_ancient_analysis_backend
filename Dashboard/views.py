import json
from django.core.paginator import Paginator
from django.db.models.functions import Cast
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import JsonResponse
from django.db.models import Count
from collections import defaultdict
from .utils.sentimentAnalysis import *
from .spiders.spiderNews import *
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from .spiders.spiderHotSearch import get_hot_search_data as HotSearchData
from .spider_ancient.spider_ancient_search import get_weibo_search_text, get_weibo_search_hot_query
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import networkx as nx
from .spider_ancient.spider_ancient_policies import get_ancient_policies_information
import redis
import threading
import time

# Create your views here.
# Redis连接配置
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def get_article_statistics(request):
    """首页数据 - 使用Redis缓存结果"""
    cache_key = "article_statistics"
    cached_data = r.get(cache_key)

    # 如果缓存存在且有效，直接返回
    if cached_data:
        return JsonResponse(json.loads(cached_data))

    # 获取文章总数
    total_articles = AncientArticles.objects.count()

    # 获取点赞量最高的文章的作者
    top_liked_article = AncientArticles.objects.order_by('-likenum').first()
    top_liked_author = top_liked_article.authorname if top_liked_article else None

    # 获取发表文章最多的城市，跳过 region 为 null 的值
    top_cities = AncientArticles.objects.exclude(region__isnull=True).values('region').annotate(
        article_count=Count('id')).order_by('-article_count')[:2]

    # 将 create_at 转换为日期
    article_counts = AncientArticles.objects.annotate(
        date=Cast('create_at', output_field=models.DateField())
    ).values('date').annotate(count=Count('id')).order_by('date')

    # 获取不同文章长度的占比
    ranges = [
        (0, 100), (100, 200), (200, 500),
        (500, 1000), (1000, 2000)
    ]

    ai_article_word_length_list = []
    for rng in ranges:
        count = AncientArticles.objects.filter(contentlength__gte=rng[0], contentlength__lt=rng[1]).count()
        ai_article_word_length_list.append({"value": count, "name": f"{rng[0]}-{rng[1]}"})

    # 查询大于2000的文章数量
    count_2000_plus = AncientArticles.objects.filter(contentlength__gte=2000).count()
    ai_article_word_length_list.append({"value": count_2000_plus, "name": "2000+"})

    # 获取文章的用户名
    usernames = AncientArticles.objects.values_list('authorname', flat=True)

    # 定义要删除的高频词列表
    stop_words = load_stopwords()

    # 对用户名进行分词并统计词频
    words = []
    for username in usernames:
        for word in jieba.cut(username):
            if word not in stop_words and re.match(r'[\u4e00-\u9fff]+', word):
                words.append(word)

    # 对词语进行统计
    word_counts = Counter(words)
    top_fifteen = dict(word_counts.most_common(15))
    wordcloud_data = [{'name': word, 'value': count} for word, count in top_fifteen.items()]

    # 准备数据
    dates = [item['date'].strftime('%Y-%m-%d') for item in article_counts]
    counts = [item['count'] for item in article_counts]
    top_city_name = top_cities[1]['region'] if top_cities and not top_cities[0]['region'] else top_cities[0][
        'region'] if top_cities else None

    # 获取点赞量最多的前四条评论
    top_comments_list = list(AncientComments.objects.order_by('-like_counts')[:4].values(
        'authorname', 'content', 'like_counts'))

    data = {
        'total_articles': total_articles,
        'top_liked_author': top_liked_author,
        'top_city': top_city_name,
        'top_comments_list': top_comments_list,
        'dates': dates,
        'ai_article_word_length_list': ai_article_word_length_list,
        'counts': counts,
        'wordcloud_data': wordcloud_data,
    }

    # 缓存结果（5分钟过期）
    r.setex(cache_key, 300, json.dumps(data))
    return JsonResponse(data)


def get_hot_words_statistics(request):
    """
    获取评论热词数据（带Redis缓存）
    """
    # 生成唯一的缓存键
    cache_key = f"hot_words:{request.GET.get('selectedWord','')}:{request.GET.get('page',1)}"

    # 检查缓存
    cached_data = r.get(cache_key)
    if cached_data:
        return JsonResponse(json.loads(cached_data))

    # 获取词频数据
    word_frequency_data = WordFrequencyAncient.objects.all()
    hot_words_list = []

    # 处理词频数据并进行情感分析
    for word_frequency in word_frequency_data:
        word = word_frequency.word
        frequency = word_frequency.frequency

        # 简单情感分析
        sentiment = "中性"  # 默认值
        try:
            sentiment_score = SnowNLP(word).sentiments
            sentiment = "正面" if sentiment_score > 0.6 else "负面" if sentiment_score < 0.4 else "中性"
        except:
            pass

        hot_words_list.append({
            'word': word,
            'frequency': frequency,
            'sentiment': sentiment,
        })

    # 处理分页查询
    selected_word = request.GET.get('selectedWord', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('pageSize', 10))

    comments_query = AncientComments.objects.filter(content__icontains=selected_word)
    paginator = Paginator(comments_query, page_size)
    comments_page = paginator.get_page(page)

    comments_list = [{
        'articleId': comment.articleid,
        'authorName': comment.authorname,
        'authorGender': comment.authorgender,
        'authorAddress': comment.authoraddress,
        'content': comment.content,
        'like_counts': comment.like_counts,
    } for comment in comments_page]

    response_data = {
        'hot_words_data': hot_words_list,
        'total': paginator.count,
        'currentPage': page,
        'pageSize': page_size,
        'allComments': comments_list
    }

    # 缓存结果（5分钟过期）
    r.setex(cache_key, 300, json.dumps(response_data))
    return JsonResponse(response_data)


def get_articles_with_comments(request):
    """
    文章数据展示（带Redis缓存）
    :param request:
    :return:
    """
    # 获取分页参数
    page = request.GET.get('page', 1)  # 默认为第一页
    page_size = request.GET.get('page_size', 6)  # 默认为每页6条数据

    # 创建唯一的缓存键
    cache_key = f"articles_with_comments:{page}:{page_size}"

    # 检查是否有缓存
    cached_data = r.get(cache_key)
    if cached_data:
        return JsonResponse(json.loads(cached_data))

    # 获取所有文章并计算评论量
    articles = AncientArticles.objects.annotate(comment_count=Count('commentnum'))

    # 使用Paginator进行分页
    paginator = Paginator(articles, page_size)
    paginated_articles = paginator.get_page(page)

    # 创建一个结果列表，包含文章信息和评论量
    results = []
    for article in paginated_articles:
        results.append({
            'articleId': article.id,
            'region': article.region,
            'reposts_count': article.reposts_count,
            'comment_count': article.comment_count,  # 评论量
            'like_count': article.likenum,
            'content_length': article.contentlength,
            'content': article.content,
            'create_at': article.create_at,
            'detailUrl': article.detailurl,  # 文章详情页
        })

    # 进行情感分析
    words = [item['content'] for item in results]
    sentiments = analyze_article_sentiment(words)

    # 将情感分析结果添加到结果中
    for index, sentiment in enumerate(sentiments):
        results[index]['judge'] = sentiment

    # 准备响应数据
    response_data = {
        'data': results,
        'total': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': paginated_articles.number
    }

    # 将结果存入Redis缓存（5分钟过期）
    r.setex(cache_key, 300, json.dumps(response_data))

    return JsonResponse(response_data)


def article_analysis(request):
    """文章内容分析 - 使用Redis缓存结果"""
    cache_key = "article_analysis"
    cached_data = r.get(cache_key)

    if cached_data:
        return JsonResponse(json.loads(cached_data))

    articles = AncientArticles.objects.all()

    # 定义统计区间
    like_intervals = [(0, 100), (100, 200), (200, 300), (300, 500), (500, 1000), (1000, float('inf'))]
    comment_intervals = [(0, 100), (100, 200), (200, 300), (300, 500), (500, float('inf'))]
    repost_intervals = [(0, 100), (100, 200), (200, 300), (300, 500), (500, float('inf'))]

    def get_interval_count(articles, field, intervals):
        interval_count = defaultdict(int)
        for article in articles:
            value = getattr(article, field)
            for start, end in intervals:
                if start <= value < end:
                    interval_count[f"{start}-{end}"] += 1
                    break
        return interval_count

    response_data = {
        'like_counts': get_interval_count(articles, 'likenum', like_intervals),
        'comment_counts': get_interval_count(articles, 'commentnum', comment_intervals),
        'repost_counts': get_interval_count(articles, 'reposts_count', repost_intervals)
    }

    # 缓存结果（10分钟过期）
    r.setex(cache_key, 600, json.dumps(response_data))
    return JsonResponse(response_data)


def region_analysis(request):
    """IP地址分析 - 使用Redis缓存结果"""
    cache_key = "region_analysis"
    cached_data = r.get(cache_key)

    if cached_data:
        return JsonResponse(json.loads(cached_data))

    article_counts = (
        AncientArticles.objects.values('region')
        .annotate(article_count=Count('id'))
        .order_by('region')
    )

    comment_counts = (
        AncientComments.objects.values('region')
        .annotate(comment_count=Count('articleid'))
        .order_by('region')
    )

    response_data = {
        'articleDataList': [
            {'region': item['region'], 'article_count': item['article_count']}
            for item in article_counts
        ],
        'commentDataList': [
            {'region': item['region'], 'comment_count': item['comment_count']}
            for item in comment_counts
        ]
    }

    # 缓存结果（15分钟过期）
    r.setex(cache_key, 900, json.dumps(response_data))
    return JsonResponse(response_data)


def comments_analysis(request):
    """评论分析 - 使用Redis缓存结果"""
    cache_key = "comments_analysis"
    cached_data = r.get(cache_key)

    if cached_data:
        return JsonResponse(json.loads(cached_data))

    interval = 20
    like_bins = AncientComments.objects.values('like_counts').annotate(count=Count('id'))

    bins = {}
    for item in like_bins:
        like_count = item['like_counts'] or 0
        bin_index = (like_count // interval) * interval
        bins[bin_index] = bins.get(bin_index, 0) + item['count']

    response_data = []
    for bin_start, count in sorted(bins.items()):
        response_data.append({
            'like_range': f"{bin_start}-{bin_start + interval}",
            'comment_count': count
        })

    gender_counts = AncientComments.objects.values_list('authorgender', flat=True)
    gender_counter = Counter(gender_counts)

    word_frequencies = WordFrequencyAncient.objects.all().values('word', 'frequency')
    word_data = [{'name': wf['word'], 'value': wf['frequency']} for wf in word_frequencies[:35]]

    result = {
        'data': response_data,
        'gender_data': [{'name': gender, 'value': count} for gender, count in gender_counter.items()],
        'word_data': word_data
    }

    # 缓存结果（10分钟过期）
    r.setex(cache_key, 600, json.dumps(result))
    return JsonResponse(result)


# 缓存键名和过期时间（1小时）
SENTIMENT_CACHE_KEY = "sentiment_analysis_result"
CACHE_EXPIRE = 3600


def sentiment_analysis(request):
    """
    文章内容+评论的情感分析（带Redis缓存）
    :param request:
    :return:
    """
    # 检查缓存是否存在
    cached_result = r.get(SENTIMENT_CACHE_KEY)
    if cached_result:
        print("从缓存中获取情感分析结果")
        return JsonResponse(json.loads(cached_result))

    print("计算新的情感分析结果...")
    start_time = time.time()

    # 获取所有文章内容和评论内容
    articles = [article for article in AncientArticles.objects.all().values_list('content', flat=True) if
                article and isinstance(article, str)]
    comments = [comment for comment in AncientComments.objects.all().values_list('content', flat=True) if
                comment and isinstance(comment, str)]

    stopwords = load_stopwords()

    # 1. 获取文章热词分析（前十个词以及它们的频率）
    top_keywords = get_top_keywords(articles, stopwords)

    # 2. 统计文章内容的情感
    article_sentiments = analyze_article_sentiment(list(articles))
    article_positive_count = sum([1 for sentiment in article_sentiments if sentiment == "正面"])
    article_neutral_count = sum([1 for sentiment in article_sentiments if sentiment == "中性"])
    article_negative_count = sum([1 for sentiment in article_sentiments if sentiment == "负面"])

    # 3. 统计评论内容的情感
    comment_sentiments = analyze_article_sentiment(list(comments))
    comment_positive_count = sum([1 for sentiment in comment_sentiments if sentiment == "正面"])
    comment_neutral_count = sum([1 for sentiment in comment_sentiments if sentiment == "中性"])
    comment_negative_count = sum([1 for sentiment in comment_sentiments if sentiment == "负面"])

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

    # 构建结果
    result = {
        'top_keywords': top_keywords,
        'article_sentiment': {
            'positive': article_positive_count,
            'neutral': article_neutral_count,
            'negative': article_negative_count
        },
        'comment_sentiment': {
            'positive': comment_positive_count,
            'neutral': comment_neutral_count,
            'negative': comment_negative_count
        },
        'keywords_sentiment': keywords_sentiment
    }

    # 将结果存入Redis缓存
    r.setex(SENTIMENT_CACHE_KEY, CACHE_EXPIRE, json.dumps(result))

    print(f"情感分析计算完成，耗时: {time.time() - start_time:.2f}秒")

    return JsonResponse(result)


def article_content_word_cloud(request):
    """
    微博内容词云图的分析
    :param request:
    :return:
    """
    stopwords = load_stopwords()

    # 获取文章内容 (假设文章存在数据库中)
    articles = AncientArticles.objects.values_list('content', flat=True)
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
    """
    热搜数据展示 and 热搜的情感分析 + Flask AI 综合解读
    :param request:
    :return:
    """
    # 获取前 50 个热搜数据
    hot_search_list = HotSearchData()[:50]

    # 提取内容
    words = [item['content'] for item in hot_search_list]

    # 批量情感分析
    sentiments = analyze_article_sentiment(words)
    for i, sentiment in enumerate(sentiments):
        hot_search_list[i]['sentiment'] = sentiment

    # 调用 Flask 新 AI 接口
    flask_ai_url = "http://127.0.0.1:5000/analyze_hot_trends"
    ai_response = {"ai_interpretation": "暂无解析结果"}  # 默认值

    try:
        response = requests.post(flask_ai_url, json={"hot_queries": words})
        if response.status_code == 200:
            ai_response = response.json()
    except requests.RequestException as e:
        print(f"调用 Flask AI 接口失败: {e}")

    # 统计情感数量
    sentiment_count = {
        '正面': sum(1 for item in hot_search_list if item['sentiment'] == '正面'),
        '中性': sum(1 for item in hot_search_list if item['sentiment'] == '中性'),
        '负面': sum(1 for item in hot_search_list if item['sentiment'] == '负面')
    }

    # 返回数据
    return JsonResponse({
        'total': len(hot_search_list),  # 数据总数
        'hot_search_data': hot_search_list,  # 所有热搜数据
        'sentiment_count': sentiment_count,  # 情感统计数量
        'ai_interpretation': ai_response.get("ai_interpretation"),  # AI 综合解析结果
    })


def get_current_news(request):
    """
    新闻页面的展示和新闻的分类
    :param request: HTTP 请求对象
    :return: JSON 响应
    """
    # 获取新闻数据及创建时间
    news_data_analysis = getContentData()

    # 统计新闻分类
    category_counts = Counter(item['label'] for item in news_data_analysis)

    # 返回新闻内容、分类统计和创建时间
    return JsonResponse({
        'news_data_analysis': news_data_analysis,
        'category_counts': category_counts,
    })


def get_data_views(request):
    """
    数据大屏的数据展示
    :param request:
    :return:
    """
    # 返回表格数据
    comments_content = [
        comment for comment in
        AncientComments.objects.all().values_list('content', flat=True).order_by('created_at').reverse()
        if comment and isinstance(comment, str)
    ]
    comments_region = list(
        AncientComments.objects.all().values_list('region', flat=True).order_by('created_at').reverse()
    )
    comments_sentiments_analysis = analyze_article_sentiment(comments_content)
    comment_list = [
        {
            'comments_content': comment,
            'sentiments_analysis': sentiment,
            'comments_region': region
        }
        for comment, sentiment, region in zip(comments_content, comments_sentiments_analysis, comments_region)
    ]

    # 返回饼图数据
    # 获取不同文章长度的占比
    # 定义文章长度的区间
    ranges = [
        (0, 100),
        (100, 200),
        (200, 500),
        (500, 1000),
        (1000, 2000),
    ]

    ai_article_word_length_list = []
    for r in ranges:
        count = AncientArticles.objects.filter(contentlength__gte=r[0], contentlength__lt=r[1]).count()
        ai_article_word_length_list.append({"value": count, "name": f"{r[0]}-{r[1]}"})

    # 查询大于2000的文章数量
    count_2000_plus = AncientArticles.objects.filter(contentlength__gte=2000).count()
    ai_article_word_length_list.append({"value": count_2000_plus, "name": "2000+"})

    # 排名图
    news_data_analysis = getContentData()
    # 修正新闻类别统计问题
    news_category_counts = Counter(item['label'] for item in news_data_analysis)

    # 修正新闻词云数据提取问题
    news_contents = [
        item['news_data'] for item in news_data_analysis if item['news_data'] and isinstance(item['news_data'], str)
    ]

    # 加载停用词
    stop_words = load_stopwords()

    # 分词和过滤
    words = []
    for news_content in news_contents:
        for word in jieba.cut(news_content):
            if (
                    word not in stop_words
                    and re.match(r'^[\u4e00-\u9fa5]+$', word)  # 只匹配中文
                    and word not in ['了', '是', '在', '的', '一个', '有', '又', '也']  # 自定义过滤词
            ):
                words.append(word)

    # 统计词频
    word_counts = Counter(words)

    # 提取词频前 15 的词
    top_fifteen = dict(word_counts.most_common(15))

    # 生成词云图数据
    news_wordcloud_data = [{'name': word, 'value': count} for word, count in top_fifteen.items()]

    # 返回胶囊图数据，新闻情感
    news_sentiments_analysis = analyze_article_sentiment(news_contents)
    news_sentiments_statistic = Counter(news_sentiments_analysis)

    # 返回翻牌器数据，统计微博文章和评论的数量
    article_count = AncientArticles.objects.count()
    comment_count = AncientComments.objects.count()

    return JsonResponse({
        'comment_list': comment_list,
        'article_type_list': ai_article_word_length_list,
        'news_category_counts': news_category_counts,
        'news_wordcloud_data': news_wordcloud_data,
        'news_sentiments_statistic': news_sentiments_statistic,
        'article_count': article_count,
        'comment_count': comment_count,
    })


# 获取当前项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 加载保存的模型和分词器
model_path = os.path.join(BASE_DIR, "fine_tuned_bert_fake_news")
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()  # 设置为评估模式


@csrf_exempt  # 禁用 CSRF 验证
def predict_fake_or_real(request):
    """
    接收前端发送的新闻内容，返回预测结果（真假）。
    """
    if request.method == "POST":
        try:
            # 解析 JSON 数据
            data = json.loads(request.body)
            text = data.get("text", "")
            if not text:
                return JsonResponse({"error": "请输入有效的文本！"}, status=400)

            # 模型预测
            inputs = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=128)
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=-1).item()

            # 映射预测结果
            label_map = {0: "假新闻", 1: "真新闻"}
            prediction = label_map[predicted_class]

            return JsonResponse({"prediction": prediction}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "无效的 JSON 数据！"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "仅支持 POST 请求！"}, status=405)


# 加载模型和 Tokenizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
fraud_detection_tokenizer = BertTokenizer.from_pretrained(os.path.join(BASE_DIR, 'bert-fraud-detection'))
fraud_detection_model = BertForSequenceClassification.from_pretrained(
    os.path.join(BASE_DIR, 'bert-fraud-detection')).to(device)
fraud_category_tokenizer = BertTokenizer.from_pretrained(os.path.join(BASE_DIR, 'bert-fraud-category'))
fraud_category_model = BertForSequenceClassification.from_pretrained(os.path.join(BASE_DIR, 'bert-fraud-category')).to(
    device)

# 设置模型为评估模式
fraud_detection_model.eval()
fraud_category_model.eval()

# 定义欺诈类别映射
fraud_categories = {
    0: "刷单返利类", 1: "虚假网络投资理财类", 2: "冒充电商物流客服类",
    3: "贷款、代办信用卡类", 4: "网络游戏产品虚假交易类", 5: "虚假购物、服务类",
    6: "冒充公检法及政府机关类", 7: "网黑案件", 8: "虚假征信类",
    9: "冒充领导、熟人类", 10: "冒充军警购物类诈骗", 11: "网络婚恋、交友类（非虚假网络投资理财类）"
}


@csrf_exempt
def predict_junk_information(request):
    """
    接收前端POST请求，进行欺诈信息检测和分类
    """
    if request.method == "POST":
        try:
            # 从请求中获取数据
            data = json.loads(request.body)
            text = data.get("text", "")

            if not text:
                return JsonResponse({"error": "文本不能为空"}, status=400)

            # Step 1: 使用 'bert-fraud-detection' 判断是否是欺诈信息
            detection_encoding = fraud_detection_tokenizer(
                text, padding=True, truncation=True, max_length=128, return_tensors="pt"
            ).to(device)

            with torch.no_grad():
                detection_outputs = fraud_detection_model(**detection_encoding)

            detection_logits = detection_outputs.logits
            is_fraud = torch.argmax(detection_logits, dim=1).item()

            # 如果是正常信息，返回结果
            if is_fraud == 0:
                return JsonResponse({"result": "正常信息"}, status=200)

            # Step 2: 如果是欺诈信息，分类预测
            category_encoding = fraud_category_tokenizer(
                text, padding=True, truncation=True, max_length=256, return_tensors="pt"
            ).to(device)

            with torch.no_grad():
                category_outputs = fraud_category_model(**category_encoding)

            category_logits = category_outputs.logits
            predicted_category = torch.argmax(category_logits, dim=1).item()
            fraud_category = fraud_categories.get(predicted_category, "未知类别")

            # 返回分类结果
            return JsonResponse({
                "result": "欺诈信息",
                "category": fraud_category,
                "reason": f"模型检测到该文本与“{fraud_category}”相关的关键词或特定模式。"
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "仅支持POST请求"}, status=405)


def fetch_combined_ai_interpretation(hot_queries):
    """
    调用 Flask 服务，获取 Kimi AI 对热点话题的综合分析结果。
    """
    if not hot_queries:
        return "暂无热点话题，无法生成解读。"
    try:
        # 向 Flask 服务发送 POST 请求
        response = requests.post(
            "http://127.0.0.1:5000/fetch_ai_interpretation",
            json={"hot_queries": hot_queries},
        )
        response.raise_for_status()
        return response.json().get("ai_interpretation", "AI 解读生成失败")
    except Exception as e:
        return f"AI 解读生成失败，原因：{str(e)}"


@csrf_exempt
def weibo_search_analysis(request):
    """
    Django 视图，用于处理微博搜索分析请求。
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        keyword = data.get('keyword', '')

        if not keyword:
            return JsonResponse({"error": "Keyword cannot be empty"}, status=400)

        try:
            # 获取微博文章和热点话题
            weibo_articles = get_weibo_search_text(keyword)
            hot_queries = get_weibo_search_hot_query(keyword)

            # 调用情感分析函数
            sentiments = analyze_article_sentiment(weibo_articles)
            sentiment_counts = Counter(sentiments)

            # 使用 Kimi AI 综合分析热点话题
            ai_interpretation = fetch_combined_ai_interpretation(hot_queries[:15])

            # 生成词云数据
            stopwords = load_stopwords()
            word_frequencies = Counter()
            for article in weibo_articles:
                words = jieba.lcut(article)
                filtered_words = [word for word in words if word not in stopwords and len(word.strip()) > 1]
                word_frequencies.update(filtered_words)

            # 构造响应数据
            return JsonResponse({
                "hot_queries": [{"index": idx + 1, "content": query} for idx, query in enumerate(hot_queries[:15])],
                "articles": [{"index": idx + 1, "content": article, "sentiment": sentiment}
                             for idx, (article, sentiment) in enumerate(zip(weibo_articles[:10], sentiments[:10]))],
                "ai_interpretation": ai_interpretation,
                "sentiment_stats": {
                    "positive": sentiment_counts["正面"],
                    "neutral": sentiment_counts["中性"],
                    "negative": sentiment_counts["负面"],
                },
                "word_frequencies": word_frequencies.most_common(100),
            })

        except Exception as e:
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def analyze_ancient_policies(request):
    """
    获取非物质文化遗产相关政策，并分析，返回政策分类饼状图和词云数据
    """
    try:
        # 获取政策信息
        policies_data = get_ancient_policies_information()

        # 生成分类统计数据（用于饼状图）
        categories = [policy["category"] for policy in policies_data]
        category_counts = Counter(categories)
        category_chart_data = [{"name": k, "value": v} for k, v in category_counts.items()]

        # 调用 Flask 接口进行 AI 解读
        flask_url = "http://127.0.0.1:5000/analyze_ai_policies"
        ai_answer = "暂未生成ai模型解读"  # 默认值

        try:
            response = requests.post(flask_url, json={"policies": policies_data})
            response.raise_for_status()
            response_data = response.json()
            ai_answer = response_data.get("ai_interpretation", "AI 解读生成失败")
        except requests.exceptions.RequestException as e:
            print(f"Flask 接口调用失败: {e}")  # 控制台打印错误信息

        # 整理词云图数据
        stop_words = load_stopwords()
        stop_words.update(['的', '中共中央'])  # 添加更多停用词
        policies_title = [policy['title'] for policy in policies_data]

        # 政策标题进行词频统计
        words = []
        for policy_title in policies_title:
            for word in jieba.cut(policy_title):
                if word not in stop_words:
                    if re.match(r'[\u4e00-\u9fff]+', word):  # 只保留中文词
                        words.append(word)

        word_counter = Counter(words)

        # 只取前二十五条数据
        top_twenty_five = dict(word_counter.most_common(25))
        word_cloud_data = [{"name": word, "value": count} for word, count in top_twenty_five.items()]

        # 返回数据
        return JsonResponse({
            "policies": policies_data,
            "ai_analysis": ai_answer,
            "category_chart_data": category_chart_data,
            "word_cloud_data": word_cloud_data
        })

    except Exception as e:
        return JsonResponse({"error": f"服务器错误: {str(e)}"}, status=500)


def load_custom_stopwords():
    """
    返回手动定义的停用词列表
    """
    return [
        "一个", "一些", "可以", "我们", "你们", "他们", "自己", "这样", "这样子",
        "没有", "因为", "所以", "但是", "而且", "如果", "还是", "那么", "然后",
        "以及", "已经", "很多", "关于", "其中", "通过", "这种", "这种情况",
        "不同", "时候", "之后", "之前", "成为", "所有", "根据", "方面", "目前",
        "什么", "如何", "是否", "以及", "那么", "由于", "发布", "这些", "就是",
        "古代"
    ]


def extract_keywords(texts, top_n=30):
    """
    使用TF-IDF提取关键词，并筛除停用词
    :param texts: 文本列表
    :param top_n: 提取的关键词数量
    :return: 关键词列表
    """
    # 加载手动定义的停用词
    stopwords = set(load_custom_stopwords())

    # 使用jieba分词，手动去除停用词
    processed_texts = []
    for text in texts:
        words = jieba.lcut(text)
        filtered_words = [word for word in words if word not in stopwords and word.strip()]
        processed_texts.append(" ".join(filtered_words))

    # 手动清洗后的文本不再依赖TfidfVectorizer的stop_words参数
    vectorizer = TfidfVectorizer(max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform(processed_texts)
    feature_names = vectorizer.get_feature_names_out()

    # 进一步筛除停用词（保证安全性）
    final_keywords = [word for word in feature_names if word not in stopwords]

    return final_keywords


def build_co_occurrence_network(texts, keywords, min_co_occurrence=3):
    """
    构建关键词共现网络，过滤低频共现的边
    :param texts: 文本列表
    :param keywords: 关键词列表
    :param min_co_occurrence: 最低共现次数
    :return: 精简后的共现网络图
    """
    co_occurrence_graph = nx.Graph()

    # 初始化关键词节点
    for keyword in keywords:
        co_occurrence_graph.add_node(keyword)

    # 统计关键词共现次数
    for text in texts:
        words_in_text = jieba.lcut(text)
        for i in range(len(words_in_text)):
            if words_in_text[i] in keywords:
                for j in range(i + 1, len(words_in_text)):
                    if words_in_text[j] in keywords:
                        if co_occurrence_graph.has_edge(words_in_text[i], words_in_text[j]):
                            co_occurrence_graph[words_in_text[i]][words_in_text[j]]['weight'] += 1
                        else:
                            co_occurrence_graph.add_edge(words_in_text[i], words_in_text[j], weight=1)

    # 过滤掉低于 min_co_occurrence 次的边
    edges_to_remove = [(u, v) for u, v, d in co_occurrence_graph.edges(data=True) if d['weight'] < min_co_occurrence]
    co_occurrence_graph.remove_edges_from(edges_to_remove)

    return co_occurrence_graph


def generate_network_data(graph):
    """
    生成图谱数据
    :param graph: 共现网络图
    :return: 图谱数据（节点和边）
    """
    nodes = [{"id": node, "label": node, "value": graph.degree(node)} for node in graph.nodes()]
    edges = [{"from": edge[0], "to": edge[1], "value": graph[edge[0]][edge[1]]['weight']} for edge in graph.edges()]

    return {"nodes": nodes, "edges": edges}


def get_tech_hotspot_graph(request):
    """
    获取技术热点图谱数据
    """
    # 从数据库中获取文章内容
    articles = AncientArticles.objects.values_list('content', flat=True)
    texts = [article for article in articles if article and isinstance(article, str)]

    # 提取关键词
    keywords = extract_keywords(texts, top_n=10)

    important_keywords = keywords[:30]  # 仅选择前30个最重要的关键词
    co_occurrence_graph = build_co_occurrence_network(texts, important_keywords)

    # 生成图谱数据
    graph_data = generate_network_data(co_occurrence_graph)

    return JsonResponse(graph_data)
