from django.db import models


# Create your models here.
class Article(models.Model):
    id = models.BigIntegerField(primary_key=True)
    likenum = models.BigIntegerField(db_column='likeNum', blank=True, null=True)  # Field name made lowercase.
    commentnum = models.BigIntegerField(db_column='commentNum', blank=True, null=True)  # Field name made lowercase.
    reposts_count = models.BigIntegerField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    contentlength = models.BigIntegerField(db_column='contentLength', blank=True,
                                           null=True)  # Field name made lowercase.
    create_at = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    detailurl = models.TextField(db_column='detailUrl', blank=True, null=True)  # Field name made lowercase.
    authoravatar = models.TextField(db_column='authorAvatar', blank=True, null=True)  # Field name made lowercase.
    authorname = models.TextField(db_column='authorName', blank=True, null=True)  # Field name made lowercase.
    authordetail = models.TextField(db_column='authorDetail', blank=True, null=True)  # Field name made lowercase.
    isvip = models.FloatField(db_column='isVip', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'article'


class Comments(models.Model):
    articleid = models.ForeignKey(Article, models.DO_NOTHING, db_column='articleId', blank=True,
                                  null=True)  # Field name made lowercase.
    created_at = models.TextField(blank=True, null=True)
    like_counts = models.BigIntegerField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    authorname = models.TextField(db_column='authorName', blank=True, null=True)  # Field name made lowercase.
    authorgender = models.TextField(db_column='authorGender', blank=True, null=True)  # Field name made lowercase.
    authoraddress = models.TextField(db_column='authorAddress', blank=True, null=True)  # Field name made lowercase.
    authoravatar = models.TextField(db_column='authorAvatar', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'comments'


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class WordFrequency(models.Model):
    word = models.TextField(blank=True, null=True)
    frequency = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'word_frequency'


class AiArticles(models.Model):
    id = models.BigIntegerField(primary_key=True)
    likenum = models.BigIntegerField(db_column='likeNum', blank=True, null=True)  # Field name made lowercase.
    commentnum = models.BigIntegerField(db_column='commentNum', blank=True, null=True)  # Field name made lowercase.
    reposts_count = models.BigIntegerField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    contentlength = models.BigIntegerField(db_column='contentLength', blank=True,
                                           null=True)  # Field name made lowercase.
    create_at = models.TextField(blank=True, null=True)
    detailurl = models.TextField(db_column='detailUrl', blank=True, null=True)  # Field name made lowercase.
    authorname = models.TextField(db_column='authorName', blank=True, null=True)  # Field name made lowercase.
    authordetail = models.TextField(db_column='authorDetail', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ai_articles'


class AiComments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    articleid = models.BigIntegerField(db_column='articleId', blank=True, null=True)  # Field name made lowercase.
    created_at = models.TextField(blank=True, null=True)
    like_counts = models.BigIntegerField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    authorname = models.TextField(db_column='authorName', blank=True, null=True)  # Field name made lowercase.
    authorgender = models.TextField(db_column='authorGender', blank=True, null=True)  # Field name made lowercase.
    authoraddress = models.TextField(db_column='authorAddress', blank=True, null=True)  # Field name made lowercase.
    authoravatar = models.TextField(db_column='authorAvatar', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ai_comments'


class AncientArticles(models.Model):
    id = models.BigIntegerField(primary_key=True)
    likenum = models.BigIntegerField(db_column='likeNum', blank=True, null=True)  # Field name made lowercase.
    commentnum = models.BigIntegerField(db_column='commentNum', blank=True, null=True)  # Field name made lowercase.
    reposts_count = models.BigIntegerField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    contentlength = models.BigIntegerField(db_column='contentLength', blank=True, null=True)  # Field name made lowercase.
    create_at = models.TextField(blank=True, null=True)
    detailurl = models.TextField(db_column='detailUrl', blank=True, null=True)  # Field name made lowercase.
    authorname = models.TextField(db_column='authorName', blank=True, null=True)  # Field name made lowercase.
    authordetail = models.TextField(db_column='authorDetail', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ancient_articles'


class AncientComments(models.Model):
    id = models.BigAutoField(primary_key=True)
    articleid = models.BigIntegerField(db_column='articleId', blank=True, null=True)  # Field name made lowercase.
    created_at = models.TextField(blank=True, null=True)
    like_counts = models.BigIntegerField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    authorname = models.TextField(db_column='authorName', blank=True, null=True)  # Field name made lowercase.
    authorgender = models.TextField(db_column='authorGender', blank=True, null=True)  # Field name made lowercase.
    authoraddress = models.TextField(db_column='authorAddress', blank=True, null=True)  # Field name made lowercase.
    authoravatar = models.TextField(db_column='authorAvatar', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ancient_comments'


class WordFrequencyAncient(models.Model):
    id = models.BigAutoField(primary_key=True)
    word = models.TextField(blank=True, null=True)
    frequency = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'word_frequency_ancient'


class AncientTech(models.Model):
    name = models.CharField(max_length=100)
    ancient_year = models.IntegerField()
    ancient_desc = models.TextField()
    ancient_model = models.FileField(upload_to='D:/PythonProjects/weibo_django/media/tech_models/')
    modern_model = models.FileField(upload_to='D:/PythonProjects/weibo_django/media/tech_models/')
    modern_desc = models.TextField()
    category = models.CharField(max_length=50)

    class Meta:
        db_table = 'ancient_technology'
