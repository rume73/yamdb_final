from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .validators import year_validator

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='Часть URL адреса группы',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='Часть URL адреса группы',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
    )
    year = models.PositiveSmallIntegerField(
        validators=[year_validator],
        help_text="Используйте формат ввода года выпуска: <YYYY>",
        verbose_name="Год")
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения',
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name='titles',
        blank=True, null=True
    )

    class Meta:
        ordering = ('-year',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField()
    score = models.IntegerField(
        blank=True,
        validators=[
            MinValueValidator(1, message='Слишком низкая оценка'),
            MaxValueValidator(10, message='Слишком высокая оценка')
        ]
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор отзыва'
    )
    pub_date = models.DateTimeField(
        'Дата добавления отзыва', auto_now_add=True, db_index=True, null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField('Комментарий')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор комментария на отзыв'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв'
    )
    pub_date = models.DateTimeField(
        'Дата добавления комментария', auto_now_add=True, db_index=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
