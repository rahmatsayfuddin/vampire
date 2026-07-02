from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
import bleach
from .models import Finding
from vkb.models import VulnerabilityKnowledgeBase

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 's', 'ol', 'ul', 'li',
                'blockquote', 'pre', 'code', 'a', 'img', 'h1', 'h2', 'h3', 'h4']
ALLOWED_ATTRS = {'a': ['href', 'target'], 'img': ['src', 'alt']}


class SlaService:
    SLA_DEFAULTS = {
        'Critical': 7,
        'High': 14,
        'Medium': 30,
        'Low': 60,
    }

    @classmethod
    def sla_days(cls, finding):
        profile = finding.project.sla_profile
        if profile:
            attr = f'sla_{finding.severity.lower()}'
            return getattr(profile, attr, 30)
        return cls.SLA_DEFAULTS.get(finding.severity, 30)

    @classmethod
    def sla_due_date(cls, finding):
        return finding.created_at + timedelta(days=cls.sla_days(finding))

    @classmethod
    def is_late(cls, finding, now=None):
        if now is None:
            now = timezone.now()
        if finding.status == 'Closed' and finding.closed_at:
            return finding.closed_at > cls.sla_due_date(finding)
        if finding.status == 'Open':
            return now > cls.sla_due_date(finding)
        return False

    @classmethod
    def sla_delay_days(cls, finding, now=None):
        if now is None:
            now = timezone.now()
        if finding.status == 'Closed' and finding.closed_at:
            delta = (finding.closed_at - cls.sla_due_date(finding)).days
            return max(0, delta)
        elif finding.status == 'Open':
            delta = (now - cls.sla_due_date(finding)).days
            return max(0, delta)
        return 0


class FindingService:

    @staticmethod
    def get_queryset_for_user(user):
        if user.is_superuser:
            return Finding.objects.select_related('project', 'project__organization').all()
        return Finding.objects.filter(project__assignment__user=user).select_related('project', 'project__organization').distinct()

    @staticmethod
    def get_finding_for_user(pk, user):
        if user.is_superuser:
            return get_object_or_404(Finding, pk=pk)
        return get_object_or_404(Finding, pk=pk, project__assignment__user=user)

    @staticmethod
    def set_closed_at_by_status(finding):
        if finding.status == 'Closed' and not finding.closed_at:
            finding.closed_at = timezone.now()
        elif finding.status != 'Closed':
            finding.closed_at = None

    @staticmethod
    def promote_to_vkb(finding, category=None):
        category = category or 'Other Notable Vulnerabilities'
        return VulnerabilityKnowledgeBase.objects.create(
            title=finding.title,
            description=finding.description,
            impact=finding.impact,
            recommendation=finding.recommendation,
            category=category,
        )
