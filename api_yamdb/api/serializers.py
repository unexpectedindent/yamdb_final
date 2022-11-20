import datetime as dt
import re

from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class AdminSerializer(ModelSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICE, default='user')

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role',
        )
        required_fields = ('username', 'email',)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role',
        )
        required_fields = ('username', 'email',)
        read_only_fields = ('role',)


class SignupSerializer(ModelSerializer):
    email = serializers.EmailField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator()
        ),
        required=True
    )
    username = serializers.CharField(
        validators=(UniqueValidator(queryset=User.objects.all()),),
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, value):
        if value == 'me' or re.match(r'^[\w.@+-]+$', value) is None:
            raise ValidationError('Недопустимое имя пользователя')
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category',
            'rating',
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year = dt.date.today().year
        if not (0 < value <= year):
            raise serializers.ValidationError('Проверьте год выпуска')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        if Review.objects.filter(
            author=self.context['request'].user,
            title__id=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв об этом произведении'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
