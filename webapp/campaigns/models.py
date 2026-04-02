from django.conf import settings
from django.db import models


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaign_conversations',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='campaign_conversations',
    )
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'Conversation {self.pk}'


class Message(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'
        STEP = 'step', 'Step'

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_role_display()} message in {self.conversation}'


class CampaignDraft(models.Model):
    class Status(models.TextChoices):
        PLANNING = 'planning', 'Planning'
        DRAFTING = 'drafting', 'Drafting'
        REVIEW = 'review', 'Review'
        APPROVED = 'approved', 'Approved'
        CREATED = 'created', 'Created'

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='drafts',
    )
    title = models.CharField(max_length=255, blank=True)
    plan = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
    )
    posts = models.ManyToManyField(
        'social_media.SocialMediaPost',
        blank=True,
        related_name='campaign_drafts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'Draft {self.pk}'
