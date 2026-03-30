from .models import Project


def project_context(request):
    if not hasattr(request, 'project') or request.project is None:
        return {}
    return {
        'current_project': request.project,
        'user_projects': Project.objects.filter(owner=request.user),
    }
