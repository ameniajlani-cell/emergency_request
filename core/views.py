from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.conf import settings

from .forms import (
    AssignmentForm,
    EmergencyRequestCreateForm,
    EmergencyTypeForm,
    EmergencyRequestUpdateForm,
    RequesterForm,
    RequesterIntakeForm,
    ResponseTeamForm,
)
from .models import (
    Assignment,
    EmergencyRequest,
    EmergencyType,
    Requester,
    ResponseTeam,
)


REQUESTS_PER_PAGE = 5


@login_required
def home(request):
    title_query = request.GET.get('title', '').strip()
    type_query = request.GET.get('type', '').strip()
    status_query = request.GET.get('status', '').strip()
    location_query = request.GET.get('location', '').strip()
    requester_query = request.GET.get('requester', '').strip()
    emergency_types = EmergencyType.objects.all()
    valid_type_ids = {str(type_id) for type_id in emergency_types.values_list('id', flat=True)}
    valid_statuses = {value for value, label in EmergencyRequest.STATUS_CHOICES}

    if type_query not in valid_type_ids:
        type_query = ''

    if status_query not in valid_statuses:
        status_query = ''

    requests = EmergencyRequest.objects.select_related('requester', 'emergency_type')
    if title_query:
        requests = requests.filter(title__icontains=title_query)

    if type_query:
        requests = requests.filter(emergency_type_id=type_query)

    if status_query:
        requests = requests.filter(status=status_query)

    if location_query:
        requests = requests.filter(
            Q(location__icontains=location_query) |
            Q(requester__location__icontains=location_query)
        )

    if requester_query:
        requests = requests.filter(requester__name__icontains=requester_query)

    status_totals = {
        item['status']: item['total']
        for item in requests.values('status').annotate(total=Count('id'))
    }
    stats = {
        'total': requests.count(),
        'pending': status_totals.get('pending', 0),
        'in_progress': status_totals.get('in_progress', 0),
        'resolved': status_totals.get('resolved', 0),
    }
    requests = requests.order_by('-created_at')
    paginator = Paginator(requests, REQUESTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'home.html', {
        'requests': page_obj.object_list,
        'stats': stats,
        'filters': {
            'title': title_query,
            'type': type_query,
            'status': status_query,
            'location': location_query,
            'requester': requester_query,
        },
        'emergency_types': emergency_types,
        'status_choices': EmergencyRequest.STATUS_CHOICES,
        'has_filters': any([title_query, type_query, status_query, location_query, requester_query]),
        'page_obj': page_obj,
        'pagination_query': query_params.urlencode(),
    })


@login_required
def create_request(request):
    if request.method == 'POST':
        requester_form = RequesterIntakeForm(request.POST, prefix='requester')
        request_form = EmergencyRequestCreateForm(request.POST, prefix='request')
        requester_valid = requester_form.is_valid()
        request_valid = request_form.is_valid()

        if requester_valid and request_valid:
            requester, _ = Requester.objects.get_or_create(
                name=requester_form.cleaned_data['name'],
                phone=requester_form.cleaned_data['phone'],
                location=requester_form.cleaned_data['location'],
            )
            # Update requester location coordinates
            if requester_form.cleaned_data.get('latitude'):
                requester.latitude = requester_form.cleaned_data['latitude']
                requester.longitude = requester_form.cleaned_data['longitude']
                requester.save()

            emergency_request = request_form.save(commit=False)
            emergency_request.requester = requester
            emergency_request.save()

            # Auto-assign teams based on emergency type
            assigned_teams = emergency_request.emergency_type.get_assigned_teams()
            for team in assigned_teams:
                Assignment.objects.get_or_create(
                    emergency_request=emergency_request,
                    response_team=team,
                )

            messages.success(request, 'Emergency request created successfully.')
            return redirect('home')
    else:
        requester_form = RequesterIntakeForm(prefix='requester')
        request_form = EmergencyRequestCreateForm(prefix='request')

    return render(request, 'create_request.html', {
        'requester_form': requester_form,
        'request_form': request_form,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })


@login_required
def update_request(request, id):
    req = get_object_or_404(EmergencyRequest, id=id)

    if request.method == 'POST':
        form = EmergencyRequestUpdateForm(request.POST, instance=req)

        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency request updated successfully.')
            return redirect('home')
    else:
        form = EmergencyRequestUpdateForm(instance=req)

    return render(request, 'update_request.html', {
        'form': form,
        'req': req,
    })


@login_required
def delete_request(request, id):
    req = get_object_or_404(EmergencyRequest, id=id)

    return delete_object(
        request=request,
        obj=req,
        object_name='Emergency Request',
        success_url_name='home',
        cancel_url_name='home',
    )


def save_model_form(request, form_class, title, kicker, submit_label, success_url_name, instance=None):
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            messages.success(request, f'{title} saved successfully.')
            return redirect(success_url_name)
    else:
        form = form_class(instance=instance)

    return render(request, 'crud_form.html', {
        'form': form,
        'title': title,
        'kicker': kicker,
        'submit_label': submit_label,
        'cancel_url': reverse(success_url_name),
    })


