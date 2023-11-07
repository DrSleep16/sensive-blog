from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from blog.models import Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.total_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts__count,
    }


def index(request):
    popular_posts = Post.objects.popular(). \
        select_related('author') \
        .fetch_posts_count_for_tags() \
        .fetch_with_total_comments()[:5]

    fresh_posts = list(
        Post.objects \
        .annotate(total_comments=Count('comments', distinct=True)) \
        .order_by('published_at').select_related('author') \
        .fetch_posts_count_for_tags()
    )[-5:]

    popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in popular_posts],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    print(context)
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related('author').annotate(total_likes=Count('likes')),
        slug=slug,
    )

    comments = post.comments.select_related('author').all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': post.author,
        })

    related_tags = post.tags.annotate(posts__count=Count('posts'))

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.total_likes,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    popular_tags = Tag.objects.popular()[:5]

    popular_posts = Post.objects.popular(). \
        select_related('author'). \
        fetch_posts_count_for_tags(). \
        fetch_with_total_comments()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'popular_posts': [serialize_post(post) for post in popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    popular_posts = Post.objects.popular() \
        .select_related('author') \
        .fetch_posts_count_for_tags() \
        .fetch_with_total_comments()[:5]

    related_posts = tag.posts.fetch_posts_count_for_tags().select_related('author').all()[:20]
    related_posts = related_posts.annotate(total_comments=Count('comments'))

    popular_tags = Tag.objects.popular()[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        'popular_posts': [serialize_post(post) for post in popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html')
