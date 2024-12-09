from django.core.paginator import Paginator
from django.shortcuts import render
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404

PER_PAGE = 9


def index(request):
    posts = Post.objects.get_published()  # type: ignore

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': 'Home - ',
        }
    )


def created_by(request, author_pk):
    user = User.objects.filter(pk=author_pk).first()

    if user is None:
        raise Http404()

    posts = Post.objects.get_published().filter(  # type: ignore
        created_by__pk=author_pk)

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    user_full_name = user.username
    if (user.first_name):
        user_full_name = f'{user.first_name} {user.last_name}'

    page_title = 'Posts de ' + user_full_name + ' - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': page_title,
        }
    )


def category(request, slug):
    posts = Post.objects.get_published().filter(  # type: ignore
        category__slug=slug)

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if len(page_obj) == 0:
        raise Http404()

    page_title = f'{page_obj[0].category.name} - Categoria - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': page_title,
        }
    )


def page(request, slug):
    page_obj = Page\
        .objects\
        .filter(is_published=True)\
        .filter(slug=slug)\
        .first()  # type: ignore

    if page_obj is None:
        raise Http404()

    page_title = f'{page_obj.title} - Page - '

    return render(
        request,
        'blog/pages/page.html',
        {
            'page': page_obj,
            'page_title': page_title,
        }
    )


def post(request, slug):
    post_obj = Post.objects.get_published().filter(slug=slug).first()  # type: ignore

    if post_obj is None:
        raise Http404()

    page_title = f'{post_obj.title} - Post - '

    return render(
        request,
        'blog/pages/post.html',
        {
            'post': post_obj,
            'page_title': page_title,
        }
    )


def tag(request, slug):
    posts = Post.objects.get_published().filter(  # type: ignore
        tags__slug=slug)

    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if len(page_obj) == 0:
        raise Http404()

    page_title = f'{page_obj[0].tags.first().name} - Tag - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'page_title': page_title,
        }
    )


def search(request):
    search_value = request.GET.get('search', '').strip()

    posts = (Post
             .objects
             .get_published()  # type: ignore
             .filter(
                 # Título contém o search_value OU
                 # Excerto contém o search_value OU
                 # Conteúdo contém o search_value
                 Q(title__icontains=search_value) |
                 Q(excerpt__icontains=search_value) |
                 Q(content__icontains=search_value)
             )[:PER_PAGE]
             )

    page_title = f'{search_value[:30]} - Search - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': posts,
            'search_value': search_value,
            'page_title': page_title,
        }
    )