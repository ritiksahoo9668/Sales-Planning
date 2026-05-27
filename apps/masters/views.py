from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.masters.services import (
    create_vendor_category,
    create_vendor_sub_category,
    create_vendor_type,
    delete_vendor_category,
    delete_vendor_sub_category,
    delete_vendor_type,
)


def _json_error(message, status=400):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _ensure_superadmin(request):
    if not request.user.is_superuser:
        return _json_error('Only superadmin can perform this action.', status=403)
    return None


@login_required
@require_POST
def vendor_type_create(request):
    permission_error = _ensure_superadmin(request)
    if permission_error:
        return permission_error
    name = request.POST.get('name', '')
    try:
        obj = create_vendor_type(name, user=request.user)
    except ValueError as exc:
        return _json_error(str(exc))
    return JsonResponse({'ok': True, 'id': obj.pk, 'name': obj.name})


@login_required
@require_POST
def vendor_category_create(request):
    permission_error = _ensure_superadmin(request)
    if permission_error:
        return permission_error
    name = request.POST.get('name', '')
    try:
        obj = create_vendor_category(name, user=request.user)
    except ValueError as exc:
        return _json_error(str(exc))
    return JsonResponse({'ok': True, 'id': obj.pk, 'name': obj.name})


@login_required
@require_POST
def vendor_sub_category_create(request):
    permission_error = _ensure_superadmin(request)
    if permission_error:
        return permission_error
    name = request.POST.get('name', '')
    category_id = request.POST.get('category_id', '')
    try:
        obj = create_vendor_sub_category(int(category_id), name, user=request.user)
    except (ValueError, TypeError) as exc:
        return _json_error(str(exc))
    return JsonResponse({
        'ok': True,
        'id': obj.pk,
        'name': obj.name,
        'category_id': obj.category_id,
    })


@login_required
@require_POST
def vendor_type_delete(request):
    permission_error = _ensure_superadmin(request)
    if permission_error:
        return permission_error
    type_id = request.POST.get('id')
    try:
        delete_vendor_type(int(type_id))
    except (ValueError, TypeError) as exc:
        return _json_error(str(exc))
    return JsonResponse({'ok': True})


@login_required
@require_POST
def vendor_category_delete(request):
    permission_error = _ensure_superadmin(request)
    if permission_error:
        return permission_error
    category_id = request.POST.get('id')
    try:
        delete_vendor_category(int(category_id))
    except (ValueError, TypeError) as exc:
        return _json_error(str(exc))
    return JsonResponse({'ok': True})


@login_required
@require_POST
def vendor_sub_category_delete(request):
    permission_error = _ensure_superadmin(request)
    if permission_error:
        return permission_error
    sub_category_id = request.POST.get('id')
    try:
        delete_vendor_sub_category(int(sub_category_id))
    except (ValueError, TypeError) as exc:
        return _json_error(str(exc))
    return JsonResponse({'ok': True})


@login_required
def vendor_sub_categories_list(request):
    """Return active sub-categories (optional ?category_id=)."""
    from apps.masters.models import VendorSubCategory

    qs = VendorSubCategory.objects.filter(is_active=True, is_deleted=False)
    category_id = request.GET.get('category_id')
    if category_id:
        qs = qs.filter(category_id=category_id)
    rows = list(qs.values('id', 'name', 'category_id'))
    return JsonResponse(rows, safe=False)
