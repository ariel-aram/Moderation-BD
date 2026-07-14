from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("moderation_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModerationConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("guild_id", models.BigIntegerField(unique=True)),
                ("muted_role_id", models.BigIntegerField(blank=True, null=True)),
            ],
        ),
    ]
