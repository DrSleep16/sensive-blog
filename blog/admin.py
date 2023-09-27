from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ['post', 'author']
    list_display = (
        'text',
        'published_at',
        'author_username',
        'post_title'
    )

    def author_username(self, obj):
        return obj.author.username

    def post_title(self, obj):
        return obj.post.title

    author_username.short_description = 'Автор'
    post_title.short_description = 'Пост'

    list_select_related = ('author', 'post')
    list_prefetch_related = ('post__author',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ['author', 'likes', 'tags']


admin.site.register(Tag)
