from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm, ProjectSettingsForm
from .models import Project


@require_POST
@login_required
def switch_project(request):
    project_id = request.POST.get('project_id')
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    request.session['active_project_id'] = project.pk
    response = redirect('home')
    response['X-Up-Accept-Layer'] = 'current'
    return response


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            request.session['active_project_id'] = project.pk
            response = HttpResponse(status=200)
            response['X-Up-Accept-Layer'] = 'null'
            response['X-Up-Events'] = '[{"type": "project:created"}]'
            return response
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=200)
            response['X-Up-Accept-Layer'] = 'null'
            response['X-Up-Events'] = '[{"type": "project:updated"}]'
            return response
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {
        'form': form,
        'is_edit': True,
        'project': project,
    })


@login_required
def project_settings(request):
    project = request.project
    name_form = ProjectForm(instance=project)
    settings_form = ProjectSettingsForm(instance=project)

    if request.method == 'POST':
        if 'save_name' in request.POST:
            name_form = ProjectForm(request.POST, instance=project)
            if name_form.is_valid():
                name_form.save()
                messages.success(request, 'Project name updated.')
                return redirect('projects:project_settings')
        elif 'save_platforms' in request.POST:
            settings_form = ProjectSettingsForm(request.POST, instance=project)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'Platform settings saved.')
                return redirect('projects:project_settings')

    return render(request, 'projects/project_settings.html', {
        'name_form': name_form,
        'settings_form': settings_form,
        'project': project,
    })


@login_required
@require_POST
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.user.projects.count() <= 1:
        messages.error(request, 'You cannot delete your only project.')
        return redirect('projects:project_settings')

    project.delete()

    another = request.user.projects.first()
    if another:
        request.session['active_project_id'] = another.pk
    else:
        request.session.pop('active_project_id', None)

    return redirect('home')
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=200)
            response['X-Up-Accept-Layer'] = 'null'
            response['X-Up-Events'] = '[{"type": "project:updated"}]'
            return response
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {
        'form': form,
        'is_edit': True,
        'project': project,
    })
