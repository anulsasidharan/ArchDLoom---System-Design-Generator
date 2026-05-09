"""Compliance mapping for GDPR / HIPAA / SOC 2 (and PCI-DSS where signals warrant)."""

from __future__ import annotations

import re

from app.domain.enterprise import ComplianceControl, ComplianceFramework, ComplianceMapping
from app.domain.requirements import ParsedRequirement

# Canonical control catalog. Each control maps to one or more frameworks.
_CONTROLS: list[ComplianceControl] = [
    ComplianceControl(
        id="iam.rbac",
        name="Role-based access control with least privilege",
        description=(
            "Deny-by-default IAM, periodic access reviews, and just-in-time elevation "
            "for production data and infrastructure planes."
        ),
        frameworks=["SOC2", "HIPAA", "GDPR", "PCI-DSS"],
    ),
    ComplianceControl(
        id="iam.mfa",
        name="MFA on privileged identities",
        description="Hardware-backed MFA on admin / break-glass identities and SSO.",
        frameworks=["SOC2", "HIPAA", "PCI-DSS"],
    ),
    ComplianceControl(
        id="data.encryption_at_rest",
        name="Encryption at rest with managed keys",
        description=(
            "AES-256 (or stronger) at rest with KMS-backed key custody; rotate keys per policy "
            "and segregate envelope keys per tenant or data class."
        ),
        frameworks=["SOC2", "HIPAA", "GDPR", "PCI-DSS"],
    ),
    ComplianceControl(
        id="data.encryption_in_transit",
        name="TLS 1.2+ everywhere",
        description="TLS 1.2+ on all external and east-west traffic; certificate rotation automated.",
        frameworks=["SOC2", "HIPAA", "GDPR", "PCI-DSS"],
    ),
    ComplianceControl(
        id="data.subject_rights",
        name="Data subject rights operations",
        description=(
            "Documented runbooks for access, rectification, deletion, and portability requests, "
            "with SLA tracking."
        ),
        frameworks=["GDPR"],
    ),
    ComplianceControl(
        id="data.dlp",
        name="Data classification and DLP",
        description=(
            "Classify PII / PHI / cardholder data; DLP scanning on egress and on developer endpoints."
        ),
        frameworks=["GDPR", "HIPAA", "PCI-DSS"],
    ),
    ComplianceControl(
        id="data.minimization",
        name="Data minimization & retention policy",
        description=(
            "Collect only data required for stated purposes; enforce per-class retention windows "
            "and crypto-shredding on expiry."
        ),
        frameworks=["GDPR", "HIPAA"],
    ),
    ComplianceControl(
        id="audit.immutable_logs",
        name="Immutable audit trail",
        description=(
            "Centralize control-plane and data-plane logs in tamper-evident storage; "
            "1+ year retention with restricted access."
        ),
        frameworks=["SOC2", "HIPAA", "PCI-DSS"],
    ),
    ComplianceControl(
        id="audit.access_review",
        name="Quarterly access review",
        description="Documented quarterly review of human and machine identities with attestation.",
        frameworks=["SOC2", "HIPAA"],
    ),
    ComplianceControl(
        id="ops.vuln_mgmt",
        name="Vulnerability management",
        description=(
            "Patching SLAs by severity, dependency scanning in CI, and external pen-test on cadence."
        ),
        frameworks=["SOC2", "PCI-DSS", "HIPAA"],
    ),
    ComplianceControl(
        id="ops.incident_response",
        name="Incident response with breach notification",
        description=(
            "Runbooks tied to severity matrix, paging rotation, and regulator/data-subject notification "
            "windows (e.g. 72h GDPR)."
        ),
        frameworks=["GDPR", "HIPAA", "SOC2"],
    ),
    ComplianceControl(
        id="ops.change_management",
        name="Change management with approvals",
        description="Peer-reviewed, traceable changes with rollback plans for production services.",
        frameworks=["SOC2", "PCI-DSS"],
    ),
    ComplianceControl(
        id="ops.bcp_dr",
        name="BCP / DR with tested drills",
        description=(
            "Documented business-continuity and DR plan with annual restore drills and result evidence."
        ),
        frameworks=["SOC2", "HIPAA"],
    ),
    ComplianceControl(
        id="vendor.tpra",
        name="Third-party / sub-processor risk",
        description=(
            "Vendor inventory, DPAs, and risk reviews; sub-processor list published for GDPR scope."
        ),
        frameworks=["GDPR", "SOC2"],
    ),
    ComplianceControl(
        id="phi.transmission_safeguards",
        name="HIPAA technical & transmission safeguards",
        description="Unique user IDs, automatic logoff, integrity controls, and PHI transmission encryption.",
        frameworks=["HIPAA"],
    ),
    ComplianceControl(
        id="phi.baa",
        name="Business Associate Agreements (BAA)",
        description="BAAs in place with all sub-processors handling PHI before processing begins.",
        frameworks=["HIPAA"],
    ),
    ComplianceControl(
        id="card.scope_reduction",
        name="Cardholder-data scope reduction",
        description=(
            "Tokenize PAN at the edge; offload acceptance/storage to PCI-DSS scoped processors where possible."
        ),
        frameworks=["PCI-DSS"],
    ),
    ComplianceControl(
        id="card.network_segmentation",
        name="Network segmentation around CDE",
        description="Hard segmentation around any cardholder-data environment with documented flows.",
        frameworks=["PCI-DSS"],
    ),
]


