from django.shortcuts import render
from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.total_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        "tags": post.total_tags,
        'first_tag_title': post.total_tags['title'],
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.total_posts,
    }


def index(request):
    most_popular_posts = Post.objects.popular()[:5] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    most_fresh_posts = Post.objects.fresh()[:5] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.filter(slug=slug) \
        .popular() \
        .prefetch_related('author') \
        .fetch_posts_count_for_tags()[0]
    serialized_comments = Comment.objects.fetch_comments_by_post(post)

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.total_likes,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': post.total_tags,
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular()[:5] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    context = {
        'post': serialized_post,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_posts = Post.objects.popular()[:5] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    related_posts = tag.posts.all()[:20] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        "posts": [
            serialize_post(post) for post in related_posts
        ],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
