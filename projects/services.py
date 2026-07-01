from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Project


class ProjectMetricsService:

    @staticmethod
    def spi(project, now=None):
        if not project.end_date or not project.start_date:
            return None
        planned_duration = (project.end_date - project.start_date).days
        if planned_duration <= 0:
            return None
        if project.completed_date:
            actual_duration = (project.completed_date - project.start_date).days
        else:
            now_date = now.date() if now else timezone.now().date()
            actual_duration = (now_date - project.start_date).days
        if actual_duration <= 0:
            return None
        return round(planned_duration / actual_duration, 2)


class ProjectService:

    @staticmethod
    def get_queryset_for_user(user):
        if user.is_superuser:
            return Project.objects.select_related('organization').all()
        return Project.objects.filter(assignment__user=user).select_related('organization').distinct()

    @staticmethod
    def get_project_for_user(pk, user):
        if user.is_superuser:
            return get_object_or_404(Project, pk=pk)
        return get_object_or_404(Project, pk=pk, assignment__user=user)

    @staticmethod
    def set_completed_date_by_status(project):
        if project.status == 'Completed' and not project.completed_date:
            project.completed_date = timezone.now().date()
        elif project.status != 'Completed':
            project.completed_date = None