def delete_object(request, obj, object_name, success_url_name, cancel_url_name):
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, f'{object_name} deleted successfully.')
            return redirect(success_url_name)
        except ProtectedError:
            messages.error(request, f'{object_name} cannot be deleted because related records still use it.')
            return redirect(cancel_url_name)

    return render(request, 'confirm_delete.html', {
        'object': obj,
        'object_name': object_name,
        'cancel_url': reverse(cancel_url_name),
    })


@login_required
def requester_list(request):
    requesters = Requester.objects.annotate(request_count=Count('emergency_requests')).order_by('name')

    return render(request, 'requester_list.html', {
        'requesters': requesters,
    })


@login_required
def requester_create(request):
    return save_model_form(
        request=request,
        form_class=RequesterForm,
        title='Requester',
        kicker='Create',
        submit_label='Create Requester',
        success_url_name='requester_list',
    )


@login_required
def requester_update(request, id):
    requester = get_object_or_404(Requester, id=id)

    return save_model_form(
        request=request,
        form_class=RequesterForm,
        title='Requester',
        kicker='Update',
        submit_label='Save Requester',
        success_url_name='requester_list',
        instance=requester,
    )


@login_required
def requester_delete(request, id):
    requester = get_object_or_404(Requester, id=id)

    return delete_object(
        request=request,
        obj=requester,
        object_name='Requester',
        success_url_name='requester_list',
        cancel_url_name='requester_list',
    )


@login_required
def emergency_type_list(request):
    emergency_types = EmergencyType.objects.annotate(request_count=Count('emergency_requests')).order_by('name')

    return render(request, 'emergency_type_list.html', {
        'emergency_types': emergency_types,
    })


@login_required
def emergency_type_create(request):
    return save_model_form(
        request=request,
        form_class=EmergencyTypeForm,
        title='Emergency Type',
        kicker='Create',
        submit_label='Create Type',
        success_url_name='emergency_type_list',
    )


@login_required
def emergency_type_update(request, id):
    emergency_type = get_object_or_404(EmergencyType, id=id)

    return save_model_form(
        request=request,
        form_class=EmergencyTypeForm,
        title='Emergency Type',
        kicker='Update',
        submit_label='Save Type',
        success_url_name='emergency_type_list',
        instance=emergency_type,
    )


@login_required
def emergency_type_delete(request, id):
    emergency_type = get_object_or_404(EmergencyType, id=id)

    return delete_object(
        request=request,
        obj=emergency_type,
        object_name='Emergency Type',
        success_url_name='emergency_type_list',
        cancel_url_name='emergency_type_list',
    )


@login_required
def response_team_list(request):
    response_teams = ResponseTeam.objects.annotate(assignment_count=Count('assignments')).order_by('name')

    return render(request, 'response_team_list.html', {
        'response_teams': response_teams,
    })


@login_required
def response_team_create(request):
    return save_model_form(
        request=request,
        form_class=ResponseTeamForm,
        title='Response Team',
        kicker='Create',
        submit_label='Create Team',
        success_url_name='response_team_list',
    )


@login_required
def response_team_update(request, id):
    response_team = get_object_or_404(ResponseTeam, id=id)

    return save_model_form(
        request=request,
        form_class=ResponseTeamForm,
        title='Response Team',
        kicker='Update',
        submit_label='Save Team',
        success_url_name='response_team_list',
        instance=response_team,
    )


@login_required
def response_team_delete(request, id):
    response_team = get_object_or_404(ResponseTeam, id=id)

    return delete_object(
        request=request,
        obj=response_team,
        object_name='Response Team',
        success_url_name='response_team_list',
        cancel_url_name='response_team_list',
    )


@login_required
def assignment_list(request):
    assignments = Assignment.objects.select_related(
        'emergency_request',
        'response_team',
    ).order_by('-assigned_at')

    return render(request, 'assignment_list.html', {
        'assignments': assignments,
    })


@login_required
def assignment_create(request):
    return save_model_form(
        request=request,
        form_class=AssignmentForm,
        title='Assignment',
        kicker='Create',
        submit_label='Create Assignment',
        success_url_name='assignment_list',
    )


@login_required
def assignment_update(request, id):
    assignment = get_object_or_404(Assignment, id=id)

    return save_model_form(
        request=request,
        form_class=AssignmentForm,
        title='Assignment',
        kicker='Update',
        submit_label='Save Assignment',
        success_url_name='assignment_list',
        instance=assignment,
    )


@login_required
def assignment_delete(request, id):
    assignment = get_object_or_404(Assignment, id=id)

    return delete_object(
        request=request,
        obj=assignment,
        object_name='Assignment',
        success_url_name='assignment_list',
        cancel_url_name='assignment_list',
    )

