from .models import Project


class ProjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            project_id = request.session.get('active_project_id')
            project = None

            if project_id:
                project = Project.objects.filter(
                    pk=project_id, owner=request.user
                ).first()

            if project is None:
                project = Project.objects.filter(owner=request.user).first()
                if project is None:
                    project = Project.objects.create(
                        owner=request.user,
                        name=request.user.company_name or 'My Project',
                    )
                request.session['active_project_id'] = project.pk

            request.project = project
        else:
            request.project = None

        return self.get_response(request)
