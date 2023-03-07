from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):

    name = models.CharField('Тэг',
                            max_length=200,
                            unique=True,)
    color = models.CharField('Цвет',
                             max_length=7,
                             null=True,)
    slug = models.CharField('Слаг тэга',
                            max_length=200,
                            null=True,
                            unique=True,)

    class Meta:
        db_table = 'tag'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):

    name = models.CharField('Ингридиент',
                            max_length=200,)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=40,
                                        help_text='Укажите единицу измерения')

    class Meta:
        db_table = 'ingredient'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}: {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
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
        return f'{self.name}'


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
        verbose_name='Количество',
        default=1,
        validators=(MinValueValidator(1,
                    message='Введите количество больше 0.'),))

    class Meta:
        db_table = 'ingredient_amount_recipe'
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [models.UniqueConstraint(
                       fields=['recipe', 'ingredients', 'amount'],
                       name='unique_recipe_ingredient_amount',)]

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(models.Model):

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Юзер',
                             related_name='favorite')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Понравившийся рецепт',
                               related_name='favorite')

    class Meta:
        db_table = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
                       fields=['user', 'recipe'],
                       name='unique_favorite_amount',)]

class ShoppingCart(models.Model):

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Юзер',
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shopping_cart')

    class Meta:
        db_table = 'shopping_cart'
        verbose_name = 'Список покупок'
        constraints = [models.UniqueConstraint(
                       fields=['user', 'recipe'],
                       name='unique_shoppingcart_amount',)]
