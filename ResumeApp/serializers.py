from rest_framework import serializers
from .models import User_Details
from django.contrib.auth.hashers import make_password, check_password

from .models import (
    Basic_Details, Experience, Education,
    Project, Certification, Achievement, AdditionalSection
)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User_Details
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'password']

    def create(self, validated_data):
        user = User_Details(**validated_data)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        exclude = ['basic_details']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['basic_details']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['basic_details']

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        exclude = ['basic_details']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        exclude = ['basic_details']

class AdditionalSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalSection
        exclude = ['basic_details']

class BasicDetailsSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    additional_sections = AdditionalSectionSerializer(many=True, required=False)

    class Meta:
        model = Basic_Details
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'linkedin_profile', 'github', 'location', 'summary',
            'skills', 'experiences', 'educations', 'projects',
            'certifications', 'achievements', 'additional_sections'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # ✅ FIX: Remove 'user' if frontend mistakenly sends it
        validated_data.pop('user', None)  # <- THIS LINE IS THE FIX!

        # Extract nested data
        experiences_data = validated_data.pop('experiences', [])
        educations_data = validated_data.pop('educations', [])
        projects_data = validated_data.pop('projects', [])
        certifications_data = validated_data.pop('certifications', [])
        achievements_data = validated_data.pop('achievements', [])
        additional_sections_data = validated_data.pop('additional_sections', [])

        # Create main Basic_Details with the authenticated user
        basic_details = Basic_Details.objects.create(user=user, **validated_data)

        # Create nested related objects
        for item in experiences_data:
            Experience.objects.create(basic_details=basic_details, **item)
        for item in educations_data:
            Education.objects.create(basic_details=basic_details, **item)
        for item in projects_data:
            Project.objects.create(basic_details=basic_details, **item)
        for item in certifications_data:
            Certification.objects.create(basic_details=basic_details, **item)
        for item in achievements_data:
            Achievement.objects.create(basic_details=basic_details, **item)
        for item in additional_sections_data:
            AdditionalSection.objects.create(basic_details=basic_details, **item)

        return basic_details

    def update(self, instance, validated_data):
        # Update basic fields
        for attr, value in validated_data.items():
            if attr in ['experiences', 'educations', 'projects', 'certifications', 'achievements', 'additional_sections']:
                continue  # Skip nested fields here
            setattr(instance, attr, value)
        instance.save()

        # Optional: Add nested update logic if needed

        return instance
