import more_itertools

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):
    def popular(self):
        popular_posts = self.annotate(
            total_likes=Count('likes', distinct=True)
        ).order_by('-total_likes')
        return popular_posts

    def fresh(self):
        fresh_posts = self.order_by('-published_at')
        return fresh_posts

    def fetch_with_comments_count(self):
        return self.annotate(total_comments=Count('comments'))

    def fetch_posts_count_for_tags(self):
        return self.prefetch_related(
            Prefetch('tags', queryset=Tag.objects.annotate(posts_with_tag=Count('posts')))
        )


class TagQuerySet(models.QuerySet):
    def popular(self):
        popular_tags = self.annotate(
            total_posts=Count('posts', distinct=True)
        ).order_by('-total_posts')
        return popular_tags


class CommentQuerySet(models.QuerySet):
    def fetch_comments_on_post(self, post):
        comments_by_post = self.select_related().filter(post=post)
        serialized_comments = []
        for comment in comments_by_post:
            serialized_comments.append({
                'text': comment.text,
                'published_at': comment.published_at,
                'author': comment.author.username,
            })
        return serialized_comments


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    objects = CommentQuerySet.as_manager()

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
