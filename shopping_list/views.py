import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ShoppingList, ItemCategory, ItemRecord
from .modelforms import ItemCategoryForm, ItemRecordForm


def shopping_list_detail(request, shopping_list_id):
    shopping_list = get_object_or_404(ShoppingList, id=shopping_list_id)
    return render(request, 'shopping_list/shopping_list_detail.html', {'shopping_list': shopping_list})


# 弃用的原地编辑表格的视图函数
def shopping_list_detail_inplace(request, shopping_list_id):
    shopping_list = get_object_or_404(ShoppingList, id=shopping_list_id)
    return render(request, 'shopping_list/shopping_list_detail_inplace.html', {'shopping_list': shopping_list})


def shopping_list_edit(request, shopping_list_id):
    context = dict()
    context['shopping_list'] = shopping_list = get_object_or_404(
        ShoppingList, id=shopping_list_id)
    context['cates'] = cates = dict()
    for item_category in shopping_list.categories.all():  # type: ignore
        item_category.context = ItemCategoryForm(
            instance=item_category).get_context()
        records = cates[item_category] = list()
        for record in item_category.items.all():
            record.context = ItemRecordForm(instance=record).get_context()
            records.append(record)
    context['item_category_form'] = ItemCategoryForm()
    return render(request, 'shopping_list/shopping_list_edit.html', context)


@require_POST
def fetch_add_item_category(request, shopping_list_id):
    res = dict()
    try:
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
    except ShoppingList.DoesNotExist:
        res['status'] = 'fail'
        res['message'] = 'shopping list does not exist'
    else:
        print(request.POST)
        form = ItemCategoryForm(request.POST)
        if form.is_valid():
            item_cate = form.save(commit=False)
            item_cate.shopping_list = shopping_list
            item_cate.save()
            res['status'] = 'success'
        else:
            res['status'] = 'fail'
            res['message'] = form.errors
    return JsonResponse(res)


@require_POST
def fetch_del_item_category(request):
    res = dict()
    try:
        pk = request.POST['id']
        item_category = ItemCategory.objects.get(id=pk)
    except KeyError:
        res['status'] = 'fail'
        res['message'] = 'no cate id in post'
    except ItemCategory.DoesNotExist:
        res['status'] = 'fail'
        res['message'] = 'shopping list does not exist'
    else:
        item_category.delete()
        res['status'] = 'success'
    return JsonResponse(res)


@require_POST
def ajax_change_item_category(request):
    item_category_id = request.POST.get('id')
    print(f"Received {request.POST}")
    try:
        item_category = ItemCategoryForm(
            request.POST, instance=ItemCategory.objects.get(id=item_category_id))
        item_category.save()
        return JsonResponse({
            'success': True,
        })
    except ItemCategory.DoesNotExist:
        return JsonResponse({'error': 'ItemCategory not found'})


@require_POST
def ajax_change_item_category_status(request):
    res_json = json.loads(request.body)
    shopping_list_id = res_json.get('target_id')
    status = res_json.get('value')
    print(f"Received {res_json}")
    try:
        item_category = ItemCategory.objects.get(id=shopping_list_id)
        item_category.status = status
        item_category.save()
        return JsonResponse({
            'success': True,
            'value': item_category.get_status_display(),  # type: ignore
            'css_class': item_category.get_css_class()
        })
    except ShoppingList.DoesNotExist:
        return JsonResponse({'error': 'ItemCategory not found'})


@require_POST
def ajax_change_item_record(request):
    item_record_id = request.POST.get('id')
    print(f"Received {request.POST}")
    try:
        item_category = ItemRecordForm(
            request.POST, instance=ItemRecord.objects.get(id=item_record_id))
        item_category.save()
        return JsonResponse({
            'success': True,
        })
    except ItemRecord.DoesNotExist:
        return JsonResponse({'error': 'ItemCategory not found'})


@require_POST
def ajax_change_item_category_name(request):
    res_json = json.loads(request.body)
    item_category_id = res_json.get('target_id')
    name = res_json.get('value')
    print(f"Received {res_json}")
    try:
        item_category = ItemCategory.objects.get(id=item_category_id)
        item_category.name = name
        item_category.save()
        return JsonResponse({
            'success': True,
        })
    except ItemCategory.DoesNotExist:
        return JsonResponse({'error': 'ItemCategory not found'})


@require_POST
def ajax_change_item_record_name(request):
    res_json = json.loads(request.body)
    item_id = res_json.get('target_id')
    name = res_json.get('value')
    print(f"Received {res_json}")
    try:
        record = ItemRecord.objects.get(id=item_id)
        record.name = name
        record.save()
        return JsonResponse({
            'success': True,
        })
    except ItemCategory.DoesNotExist:
        return JsonResponse({'error': 'Item not found'})


@require_POST
def ajax_change_item_record_quantity(request):
    res_json = json.loads(request.body)
    item_record_id = res_json.get('target_id')
    quantity = res_json.get('value')
    print(f"Received {res_json}")
    try:
        item_record = ItemRecord.objects.get(id=item_record_id)
        item_record.quantity = quantity
        item_record.save()
        return JsonResponse({
            'success': True,
        })
    except ItemCategory.DoesNotExist:
        return JsonResponse({'error': 'ItemRecord not found'})


@require_POST
def ajax_change_item_record_note(request):
    res_json = json.loads(request.body)
    item_record_id = res_json.get('target_id')
    note = res_json.get('value')
    print(f"Received {res_json}")
    try:
        item_record = ItemRecord.objects.get(id=item_record_id)
        item_record.note = note
        item_record.save()
        return JsonResponse({
            'success': True,
        })
    except ItemCategory.DoesNotExist:
        return JsonResponse({'error': 'ItemRecord not found'})


@require_POST
def ajax_create_item_category(request):
    res_json = json.loads(request.body)
    name = res_json.get('item_category_name')
    if name is None or name.strip() == '':
        return JsonResponse({'error': '品类名称不能为空'})
    shopping_list_id = res_json.get('shopping_list_id')
    note = res_json.get('item_category_note', '')
    print(f"Received {res_json}")

    try:
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        ItemCategory.objects.create(
            name=name, shopping_list=shopping_list, note=note)
        return JsonResponse({
            'success': True
        })
    except ShoppingList.DoesNotExist:
        return JsonResponse({'error': '清单不存在'})


@require_POST
def ajax_create_item_record(request):
    res_json = json.loads(request.body)
    item_name = res_json.get('item_name')
    if item_name is None or item_name.strip() == '':
        return JsonResponse({'error': '单品名称不能为空'})
    item_category_id = res_json.get('item_category_id')
    quantity = res_json.get('item_quantity', 1)
    note = res_json.get('item_record_note', '')
    print(f"Received {res_json}")
    try:
        item_category = ItemCategory.objects.get(id=item_category_id)
        ItemRecord.objects.create(
            name=item_name, category=item_category, quantity=quantity, note=note)
        return JsonResponse({
            'success': True
        })
    except ItemCategory.DoesNotExist:
        return JsonResponse({'error': '品类不存在'})
