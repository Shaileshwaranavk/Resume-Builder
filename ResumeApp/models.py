from django.db import models

from django.contrib.auth.hashers import make_password, check_password

class User_Details(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    password = models.CharField(max_length=128)  # Store hashed password

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    @property
    def is_authenticated(self):
        return True


class Basic_Details(models.Model):
    user = models.OneToOneField('User_Details', on_delete=models.CASCADE, related_name='basic_details', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    linkedin_profile = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255)
    skills = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Experience(models.Model):
    basic_details = models.ForeignKey(Basic_Details, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=100)
    start_date = models.TextField()
    end_date = models.TextField()
    currently_working = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Education(models.Model):
    basic_details = models.ForeignKey(Basic_Details, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    gpa = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    start_date = models.TextField()
    end_date = models.TextField()
    description = models.TextField()

    def __str__(self):
        return f"{self.degree} from {self.institution}"

class Project(models.Model):
    basic_details = models.ForeignKey(Basic_Details, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    description = models.TextField()
    technologies_used = models.JSONField(default=list, blank=True)
    start_date = models.TextField()
    end_date = models.TextField()
    ongoing = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Certification(models.Model):
    basic_details = models.ForeignKey(Basic_Details, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=100)
    issuing_organization = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Achievement(models.Model):
    basic_details = models.ForeignKey(Basic_Details, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class AdditionalSection(models.Model):
    basic_details = models.ForeignKey(Basic_Details, on_delete=models.CASCADE, related_name='additional_sections')
    section_title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return f"{self.section_title} - {self.basic_details}"