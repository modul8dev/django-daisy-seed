import json

from django.http import (
    HttpResponse,
    JsonResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CampaignDraft, Conversation, Message
from .services import create_campaign_posts, run_agent_stream


def chat_view(request, conversation_id=None):
    """Main chat page. Optionally loads a specific conversation."""
    conversations = Conversation.objects.filter(
        user=request.user,
        project=request.project,
    ).order_by('-updated_at')[:50]

    chat_messages = []
    active_conversation = None

    if conversation_id:
        active_conversation = get_object_or_404(
            Conversation,
            pk=conversation_id,
            user=request.user,
            project=request.project,
        )
        chat_messages = list(active_conversation.messages.all().order_by('created_at'))

    return render(request, 'campaigns/chat.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'chat_messages': chat_messages,
    })


@require_POST
def conversation_create(request):
    """Create a new conversation and redirect to it."""
    conversation = Conversation.objects.create(
        user=request.user,
        project=request.project,
    )
    return redirect('campaigns:chat_conversation', conversation_id=conversation.pk)


@require_POST
def conversation_delete(request, pk):
    """Delete a conversation."""
    conversation = get_object_or_404(
        Conversation,
        pk=pk,
        user=request.user,
        project=request.project,
    )
    conversation.delete()
    return redirect('campaigns:chat')


def conversation_messages(request, conversation_id):
    """Return messages for a conversation as an HTML fragment."""
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        user=request.user,
        project=request.project,
    )
    chat_messages = list(conversation.messages.all().order_by('created_at'))
    return render(request, 'campaigns/partials/messages.html', {
        'chat_messages': chat_messages,
        'active_conversation': conversation,
    })


async def send_message(request, conversation_id):
    """SSE endpoint: send a message and stream agent responses."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    from asgiref.sync import sync_to_async

    conversation = await sync_to_async(get_object_or_404)(
        Conversation,
        pk=conversation_id,
        user=request.user,
        project=request.project,
    )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = body.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    async def event_stream():
        async for sse_chunk in run_agent_stream(conversation, user_message):
            yield sse_chunk

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream',
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@require_POST
def approve_campaign(request, conversation_id, draft_id):
    """Approve a campaign draft and create the actual posts."""
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        user=request.user,
        project=request.project,
    )
    draft = get_object_or_404(
        CampaignDraft,
        pk=draft_id,
        conversation=conversation,
    )

    if draft.status == CampaignDraft.Status.CREATED:
        return JsonResponse({
            'error': 'This campaign has already been created.',
        }, status=400)

    posts = create_campaign_posts(conversation, draft)

    return JsonResponse({
        'message': f'Created {len(posts)} post(s) successfully.',
        'post_ids': [p.id for p in posts],
    })
