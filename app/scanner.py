import re


def scan_dockerfile(content):
    findings = []

    if re.search(r"USER\s+root", content, re.IGNORECASE):
        findings.append({
            "severity": "HIGH",
            "title": "Container runs as root",
            "description": (
                "Running the application as root increases the impact "
                "of a potential container compromise."
            ),
            "recommendation": (
                "Create a dedicated non-root user and run the application "
                "using that user."
            )
        })

    if re.search(r"FROM\s+\S+:latest", content, re.IGNORECASE):
        findings.append({
            "severity": "MEDIUM",
            "title": "Unpinned Docker image",
            "description": (
                "Using the latest tag can result in unpredictable builds "
                "and makes image versions difficult to track."
            ),
            "recommendation": (
                "Pin the image to a specific version or digest."
            )
        })

    if re.search(
        r"(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|PASSWORD|SECRET_KEY)\s*=",
        content,
        re.IGNORECASE
    ):
        findings.append({
            "severity": "CRITICAL",
            "title": "Potential secret detected",
            "description": (
                "A credential or secret may be hardcoded in the Dockerfile."
            ),
            "recommendation": (
                "Remove the secret and use a secure secrets-management "
                "solution such as AWS Secrets Manager."
            )
        })

    return findings


def scan_terraform(content):
    findings = []

    if "0.0.0.0/0" in content:
        findings.append({
            "severity": "HIGH",
            "title": "Potential unrestricted network access",
            "description": (
                "0.0.0.0/0 allows traffic from any IPv4 address."
            ),
            "recommendation": (
                "Restrict access to trusted CIDR ranges and only expose "
                "the ports that are required."
            )
        })

    if re.search(r"encrypted\s*=\s*false", content, re.IGNORECASE):
        findings.append({
            "severity": "HIGH",
            "title": "Encryption disabled",
            "description": (
                "A resource appears to have encryption explicitly disabled."
            ),
            "recommendation": (
                "Enable encryption at rest wherever supported."
            )
        })

    return findings


def scan_github_actions(content):
    findings = []

    if re.search(
        r"AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY",
        content,
        re.IGNORECASE
    ):
        findings.append({
            "severity": "CRITICAL",
            "title": "Static AWS credentials detected",
            "description": (
                "Long-lived AWS credentials in CI/CD create a significant "
                "security risk if they are exposed."
            ),
            "recommendation": (
                "Use GitHub Actions OIDC with an AWS IAM role instead "
                "of storing long-lived credentials."
            )
        })

    if "permissions:" not in content:
        findings.append({
            "severity": "MEDIUM",
            "title": "GitHub Actions permissions not explicitly defined",
            "description": (
                "The workflow does not explicitly define GitHub token "
                "permissions."
            ),
            "recommendation": (
                "Define the minimum required permissions at workflow "
                "or job level."
            )
        })

    return findings