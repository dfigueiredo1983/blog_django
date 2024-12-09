from django.db import models
from utils.rands import slugify_new
from django.contrib.auth.models import User
from utils.rezise_image import resize_image
from django_summernote.models import AbstractAttachment  # type: ignore
from django.urls import reverse


class PostAttachment(AbstractAttachment):
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name

        current_file_name = str(self.file.name)
        super_save = super().save(*args, **kwargs)
        file_chaged = False

        if self.file:
            file_changed = current_file_name != self.file.name

        if file_chaged:
            resize_image(self.file, 900, True, 70)

        return super_save


class Tag(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tag'

    name: models.CharField = models.CharField(max_length=255,)
    slug: models.SlugField = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name, 10)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name: models.CharField = models.CharField(max_length=255,)
    slug: models.SlugField = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name, 10)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Page(models.Model):
    title: models.CharField = models.CharField(max_length=65,)
    slug: models.SlugField = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255,
    )
    is_published: models.BooleanField = models.BooleanField(
        default=False,
        help_text=('Este campo precisa ser marcado para que a publicação '
                   'seja mostrada na página.'),
    )
    content: models.TextField = models.TextField()

    def get_absolute_url(self):
        # return reverse("model_detail", kwargs={"pk": self.pk})
        if not self.is_published:  # post marcado com não publicado
            return reverse('blog:index')
        return reverse('blog:page', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.title, 10)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class PostManager(models.Manager):
    def get_published(self):  # self == objects
        return self\
            .filter(is_published=True)\
            .order_by('-pk')


class Post(models.Model):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    objects = PostManager()

    title: models.CharField = models.CharField(max_length=65,)
    slug: models.SlugField = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255,
    )
    excerpt: models.CharField = models.CharField(max_length=150)
    is_published: models.BooleanField = models.BooleanField(
        default=False,
        help_text=('Este campo precisa ser marcado para que a publicação '
                   'seja mostrada na página.'),
    )
    content: models.TextField = models.TextField()
    cover: models.ImageField = models.ImageField(
        upload_to='posts/%Y/%m/',
        blank=True,
        default='',
    )
    conver_in_post_content: models.BooleanField = models.BooleanField(
        default=True,
        help_text='Se marcado exibirá a capa dentro do post.',
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True,)
    # Acessando o post pelo usuário user.post_set.all() - conflito com o outro ForeignKey
    # Acesso correto com o related_name: user.post_created_by.all
    created_by: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='post_created_by',
    )
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True,)
    # Acessando o post pelo usuário user.post_set.all() - conflito com o outro ForeignKey
    # Acesso correto com o related_name: user.post_updated_by.all
    updated_by: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='post_updated_by',
    )
    # um post tem apenas uma categoria, mas categoria tem vários posts relacionados
    category: models.ForeignKey = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    # uma tag pode existir em vários posts e um post pode ter várias tags
    tags: models.ManyToManyField = models.ManyToManyField(
        Tag,
        blank=True,
        default='',
    )

    def get_absolute_url(self):
        # return reverse("model_detail", kwargs={"pk": self.pk})
        if not self.is_published:  # post marcado com não publicado
            return reverse('blog:index')
        return reverse('blog:post', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.title, 10)
        # return super().save(*args, **kwargs)

        current_cover_name = str(self.cover.name)
        super_save = super().save(*args, **kwargs)
        cover_changed = False

        if self.cover:
            cover_changed = current_cover_name != self.cover.name

        if cover_changed:
            resize_image(self.cover, 800, True, 70)

        return super_save

    def __str__(self) -> str:
        return self.title
