from django.contrib.auth import authenticate

from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets

import os
import re

from .services import transcribe_audio, detect_intent_and_subintent, load_data, get_response, train_models
from .serializers import UserSerializer, EmployeeSerializer, RequestSerializer, IntentSerializer, SubintentSerializer, PhraseSerializer, EmailRecipientSerializer
from .models import User, Employee, Request, Intent, Subintent, Phrase, EmailRecipient
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail


class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission to only allow admins full access,
    while non-admin users can only access their own data.
    """
    def has_permission(self, request, view):
        # Allow access if the user is authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin users have access to all objects
        if request.user.is_admin:
            return True
        # Non-admin users can only access their own data
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class LoginView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = authenticate(email=request.data['email'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class AudioIntentViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({'error': 'Аудиофайл не предоставлен.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Извлекаем ID пользователя из имени файла
        match = re.match(r"^(\d+)_", audio_file.name)
        if match:
            telegram_id = match.group(1)
        else:
            return Response({'error': 'Неверный формат имени файла.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем пользователя с полученным Telegram ID
        try:
            user = User.objects.get(id=telegram_id)
        except ObjectDoesNotExist:
            return Response({'error': 'Пользователь с таким ID не найден.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Сохраняем аудиофайл на диск
        save_path = os.path.join('temp', audio_file.name)
        with open(save_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # Транскрибируем аудиофайл
        transcribed_text = transcribe_audio(save_path)

        # Сохраняем запрос в базе данных
        request_instance = Request(user_id=user, request=transcribed_text, ready=False)
        request_instance.save()

        # Обучаем модели и определяем намерение
        intent_data, subintent_data = load_data()
        models = train_models(intent_data, subintent_data)
        intent_name, subintent_name = detect_intent_and_subintent(transcribed_text, models)
        
        # Получаем ответ
        response_text = get_response(intent_name, subintent_name)

        # Отправляем письмо с информацией
        self.send_email(user, transcribed_text, intent_name, subintent_name)

        return Response({
            'transcribed_text': transcribed_text, 
            'intent': intent_name, 
            'subintent': subintent_name, 
            'response': response_text
        })

    def send_email(self, user, transcribed_text, intent_name, subintent_name):
        subject = "Новое намерение распознано"
        message = (
            f"Распознанный текст: {transcribed_text}\n"
            f"Итоговое намерение: {intent_name}\n"
            f"Поднамерение: {subintent_name}\n"
            f"Пользовательская информация:\n"
            f"Telegram ID: {user.id}\n"
            f"Телефон: {user.phone}\n"
            f"Номер договора: {user.agreement}\n"
            f"Адрес: {user.address}\n"
        )
        email_list = EmailRecipient.objects.values_list('email', flat=True)

        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=email_list,
            fail_silently=False,
        )


# class TextIntentViewSet(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         text_message = request.data.get('text')
#         if not text_message:
#             return Response({'error': 'Текстовое сообщение не предоставлено.'}, status=status.HTTP_400_BAD_REQUEST)

#         telegram_id = request.data.get('id')
#         try:
#             user = User.objects.get(id=telegram_id)
#         except ObjectDoesNotExist:
#             return Response({'error': 'Пользователь с таким ID не найден.'}, status=status.HTTP_404_NOT_FOUND)

#         # Сохраняем запрос в базе данных
#         request_instance = Request(user_id=user, request=text_message, ready=False)
#         request_instance.save()

#         # Обучаем модели и определяем намерение
#         intent_data, subintent_data = load_data()
#         models = train_models(intent_data, subintent_data)
#         intent_name, subintent_name = detect_intent_and_subintent(text_message, models)
        
#         # Получаем ответ
#         response_text = get_response(intent_name, subintent_name)

#         # Отправляем письмо с информацией
#         self.send_email(user, text_message, intent_name, subintent_name)

#         return Response({
#             'transcribed_text': text_message, 
#             'intent': intent_name, 
#             'subintent': subintent_name, 
#             'response': response_text
#         })

#     def send_email(self, user, transcribed_text, intent_name, subintent_name):
#         subject = "Новое намерение распознано"
#         message = (
#             f"Распознанный текст: {transcribed_text}\n"
#             f"Итоговое намерение: {intent_name}\n"
#             f"Поднамерение: {subintent_name}\n"
#             f"Пользовательская информация:\n"
#             f"Telegram ID: {user.id}\n"
#             f"Телефон: {user.phone}\n"
#             f"Номер договора: {user.agreement}\n"
#             f"Адрес: {user.address}\n"
#         )
#         email_list = EmailRecipient.objects.values_list('email', flat=True)

#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=None,
#             recipient_list=email_list,
#             fail_silently=False,
#         )


class TextIntentViewSet(APIView): 
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text_message = request.data.get('text')
        if not text_message:
            return Response({'error': 'Текстовое сообщение не предоставлено.'}, status=status.HTTP_400_BAD_REQUEST)

        telegram_id = request.data.get('id')
        try:
            user = User.objects.get(id=telegram_id)
        except ObjectDoesNotExist:
            return Response({'error': 'Пользователь с таким ID не найден.'}, status=status.HTTP_404_NOT_FOUND)

        # Сохраняем запрос в базе данных
        request_instance = Request(user_id=user, request=text_message, ready=False)
        request_instance.save()

        # Обучаем модели и определяем намерение
        intent_data, subintent_data = load_data()
        models = train_models(intent_data, subintent_data)
        intent_name, subintent_name = detect_intent_and_subintent(text_message, models)
        
        # Получаем ответ
        response_text = get_response(intent_name, subintent_name)

        # Отправляем письмо с информацией
        self.send_email(user, text_message, intent_name, subintent_name)

        return Response({
            'transcribed_text': text_message, 
            'intent': intent_name, 
            'subintent': subintent_name, 
            'response': response_text
        })

    def send_email(self, user, transcribed_text, intent_name, subintent_name):
        subject = "Новое намерение распознано"
        message = (
            f"Распознанный текст: {transcribed_text}\n"
            f"Итоговое намерение: {intent_name}\n"
            f"Поднамерение: {subintent_name}\n"
            f"Пользовательская информация:\n"
            f"Telegram ID: {user.id}\n"
            f"Телефон: {user.phone}\n"
            f"Номер договора: {user.agreement}\n"
            f"Адрес: {user.address}\n"
        )
        email_list = EmailRecipient.objects.values_list('email', flat=True)

        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=email_list,
            fail_silently=False,
        )



class RegistrationView(generics.CreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class IntentViewSet(viewsets.ModelViewSet):
    queryset = Intent.objects.all()
    serializer_class = IntentSerializer
    permission_classes = [permissions.IsAuthenticated]


# class SubintentViewSet(viewsets.ModelViewSet):
#     queryset = Subintent.objects.all()
#     serializer_class = SubintentSerializer
#     permission_classes = [permissions.IsAuthenticated]

class SubintentViewSet(viewsets.ModelViewSet):
    serializer_class = SubintentSerializer

    def get_queryset(self):
        # Получаем параметр intent_id из запроса
        intent_id = self.request.query_params.get('intent_id')
        if intent_id:
            # Если intent_id передан, фильтруем по нему
            return Subintent.objects.filter(intent_id=intent_id)
        # Если intent_id не передан, возвращаем пустой queryset или весь набор по умолчанию
        return Subintent.objects.none()  # либо .all(), если нужны все поднамерения
    
    # Если нужен кастомный ответ, можно переопределить list
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "No subintents found for the specified intent_id."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PhraseViewSet(viewsets.ModelViewSet):
    queryset = Phrase.objects.all()
    serializer_class = PhraseSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()  # Добавляем queryset по умолчанию
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrSelf]

    def get_queryset(self):
        # Делаем выборку в зависимости от роли пользователя
        if self.request.user.is_admin:
            return Employee.objects.all()
        return Employee.objects.filter(id=self.request.user.id)


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmailRecipientViewSet(viewsets.ModelViewSet):
    queryset = EmailRecipient.objects.all()
    serializer_class = EmailRecipientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Переопределяем метод list, чтобы вернуть список email-адресов
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Необходимо указать электронную почту.'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка на валидность электронной почты
        try:
            # Удаляем все существующие email-адреса
            EmailRecipient.objects.all().delete()

            # Создаем новый email-адрес
            email_recipient = EmailRecipient.objects.create(email=email)
            return Response({'success': f'Электронная почта {email} успешно добавлена.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class SendEmailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        email_list = EmailRecipient.objects.values_list('email', flat=True)

        if not subject or not message:
            return Response({'error': 'Необходимо указать тему и сообщение'}, status=status.HTTP_400_BAD_REQUEST)

        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # По умолчанию будет использовать DEFAULT_FROM_EMAIL
            recipient_list=email_list,
            fail_silently=False,
        )

        return Response({'success': 'Письмо успешно отправлено на все адреса.'}, status=status.HTTP_200_OK)