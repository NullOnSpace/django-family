import json

from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import HttpRequest, JsonResponse

from .models import TaskCalendar


# Create your views here.
@require_POST
def fetch_change_task_status(request: HttpRequest) -> JsonResponse:
    res = dict()
    try:
        data = json.loads(request.body)
    except Exception:
        res['status'] = 'error'
        res['message'] = '无效的JSON数据'
        return JsonResponse(res)
    print(data)
    task_id = data.get('task_id')
    is_completed = data.get('new_status')
    if not task_id or not isinstance(is_completed, bool):
        res['status'] = 'error'
        res['message'] = '缺少必要参数'
    else:
        try:
            task = TaskCalendar.objects.get(id=task_id)
            task.is_completed = is_completed
            task.save()
            res['status'] = 'success'
            res['is_completed'] = task.is_completed
            res['status_class'] = task.get_display_class()
            res['status_text'] = task.get_status()
            res['message'] = '任务状态更新成功'
        except TaskCalendar.DoesNotExist:
            res['status'] = 'error'
            res['message'] = 'task id not found'
        except Exception as e:
            res['status'] = 'error'
            res['message'] = str(e)
    return JsonResponse(res)