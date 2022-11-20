from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import (CreateOrIsAuthorOrReadOnly, IsAdmin,
                          IsAdminOrReadOnly, IsGuest)
from .serializers import (AdminSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SignupSerializer, TitleReadSerializer,
                          TitleWriteSerializer, TokenSerializer,
                          UserSerializer)


class AbstractViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
):
    pass


@api_view(['POST'])
@permission_classes([IsGuest])
def signup(request):
    if request.user.is_authenticated:
        raise ValidationError('Вы уже зарегестрировны.')
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Welcome to YaMDB!',
        from_email='YaMDB@project.com',
        recipient_list=(user.email,),
        message=confirmation_code
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    if not default_token_generator.check_token(
        user,
        serializer.validated_data['confirmation_code']
    ):
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    token = RefreshToken.for_user(user)
    return Response(
        {'token': str(token.access_token)},
        status=status.HTTP_200_OK
    )


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAuthenticated, IsAdmin,)

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = AdminSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if user.is_admin:
            serializer = AdminSerializer(
                user, data=request.data, partial=True
            )
        else:
            serializer = UserSerializer(
                user, data=request.data, partial=True
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(AbstractViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(AbstractViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    serializer_class = TitleReadSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = TitleFilter
    ordering = ('id',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve',):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    permission_classes = (CreateOrIsAuthorOrReadOnly,)
    serializer_class = ReviewSerializer

    def check_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.check_title())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.check_title())


class CommentViewSet(ModelViewSet):
    permission_classes = (CreateOrIsAuthorOrReadOnly,)
    serializer_class = CommentSerializer

    def check_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.check_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.check_review()
        )
