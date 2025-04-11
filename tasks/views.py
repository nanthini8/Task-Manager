import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.db.models import Q
import datetime

@csrf_exempt
def task_list(request):
    if request.method == "GET":
        # Filters and search
        status = request.GET.get('status')
        priority = request.GET.get('priority')
        search = request.GET.get('search')

        tasks = Task.objects.all()

        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if search:
            tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))

        today = datetime.date.today()
        due = request.GET.get('due')
        if due == 'upcoming':
            tasks = tasks.filter(due_date__gte=today)
        elif due == 'overdue':
            tasks = tasks.filter(due_date__lt=today)

        data = [{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'user_id': task.user.id,
        } for task in tasks]

        return JsonResponse(data,safe=False) # In order to allow non-dict objects to be serialized set the safe parameter to False

    elif request.method == "POST":
        body = json.loads(request.body)
        user = User.objects.get(id=body['user_id'])
        task = Task.objects.create(
            title=body['title'],
            description=body['description'],
            status=body['status'],
            priority=body['priority'],
            due_date=parse_date(body['due_date']),
            user=user
        )
        return JsonResponse({'id': task.id, 'message': 'Task created successfully'})
    
@csrf_exempt
def task_detail(request, pk):
    try:
        task = Task.objects.get(id=pk)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    if request.method == "GET":
        data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'user_id': task.user.id,
        }
        return JsonResponse(data)

    elif request.method == "PUT":
        body = json.loads(request.body)
        task.title = body['title']
        task.description = body['description']
        task.status = body['status']
        task.priority = body['priority']
        task.due_date = parse_date(body['due_date'])
        task.save()
        return JsonResponse({'message': 'Task updated successfully'})

    elif request.method == "DELETE":
        task.delete()
        return JsonResponse({'message': 'Task deleted'})

