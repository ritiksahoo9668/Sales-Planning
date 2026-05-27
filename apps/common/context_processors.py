from django.conf import settings


def erp_context(request):
    return {
        'ERP_APP_NAME': getattr(settings, 'ERP_APP_NAME', 'ERP'),
        'ERP_MODULE_NAME': getattr(settings, 'ERP_MODULE_NAME', 'Business Partners'),
    }
