from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.http import FileResponse
from django.conf import settings

from .models import User_Details, Basic_Details
from .serializers import RegisterSerializer, LoginSerializer, BasicDetailsSerializer
from ResumeApp.resume_generator import fill_template_with_data

import jwt
from datetime import datetime, timedelta


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')

        if not all([email, first_name, last_name, password]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User_Details.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User_Details(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User_Details.objects.get(email=email)
        except User_Details.DoesNotExist:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=60),
            'iat': datetime.utcnow(),
            'email': user.email
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'message': 'Login successful.',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'access': token
        }, status=status.HTTP_200_OK)


class ResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if hasattr(request.user, 'basic_details'):
                return Response({'error': 'Resume already exists. Use PATCH to update.'}, status=status.HTTP_400_BAD_REQUEST)
        except Basic_Details.DoesNotExist:
            pass

        serializer = BasicDetailsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            return Response({"id": instance.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            resume = request.user.basic_details
        except Basic_Details.DoesNotExist:
            return Response({'error': 'Resume not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BasicDetailsSerializer(resume)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        try:
            resume = request.user.basic_details
        except Basic_Details.DoesNotExist:
            return Response({'error': 'Resume not found. Use POST to create.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BasicDetailsSerializer(resume, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResumeDocxDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("\n-----------------------------")
        print("Download view HIT")
        print("Request.user:", request.user)
        print("Request.user ID:", getattr(request.user, "id", None))
        print("User authenticated?", getattr(request.user, "is_authenticated", False))
        print("-----------------------------")

        try:
            resume = request.user.basic_details
            print("Basic_Details found:", resume)
        except Basic_Details.DoesNotExist:
            print("❌ Basic_Details DOES NOT EXIST for user.")
            return Response({'error': 'Resume not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BasicDetailsSerializer(resume)
        docx_buffer = fill_template_with_data(serializer.data)

        print("✅ DOCX generated. Returning file.")
        return FileResponse(
            docx_buffer,
            as_attachment=True,
            filename='resume.docx',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
