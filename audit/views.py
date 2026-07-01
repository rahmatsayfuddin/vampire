from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AuditLog
from django.core.paginator import Paginator


@login_required
@user_passes_test(lambda u: u.is_superuser)
def audit_list(request):
    logs = AuditLog.objects.select_related('user', 'content_type').all()
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'audit/audit_list.html', {
        'page_obj': page_obj,
        'num_pages': paginator.num_pages,
    })
