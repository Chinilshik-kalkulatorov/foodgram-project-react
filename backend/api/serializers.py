from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CharField, EmailField,
                                        IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueValidator

from users.models import Subscription, User
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from .fields import RecipeSubscribeUserField


class CreateUserSerializer(UserCreateSerializer):

    username = CharField(validators=[UniqueValidator(
        queryset=User.objects.all())])
    email = EmailField(validators=[UniqueValidator(
        queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'password',)
        extra_kwargs = {'password': {'write_only': True}}


class UsersSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientCreateSerializer(ModelSerializer):

    id = IntegerField(read_only=False)

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')

class ReadIngredientsInRecipeSerializer(ModelSerializer):

    id = ReadOnlyField(source='ingredients.id')
    name = ReadOnlyField(source='ingredients.name')
    measurement_unit = ReadOnlyField(source='ingredients.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name',
                  'measurement_unit',
                  'amount',)

    def to_representation(self, instance):
        representation = IngredientCreateSerializer(instance.ingredients).data
        representation['name'] = instance.ingredients.name
        representation['measurement_unit'] = instance.ingredients.measurement_unit
        representation['amount'] = instance.amount
        return representation

class RecipeSerializer(ModelSerializer):

    author = UsersSerializer(read_only=True)
    ingredients = ReadIngredientsInRecipeSerializer(source='amount_ingredient', many=True)
    tags = TagSerializer(many=True)
    is_in_shopping_cart = SerializerMethodField()
    is_favorited = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ReadIngredientsInRecipeSerializer.objects.create(recipe=recipe,
                                                             **ingredient_data)
        recipe.save()
        return recipe

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return Favorite.objects.filter(
                user=user, recipe=obj).exists()
        return False


class RecipeCreateSerializer(ModelSerializer):

    ingredients = IngredientCreateSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    image = Base64ImageField()
    name = CharField(max_length=200)
    cooking_time = IntegerField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags',
                  'image', 'name', 'text',
                  'cooking_time', 'author')

    # @staticmethod
    # def create_ingredients(ingredients, recipe):
    #     print("Create ingredients: ", ingredients)
    #     for ingredient in ingredients:
    #         amount = ingredient['amount']
    #         if AmountIngredient.objects.filter(
    #                 recipe=recipe,
    #                 ingredients=get_object_or_404(
    #                     Ingredient, id=ingredient['id'])).exists():
    #             amount += F('amount')
    #         AmountIngredient.objects.update_or_create(
    #             recipe=recipe,
    #             ingredients=get_object_or_404(
    #                 Ingredient, id=ingredient['id']),
    #             defaults={'amount': amount})

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image,
                                       **validated_data)
        # self.create_ingredients(ingredients_data, recipe)

        recipe.tags.set(tags_data)
        ingredients_list = [
            AmountIngredient(
                recipe=recipe,
                ingredients=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ]
        AmountIngredient.objects.bulk_create(ingredients_list)

        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        AmountIngredient.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        data = RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}).data
        return data

    def validate_ingredients(self, data):
        ingredient_data = self.initial_data.get('ingredients')
        if ingredient_data:
            checked_ingredients = set()
            for ingredient in ingredient_data:
                ingredient_obj = get_object_or_404(
                    Ingredient, id=ingredient['id']
                )
                if ingredient_obj in checked_ingredients:
                    raise ValidationError('дубликат ингредиента')
                checked_ingredients.add(ingredient_obj)
        return ingredient_data

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError('Время приготовления должно быть больше 0')
        return cooking_time

    # def validate_ingredients(self, ingredients):
    #     print("Ingredients in validation: ", ingredients)
    #     raise NotImplementedError
    #     ingredients_ids = [ingredient.get('id') for ingredient in ingredients]

    #     for ingredient in ingredients:
    #         if int(ingredient['amount']) <= 0:
    #             raise ValidationError(
    #                 'Количество ингредиентов должно быть больше 0')

    #     if len(ingredients_ids) != len(set(ingredients_ids)):
    #         raise ValidationError('Список ингредиентов содержит дубликаты')

    #     return ingredients


class RecipeForSubscriptionersSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionSerializer(ModelSerializer):
    """Сериализатор для подписок."""
    recipes = RecipeSubscribeUserField()
    recipes_count = SerializerMethodField(read_only=True)
    id = ReadOnlyField(source='author.id')
    email = ReadOnlyField(source='author.email')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj.user,
                                           author=obj.author).exists()
