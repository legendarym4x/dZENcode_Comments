# Generated by Django 5.1.1 on 2024-09-14 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_comments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user_name",
                    models.CharField(
                        default="user", max_length=255, verbose_name="User Name"
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="E-mail")),
            ],
        ),
        migrations.AlterField(
            model_name="comment",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="E-mail"),
        ),
    ]
