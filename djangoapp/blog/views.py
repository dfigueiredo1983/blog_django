from typing import Any
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse

from django.views.generic import ListView

PER_PAGE = 9


class PostListView(ListView):
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()  # type: ignore

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Home - '
        })
        return context


class CreatedByListView(PostListView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Criando um dicionário vazio para o contexto
        self._temp_context: dict[str, Any] = {}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            raise Http404()
            # return redirect('blog:index')

        self._temp_context.update({
            'author_pk': author_pk,
            'user': user,
        })

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self._temp_context['user']

        user_full_name = user.username
        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'

        page_title = 'Posts de ' + user_full_name + ' - '

        context.update({
            'page_title': page_title,
        })

        return context

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        # author_pk = self._temp_context['author_pk']
        author_pk = self._temp_context['user'].pk
        queryset = queryset.filter(created_by__pk=author_pk)

        return queryset


class CategoryListView(PostListView):

    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        queryset = queryset.filter(category__slug=self.kwargs.get('slug'))
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # print('Imprimindo o self: ', self)
        # print('Imprimindo o self: ', dir(self))
        # print('Imprimindo o self: ', self.__dict__)

        page_title = f'{self.object_list[0].category.name} '  # type: ignore
        '- Categoria - '

        context.update({
            'page_title': page_title,
        })

        return context


class TagListView(PostListView):

    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super()\
            .get_queryset()\
            .filter(tags__slug=self.kwargs.get('slug'))

        return queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page_title = (
            f'{self.object_list[0].tags.first().name}'  # type: ignore
            ' - Tag - '
        )
        context.update({
            'page_title': page_title,
        })
        return context


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
