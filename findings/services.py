from datetime import timedelta, datetime, date, timezone
from django.utils import timezone as tz
from django.shortcuts import get_object_or_404
import bleach
from .models import Finding, FindingComment
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
    def _get_ra_expiry(cls, finding):
        ra = finding.risk_acceptances.first()
        if ra:
            return datetime.combine(ra.accept_until, datetime.min.time()).replace(tzinfo=timezone.utc)
        return None

    @classmethod
    def sla_days(cls, finding):
        if finding.status == 'Risk Acceptance':
            return None
        profile = finding.project.sla_profile
        if profile:
            attr = f'sla_{finding.severity.lower()}'
            return getattr(profile, attr, 30)
        return cls.SLA_DEFAULTS.get(finding.severity, 30)

    @classmethod
    def sla_due_date(cls, finding):
        if finding.status == 'Risk Acceptance':
            expiry = cls._get_ra_expiry(finding)
            if expiry:
                return expiry
        return finding.created_at + timedelta(days=cls.sla_days(finding) or 30)

    @classmethod
    def is_late(cls, finding, now=None):
        if now is None:
            now = tz.now()
        if finding.status == 'Closed' and finding.closed_at:
            return finding.closed_at > cls.sla_due_date(finding)
        if finding.status in ('Open', 'Risk Acceptance'):
            return now > cls.sla_due_date(finding)
        return False

    @classmethod
    def sla_delay_days(cls, finding, now=None):
        if now is None:
            now = tz.now()
        due = cls.sla_due_date(finding)
        if finding.status == 'Closed' and finding.closed_at:
            delta = (finding.closed_at - due).days
            return max(0, delta)
        if finding.status in ('Open', 'Risk Acceptance'):
            delta = (now - due).days
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
            finding.closed_at = tz.now()
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

    @staticmethod
    def accept_risk(finding, reason, evidence, user, accept_until):
        from .models import RiskAcceptance
        ra = RiskAcceptance.objects.create(
            finding=finding, reason=reason, evidence=evidence,
            accepted_by=user, accept_until=accept_until,
        )
        finding.status = 'Risk Acceptance'
        finding.save()
        return ra

    @staticmethod
    def reopen(finding, reason, user):
        finding.status = 'Open'
        finding.closed_at = None
        finding.save()
        FindingComment.objects.create(finding=finding, user=user, content=f'Reopened: {reason}')

    @staticmethod
    def close(finding):
        finding.status = 'Closed'
        finding.closed_at = tz.now()
        finding.save()
