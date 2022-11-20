from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

AMOUNT_LETTERS = 15

LIMIT_VALUE = 10


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )

    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='slug-код категории'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Катагория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название жанра')

    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='slug-код жанра'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Название произведения'
    )

    year = models.PositiveSmallIntegerField(verbose_name='Год выпуска')

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )

    genre = models.ManyToManyField(
        Genre,
        blank=True,
        null=True,
        through='GenreTitle',
        verbose_name='Жанры'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категории'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:AMOUNT_LETTERS]


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Жанры'
    )

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Название произведения'
    )

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )

    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг произведения',
        blank=True, null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(
                10, f'The value should be lesser than {LIMIT_VALUE}.'
            )
        ],
        default=0
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        db_index=True,
        auto_now_add=True
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review_for_title'
            )
        ]

    def __str__(self):
        return self.text[AMOUNT_LETTERS]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв на произведение'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментатор'
    )

    text = models.TextField(verbose_name='Текст комментария')

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        db_index=True,
        auto_now_add=True
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.author}/{self.text[:AMOUNT_LETTERS]}'
