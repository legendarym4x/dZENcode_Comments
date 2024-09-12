from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import RegexValidator, EmailValidator, URLValidator, FileExtensionValidator
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils import timezone

# Validators
alphanumeric_validator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
file_size_limit = 100 * 1024  # 100 KB limit for text files


def validate_file_size(file):
    if file.size > file_size_limit:
        raise ValidationError("File size exceeds the allowed limit of 100 KB.")


class Comment(models.Model):
    user_name = models.CharField(
        max_length=255,
        validators=[alphanumeric_validator],
        verbose_name="User Name"
    )
    email = models.EmailField(
        validators=[EmailValidator(message="Enter a valid email address.")],
        verbose_name="E-mail"
    )
    home_page = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        verbose_name="Home page"
    )
    captcha = models.CharField(
        max_length=6,
        validators=[alphanumeric_validator],
        verbose_name="CAPTCHA"
    )
    text = models.TextField(verbose_name="Comment Text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    # Parent comment for threaded comments
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Parent Comment"
    )

    # Image field for image attachments with size restrictions
    image = models.ImageField(
        upload_to='images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'gif'])],
        verbose_name="Image"
    )

    # File field for text file attachments with size restrictions
    text_file = models.FileField(
        upload_to='text_files/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['txt']),
            validate_file_size
        ],
        verbose_name="Text File"
    )

    class Meta:
        ordering = ['-created_at']  # Default sorting: newest comments first

    def __str__(self):
        return f"Comment by {self.user_name} on {self.created_at}"

    def save(self, *args, **kwargs):
        allowed_tags = []  # Specify the allowed tags if needed
        self.text = strip_tags(self.text)  # Remove all HTML tags
        super().save(*args, **kwargs)
