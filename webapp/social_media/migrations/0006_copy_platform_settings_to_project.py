from django.db import migrations


def copy_platform_settings(apps, schema_editor):
    SocialMediaSettings = apps.get_model('social_media', 'SocialMediaSettings')
    Project = apps.get_model('projects', 'Project')

    for sms in SocialMediaSettings.objects.select_related('project').all():
        try:
            project = sms.project
            project.enable_linkedin = sms.enable_linkedin
            project.enable_x = sms.enable_x
            project.enable_facebook = sms.enable_facebook
            project.enable_instagram = sms.enable_instagram
            project.save(update_fields=[
                'enable_linkedin', 'enable_x', 'enable_facebook', 'enable_instagram',
            ])
        except Exception:
            pass


def reverse_copy(apps, schema_editor):
    pass  # No need to reverse data migration


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0005_alter_socialmediapost_project_and_more'),
        ('projects', '0003_project_platform_settings'),
    ]

    operations = [
        migrations.RunPython(copy_platform_settings, reverse_copy),
    ]
