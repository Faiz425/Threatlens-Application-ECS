import sys
from pathlib import Path

import pytest  # pyright: ignore[reportMissingImports]

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "app")
)

from app import app, calculate_risk, get_risk_label
from scanner import (  # pyright: ignore[reportMissingImports]
    scan_dockerfile,
    scan_terraform,
    scan_github_actions,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"ThreatLens" in response.data
    assert b"Security Scanner" in response.data


def test_dockerfile_root_detection():
    content = """
    FROM python:3.12
    USER root
    """

    findings = scan_dockerfile(content)

    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"
    assert findings[0]["title"] == "Container runs as root"


def test_terraform_open_security_group_detection():
    content = """
    resource "aws_security_group_rule" "ssh" {
        type = "ingress"
        from_port = 22
        to_port = 22
        cidr_blocks = ["0.0.0.0/0"]
    }
    """

    findings = scan_terraform(content)

    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"


def test_github_actions_static_credentials_detection():
    content = """
    env:
      AWS_ACCESS_KEY_ID: example
      AWS_SECRET_ACCESS_KEY: example
    """

    findings = scan_github_actions(content)

    assert any(
        finding["severity"] == "CRITICAL"
        for finding in findings
    )


def test_clean_dockerfile_has_no_findings():
    content = """
    FROM python:3.12

    RUN useradd --create-home appuser

    USER appuser
    """

    findings = scan_dockerfile(content)

    assert findings == []


def test_risk_score_for_high_finding():
    findings = [
        {
            "severity": "HIGH"
        }
    ]

    score = calculate_risk(findings)

    assert score == 80


def test_risk_score_for_critical_finding():
    findings = [
        {
            "severity": "CRITICAL"
        }
    ]

    score = calculate_risk(findings)

    assert score == 65


def test_risk_score_never_goes_below_zero():
    findings = [
        {"severity": "CRITICAL"},
        {"severity": "CRITICAL"},
        {"severity": "CRITICAL"},
        {"severity": "CRITICAL"},
    ]

    score = calculate_risk(findings)

    assert score == 0


def test_risk_label():
    assert get_risk_label(100) == "LOW RISK"
    assert get_risk_label(80) == "MODERATE RISK"
    assert get_risk_label(50) == "HIGH RISK"
    assert get_risk_label(20) == "CRITICAL RISK"


def test_scan_endpoint(client):
    response = client.post(
        "/scan",
        data={
            "type": "dockerfile",
            "content": """
            FROM python:3.12
            USER root
            """
        },
    )

    assert response.status_code == 200
    assert b"Container runs as root" in response.data


def test_scan_rejects_empty_content(client):
    response = client.post(
        "/scan",
        data={
            "type": "dockerfile",
            "content": "",
        },
    )

    assert response.status_code == 400


def test_scan_rejects_invalid_type(client):
    response = client.post(
        "/scan",
        data={
            "type": "invalid",
            "content": "test",
        },
    )

    assert response.status_code == 400