from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название тэга', unique=True, max_length=20)
    slug = models.SlugField('Адрес тэга', unique=True, max_length=20)
    color = models.CharField(
        'Цвет(HEX)', unique=True, max_length=7, default='#49B64E'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Еденицы измерения', max_length=20)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Название',
                            max_length=200,)
    image = models.ImageField('Картинка',)
    text = models.TextField('Описание',)
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Список ингредиентов',
                                         through='AmountIngredient',
                                         related_name='recipes',)
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Тег',)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)')
    validators = (MinValueValidator(1,
                  message='Укажите время приготовления блюда больше 0'),)

    class Meta:
        db_table = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} ({self.author})'


class AmountIngredient(models.Model):

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='amount_ingredient',
                               )
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.CASCADE,
                                    verbose_name='Ингредиент',
                                    related_name='amount_ingredient',
                                    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=(
            MinValueValidator(1, message='Количество не может быть меньше 1'),
        ),
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique ingredient recipe'
            ),
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uniq_favorite_user_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uniq_cart_user_recipe'
            )
        ]
