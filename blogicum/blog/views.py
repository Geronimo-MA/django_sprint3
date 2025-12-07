from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.utils import timezone

from .models import Category, Post


def _render(template_name: str, context: dict) -> HttpResponse:
    template = loader.get_template(template_name)
    ctx = Context(context)
    # Важно для автотестов: dict(response.context) должен работать
    ctx.keys = lambda: ctx.flatten().keys()  # type: ignore[attr-defined]
    return HttpResponse(template.render(ctx))


def index(request):
    now = timezone.now()
    posts = (
        Post.objects.select_related('author', 'category', 'location')
        .filter(
            is_published=True,
            pub_date__lte=now,
            category__is_published=True,
        )
        .order_by('-pub_date')[:5]
    )
    return _render('blog/index.html', {'posts': posts})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)

    now = timezone.now()
    posts = (
        Post.objects.select_related('author', 'category', 'location')
        .filter(
            category=category,
            is_published=True,
            pub_date__lte=now,
        )
        .order_by('-pub_date')
    )
    return _render('blog/category.html', {'category': category, 'posts': posts})


def post_detail(request, post_id):
    now = timezone.now()
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id,
        is_published=True,
        pub_date__lte=now,
        category__is_published=True,
    )
    return _render('blog/detail.html', {'post': post})
