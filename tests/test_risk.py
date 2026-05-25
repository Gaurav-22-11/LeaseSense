from leasesense.risk import analyze_risks


def test_subleasing_restriction_is_flagged():
    text = "Tenant shall not sublease the premises without landlord's prior written consent."

    risks = analyze_risks(text)
    sublease = next(risk for risk in risks if risk.name == "Subleasing Restrictions")

    assert sublease.level.value == "high"
    assert sublease.evidence


def test_joint_liability_high_signal():
    text = "All tenants are jointly and severally liable for rent and damages."

    risks = analyze_risks(text)
    joint = next(risk for risk in risks if risk.name == "Joint Liability")

    assert joint.level.value == "high"