_FRAMEWORK_NAMES: dict[str, str] = {
    "GDPR": "GDPR (EU 2016/679)",
    "HIPAA": "HIPAA (US Health Insurance Portability and Accountability Act)",
    "SOC2": "SOC 2 (Trust Services Criteria)",
    "PCI-DSS": "PCI-DSS (Payment Card Industry Data Security Standard)",
}

_DOMAIN_TO_INFERRED: dict[str, list[str]] = {
    "healthcare": ["HIPAA", "SOC2"],
    "health": ["HIPAA", "SOC2"],
    "medical": ["HIPAA", "SOC2"],
    "fintech": ["SOC2", "PCI-DSS"],
    "finance": ["SOC2", "PCI-DSS"],
    "banking": ["SOC2", "PCI-DSS"],
    "payments": ["PCI-DSS", "SOC2"],
    "e-commerce": ["PCI-DSS", "GDPR", "SOC2"],
    "ecommerce": ["PCI-DSS", "GDPR", "SOC2"],
    "retail": ["PCI-DSS", "GDPR", "SOC2"],
    "saas": ["SOC2", "GDPR"],
    "edtech": ["GDPR", "SOC2"],
    "education": ["GDPR", "SOC2"],
    "marketplace": ["PCI-DSS", "GDPR", "SOC2"],
}

_KEYWORD_INFERENCE: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bphi\b|protected health|patient|ehr|emr", re.IGNORECASE), "HIPAA"),
    (re.compile(r"\bpii\b|personal data|gdpr|eu citizens?|data subject", re.IGNORECASE), "GDPR"),
    (re.compile(r"credit card|cardholder|pan|payment card|pci", re.IGNORECASE), "PCI-DSS"),
    (re.compile(r"\bsoc ?2\b|trust services|customer attestation", re.IGNORECASE), "SOC2"),
]


def _normalize_explicit(name: str) -> str | None:
    if not name:
        return None
    n = re.sub(r"[^a-z0-9]+", "", name.lower())
    if n in {"gdpr", "eugdpr"}:
        return "GDPR"
    if n in {"hipaa", "hipaaomnibus"}:
        return "HIPAA"
    if n in {"soc2", "soc2type1", "soc2type2", "soc2typeii"}:
        return "SOC2"
    if "pci" in n:
        return "PCI-DSS"
    return None


def _drivers_for(code: str, req: ParsedRequirement) -> list[str]:
    domain = req.domain.lower()
    drivers: list[str] = []
    if code == "GDPR":
        drivers.append("Personal data of EU/UK data subjects in or out of scope.")
        if "marketplace" in domain or "ecommerce" in domain or "e-commerce" in domain:
            drivers.append("Consumer accounts and order history typically constitute personal data.")
    if code == "HIPAA":
        drivers.append("Protected Health Information (PHI) handled by the system.")
    if code == "SOC2":
        drivers.append("B2B / SaaS customer trust attestation expected by enterprise buyers.")
    if code == "PCI-DSS":
        drivers.append("Card payment data accepted, processed, transmitted, or stored.")
    return drivers


def build_compliance_mapping(requirements: ParsedRequirement) -> ComplianceMapping:
    """Return aggregated compliance posture combining explicit + inferred frameworks."""
    explicit_codes: list[str] = []
    for need in requirements.compliance_needs:
        code = _normalize_explicit(need.name)
        if code and code not in explicit_codes:
            explicit_codes.append(code)

    domain_key = requirements.domain.lower().strip()
    inferred = list(_DOMAIN_TO_INFERRED.get(domain_key, []))

    blob_sources: list[str] = [
        requirements.summary or "",
        " ".join(requirements.core_features),
    ]
    for fr in requirements.functional_requirements:
        blob_sources.append(f"{fr.name} {fr.description}")
    for c in requirements.compliance_needs:
        blob_sources.append(f"{c.name} {c.description}")
    blob = "\n".join(blob_sources)
    for pattern, code in _KEYWORD_INFERENCE:
        if pattern.search(blob) and code not in inferred and code not in explicit_codes:
            inferred.append(code)

    seen: list[str] = []
    for code in [*explicit_codes, *inferred]:
        if code not in seen:
            seen.append(code)

    if not seen:
        seen = ["SOC2"]
        inferred = ["SOC2"]

    frameworks: list[ComplianceFramework] = []
    for code in seen:
        controls = [c for c in _CONTROLS if code in c.frameworks]
        frameworks.append(
            ComplianceFramework(
                code=code,
                name=_FRAMEWORK_NAMES.get(code, code),
                drivers=_drivers_for(code, requirements),
                controls=controls,
            )
        )

    notes: list[str] = []
    if not explicit_codes:
        notes.append(
            "No frameworks were explicitly stated — the inferred set is a starting point for legal/security review."
        )
    if "GDPR" in seen and "HIPAA" in seen:
        notes.append(
            "Operating across GDPR + HIPAA scopes: separate retention and breach-notification clocks must be tracked."
        )
    if "PCI-DSS" in seen:
        notes.append(
            "Aggressively reduce PCI scope by tokenizing PAN at the edge or using a hosted vault."
        )

    return ComplianceMapping(
        frameworks=frameworks,
        inferred_codes=inferred,
        explicit_codes=explicit_codes,
        notes=notes,
    )
