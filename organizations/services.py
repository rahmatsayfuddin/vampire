from .models import Organization


class OrganizationService:

    @staticmethod
    def get_queryset_for_user(user):
        if user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(project__assignment__user=user).distinct()
