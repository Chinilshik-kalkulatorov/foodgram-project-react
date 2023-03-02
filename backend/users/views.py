from api.permissions import IsAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import TokenSerializer, UserSerializer, UserSingUpSerializer
from .utils import generate_confirmation_code


@api_view(['POST'])
def user_sing_up(request):
    username = request.data.get('username')
    if not User.objects.filter(username=username).exists():
        serializer = UserSingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if username != "me":
            serializer.save()
            generate_confirmation_code(username)
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )
        return Response(
            "Вы не можете создать пользователя с таким username.",
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = get_object_or_404(User, username=username)
    serializer = UserSingUpSerializer(
        user, data=request.data, partial=True
    )
    serializer.is_valid(raise_exception=True)
    if serializer.validated_data['email'] == user.email:
        serializer.save()
        generate_confirmation_code(username)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )
    return Response(
        'Пользователя с указанной почтой не существует',
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def get_user_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data.get("confirmation_code")
    username = serializer.validated_data['username']
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return Response(
            'Пользователь не найден', status=status.HTTP_404_NOT_FOUND
        )
    if user.confirmation_code == confirmation_code:
        refresh = RefreshToken.for_user(user)
        token_data = {'token': str(refresh.access_token)}
        return Response(
            token_data, status=status.HTTP_200_OK
        )
    return Response(
        'Код подтверждения неверный', status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    search_fields = ('=username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
