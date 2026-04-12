import html
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from .models import Group, GroupTask, Message, TaskMessage, GroupTaskChecklist
from .forms import GroupForm, GroupTaskForm, EditGroupTaskForm, AddMemberForm

User = get_user_model()


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _is_creator(group, user):
    return group.created_by == user


# ──────────────────────────────────────────────
# Group list / create
# ──────────────────────────────────────────────

@login_required
def group_list(request):
    groups = Group.objects.filter(members=request.user).order_by('-created_at')
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            group.members.add(request.user)
            django_messages.success(request, f"Group '{group.name}' created!")
            return redirect('collaboration:detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'collaboration/groups.html', {'groups': groups, 'form': form})


# ──────────────────────────────────────────────
# Group detail
# ──────────────────────────────────────────────

@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    tasks = GroupTask.objects.filter(group=group).prefetch_related('assigned_to')
    messages_list = Message.objects.filter(group=group).order_by('timestamp').select_related('sender')[:100]
    task_form = GroupTaskForm(group=group)
    add_member_form = AddMemberForm()
    is_creator = _is_creator(group, request.user)

    # Pre-attach chat messages directly onto task objects for easy template access
    tasks = list(tasks)
    for task in tasks:
        can_see_chat = is_creator or task.assigned_to.filter(pk=request.user.pk).exists()
        task.can_see_chat = can_see_chat
        if can_see_chat:
            task.chat_messages = list(
                TaskMessage.objects.filter(task=task).order_by('timestamp').select_related('sender')[:50]
            )
        else:
            task.chat_messages = []

    return render(request, 'collaboration/group_detail.html', {
        'group': group,
        'tasks': tasks,
        'messages': messages_list,
        'task_form': task_form,
        'add_member_form': add_member_form,
        'is_creator': is_creator,
    })



# ──────────────────────────────────────────────
# Add task (creator only)
# ──────────────────────────────────────────────

@login_required
@require_POST
def add_group_task(request, pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    if not _is_creator(group, request.user):
        django_messages.error(request, "Only the project creator can add tasks.")
        return redirect('collaboration:detail', pk=pk)

    form = GroupTaskForm(request.POST, request.FILES, group=group)
    if form.is_valid():
        task = form.save(commit=False)
        task.group = group
        task.save()
        form.save_m2m()
        # Auto-add newly assigned users as group members
        for user in task.assigned_to.all():
            group.members.add(user)
        # Parse new checklist items
        for item_content in request.POST.getlist('checklist_new[]'):
            if item_content.strip():
                GroupTaskChecklist.objects.create(task=task, content=item_content.strip())

        django_messages.success(request, f"Task '{task.title}' added!")
    else:
        django_messages.error(request, "Could not create task. Please check the form.")
    return redirect('collaboration:detail', pk=pk)


# ──────────────────────────────────────────────
# Edit task (creator only)
# ──────────────────────────────────────────────

@login_required
def edit_group_task(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)

    if not _is_creator(group, request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        form = EditGroupTaskForm(request.POST, request.FILES, instance=task, group=group)
        if form.is_valid():
            task = form.save()
            # Auto-add newly assigned users as group members
            for user in task.assigned_to.all():
                group.members.add(user)

            # Parse new checklist items
            for item_content in request.POST.getlist('checklist_new[]'):
                if item_content.strip():
                    GroupTaskChecklist.objects.create(task=task, content=item_content.strip())
            
            # Update or delete existing checklist items
            for item in task.checklist_items.all():
                if f"checklist_delete_{item.pk}" in request.POST:
                    item.delete()
                else:
                    new_val = request.POST.get(f"checklist_existing_{item.pk}")
                    if new_val and new_val.strip():
                        item.content = new_val.strip()
                        item.save()

            django_messages.success(request, f"Task '{task.title}' updated!")
            return redirect('collaboration:detail', pk=pk)
        else:
            django_messages.error(request, "Could not update task.")
            return redirect('collaboration:detail', pk=pk)

    # GET — return task data as JSON for modal population
    assigned_ids = list(task.assigned_to.values_list('id', flat=True))
    checklist = list(task.checklist_items.values('id', 'content', 'is_done'))
    return JsonResponse({
        'id': task.pk,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'deadline': task.deadline.strftime('%Y-%m-%dT%H:%M') if task.deadline else '',
        'assigned_to': assigned_ids,
        'checklist': checklist,
    })


# ──────────────────────────────────────────────
# Delete task (creator only)
# ──────────────────────────────────────────────

@login_required
@require_POST
def toggle_task_checklist(request, pk, task_pk, item_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)
    item = get_object_or_404(GroupTaskChecklist, pk=item_pk, task=task)

    if not (_is_creator(group, request.user) or task.assigned_to.filter(pk=request.user.pk).exists()):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    item.is_done = not item.is_done
    item.save()
    return JsonResponse({'success': True, 'is_done': item.is_done})


# ──────────────────────────────────────────────
# Delete task (creator only)
# ──────────────────────────────────────────────

@login_required
@require_POST
def delete_group_task(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)

    if not _is_creator(group, request.user):
        django_messages.error(request, "Only the project creator can delete tasks.")
        return redirect('collaboration:detail', pk=pk)

    task_title = task.title
    task.delete()
    django_messages.success(request, f"Task '{task_title}' deleted.")
    return redirect('collaboration:detail', pk=pk)


# ──────────────────────────────────────────────
# Delete group (creator only)
# ──────────────────────────────────────────────

@login_required
@require_POST
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)

    if not _is_creator(group, request.user):
        django_messages.error(request, "Only the project creator can delete this group.")
        return redirect('collaboration:detail', pk=pk)

    group_name = group.name
    group.delete()
    django_messages.success(request, f"Group '{group_name}' has been deleted.")
    return redirect('collaboration:list')


# ──────────────────────────────────────────────
# Member management (creator only)
# ──────────────────────────────────────────────

@login_required
@require_POST
def add_member(request, pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)

    if not _is_creator(group, request.user):
        django_messages.error(request, "Only the project creator can add members.")
        return redirect('collaboration:detail', pk=pk)

    username = request.POST.get('username', '').strip()
    try:
        user = User.objects.get(username__iexact=username)
        if group.members.filter(pk=user.pk).exists():
            django_messages.info(request, f"{user.username} is already a member.")
        else:
            group.members.add(user)
            django_messages.success(request, f"{user.username} added to the group!")
    except User.DoesNotExist:
        django_messages.error(request, f"No user found with username '{username}'.")
    return redirect('collaboration:detail', pk=pk)


@login_required
@require_POST
def remove_member(request, pk, user_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)

    if not _is_creator(group, request.user):
        django_messages.error(request, "Only the project creator can remove members.")
        return redirect('collaboration:detail', pk=pk)

    if user_pk == request.user.pk:
        django_messages.error(request, "You cannot remove yourself as the creator.")
        return redirect('collaboration:detail', pk=pk)

    try:
        user = group.members.get(pk=user_pk)
        group.members.remove(user)
        django_messages.success(request, f"{user.username} removed from the group.")
    except User.DoesNotExist:
        django_messages.error(request, "User not found in this group.")
    return redirect('collaboration:detail', pk=pk)


# ──────────────────────────────────────────────
# Task status update (any assigned member)
# ──────────────────────────────────────────────

@login_required
@require_POST
def update_group_task_status(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)

    # Allow creator OR assigned members to update status
    if not _is_creator(group, request.user) and not task.assigned_to.filter(pk=request.user.pk).exists():
        django_messages.error(request, "You are not assigned to this task.")
        return redirect('collaboration:detail', pk=pk)

    new_status = request.POST.get('status', task.status)
    valid_statuses = [choice[0] for choice in GroupTask.STATUS_CHOICES]
    if new_status in valid_statuses:
        task.status = new_status
        task.save()
    return redirect('collaboration:detail', pk=pk)


# ──────────────────────────────────────────────
# Group Chat
# ──────────────────────────────────────────────

@login_required
@require_POST
def send_message(request, pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    content = html.escape(request.POST.get('content', '').strip())
    if content:
        Message.objects.create(group=group, sender=request.user, content=content)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('collaboration:detail', pk=pk)


@login_required
def get_messages_api(request, pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    after_id = request.GET.get('after', 0)
    msgs = Message.objects.filter(group=group, pk__gt=after_id).order_by('timestamp').select_related('sender')
    data = [
        {
            'id': m.pk,
            'sender': m.sender.username,
            'sender_initial': m.sender.username[0].upper(),
            'content': m.content,
            'timestamp': m.timestamp.strftime('%I:%M %p'),
            'is_me': m.sender == request.user,
        }
        for m in msgs
    ]
    return JsonResponse({'messages': data})


# ──────────────────────────────────────────────
# Task Chat
# ──────────────────────────────────────────────

@login_required
@require_POST
def send_task_message(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)

    # Only assigned members or creator can send task messages
    if not _is_creator(group, request.user) and not task.assigned_to.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Not assigned to this task'}, status=403)

    content = html.escape(request.POST.get('content', '').strip())
    if content:
        TaskMessage.objects.create(task=task, sender=request.user, content=content)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('collaboration:detail', pk=pk)


@login_required
def get_task_messages_api(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk, members=request.user)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)

    # Only assigned members or creator can read task messages
    if not _is_creator(group, request.user) and not task.assigned_to.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Not assigned to this task'}, status=403)

    after_id = request.GET.get('after', 0)
    msgs = TaskMessage.objects.filter(task=task, pk__gt=after_id).order_by('timestamp').select_related('sender')
    data = [
        {
            'id': m.pk,
            'sender': m.sender.username,
            'sender_initial': m.sender.username[0].upper(),
            'content': m.content,
            'timestamp': m.timestamp.strftime('%I:%M %p'),
            'is_me': m.sender == request.user,
        }
        for m in msgs
    ]
    return JsonResponse({'messages': data})


# ──────────────────────────────────────────────
# User search API
# ──────────────────────────────────────────────

@login_required
def user_search_api(request):
    q = request.GET.get('q', '').strip()
    group_pk = request.GET.get('group', None)
    results = []

    if q and len(q) >= 1:
        users = User.objects.filter(
            username__icontains=q
        ) | User.objects.filter(
            first_name__icontains=q
        ) | User.objects.filter(
            last_name__icontains=q
        )
        users = users.exclude(pk=request.user.pk).distinct()[:10]

        exclude_pks = set()
        if group_pk:
            try:
                grp = Group.objects.get(pk=group_pk, members=request.user)
                exclude_pks = set(grp.members.values_list('pk', flat=True))
            except Group.DoesNotExist:
                pass

        for u in users:
            results.append({
                'id': u.pk,
                'username': u.username,
                'full_name': f"{u.first_name} {u.last_name}".strip() or u.username,
                'initial': u.username[0].upper(),
                'already_member': u.pk in exclude_pks,
            })

    return JsonResponse({'users': results})
