# pyright: reportMissingImports=false

from flask import Flask, jsonify, request, render_template_string
from scanner import (
    scan_dockerfile,
    scan_terraform,
    scan_github_actions,
)

app = Flask(__name__)


HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>ThreatLens</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1100px;
            margin: 40px auto;
            padding: 20px;
            background: #f4f6f8;
            color: #1f2937;
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #6b7280;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            margin-bottom: 25px;
        }

        select,
        textarea,
        button {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            box-sizing: border-box;
        }

        textarea {
            min-height: 300px;
            font-family: monospace;
            resize: vertical;
        }

        button {
            background: #111827;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }

        button:hover {
            background: #374151;
        }

        .features {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
        }

        .feature {
            flex: 1;
            background: white;
            padding: 18px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        .feature strong {
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>

<body>

    <h1>🛡️ ThreatLens</h1>

    <p class="subtitle">
        AI-assisted DevSecOps security scanner.
        Find the risk. Understand the vulnerability. Fix it.
    </p>

    <div class="features">
        <div class="feature">
            🐳
            <strong>Container Security</strong>
            Dockerfile analysis
        </div>

        <div class="feature">
            ☁️
            <strong>Infrastructure Security</strong>
            Terraform analysis
        </div>

        <div class="feature">
            ⚙️
            <strong>CI/CD Security</strong>
            GitHub Actions analysis
        </div>
    </div>

    <div class="card">

        <h2>Security Scanner</h2>

        <form method="POST" action="/scan">

            <label for="type">
                <strong>What are you scanning?</strong>
            </label>

            <select name="type" id="type">
                <option value="dockerfile">🐳 Dockerfile</option>
                <option value="terraform">☁️ Terraform</option>
                <option value="github">⚙️ GitHub Actions</option>
            </select>

            <br><br>

            <label for="content">
                <strong>Paste your configuration</strong>
            </label>

            <textarea
                id="content"
                name="content"
                placeholder="Paste your configuration here..."
                required
            ></textarea>

            <button type="submit">
                🔍 Scan for Security Issues
            </button>

        </form>

    </div>

</body>
</html>
"""


def calculate_risk(findings):
    """
    Calculate a simple security risk score.

    The score starts at 100 and decreases according
    to the severity of detected findings.
    """

    deductions = {
        "CRITICAL": 35,
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 5,
    }

    score = 100

    for finding in findings:
        severity = finding.get("severity", "LOW")
        score -= deductions.get(severity, 0)

    return max(score, 0)


def get_risk_label(score):
    if score >= 90:
        return "LOW RISK"
    elif score >= 70:
        return "MODERATE RISK"
    elif score >= 40:
        return "HIGH RISK"

    return "CRITICAL RISK"


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/scan", methods=["POST"])
def scan():
    content = request.form.get("content", "")
    scan_type = request.form.get("type", "")

    if not content.strip():
        return jsonify(error="No content provided"), 400

    if scan_type == "dockerfile":
        findings = scan_dockerfile(content)

    elif scan_type == "terraform":
        findings = scan_terraform(content)

    elif scan_type == "github":
        findings = scan_github_actions(content)

    else:
        return jsonify(error="Invalid scan type"), 400

    score = calculate_risk(findings)
    risk_label = get_risk_label(score)

    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <title>ThreatLens Security Report</title>

            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1100px;
                    margin: 40px auto;
                    padding: 20px;
                    background: #f4f6f8;
                    color: #1f2937;
                }

                .header {
                    margin-bottom: 25px;
                }

                .score {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    margin-bottom: 25px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
                }

                .score-number {
                    font-size: 48px;
                    font-weight: bold;
                }

                .risk-label {
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 5px;
                }

                .finding {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }

                .severity {
                    font-weight: bold;
                    font-size: 18px;
                    margin-bottom: 10px;
                }

                .critical {
                    color: #991b1b;
                }

                .high {
                    color: #dc2626;
                }

                .medium {
                    color: #d97706;
                }

                .low {
                    color: #2563eb;
                }

                .recommendation {
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 15px;
                }

                .clean {
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }

                a {
                    display: inline-block;
                    margin-top: 20px;
                    text-decoration: none;
                    color: white;
                    background: #111827;
                    padding: 12px 20px;
                    border-radius: 6px;
                }
            </style>
        </head>

        <body>

            <div class="header">
                <h1>🛡️ ThreatLens</h1>
                <p>Security Analysis Report</p>
            </div>

            <div class="score">

                <div>
                    <strong>Security Score</strong>
                </div>

                <div class="score-number">
                    {{ score }}/100
                </div>

                <div class="risk-label">
                    {{ risk_label }}
                </div>

                <p>
                    {{ findings|length }} security finding(s) detected.
                </p>

            </div>

            {% if findings %}

                {% for finding in findings %}

                    <div class="finding">

                        <div class="severity
                            {% if finding.severity == 'CRITICAL' %}
                                critical
                            {% elif finding.severity == 'HIGH' %}
                                high
                            {% elif finding.severity == 'MEDIUM' %}
                                medium
                            {% else %}
                                low
                            {% endif %}
                        ">

                            {% if finding.severity == "CRITICAL" %}
                                🔴
                            {% elif finding.severity == "HIGH" %}
                                🟠
                            {% elif finding.severity == "MEDIUM" %}
                                🟡
                            {% else %}
                                🔵
                            {% endif %}

                            {{ finding.severity }}

                        </div>

                        <h2>{{ finding.title }}</h2>

                        <p>
                            {{ finding.description }}
                        </p>

                        <div class="recommendation">

                            <strong>💡 Recommendation</strong>

                            <p>
                                {{ finding.recommendation }}
                            </p>

                        </div>

                    </div>

                {% endfor %}

            {% else %}

                <div class="clean">

                    <h2>✅ No security issues detected</h2>

                    <p>
                        ThreatLens did not identify any issues using
                        the current security rules.
                    </p>

                </div>

            {% endif %}

            <a href="/">← Scan another configuration</a>

        </body>

        </html>
        """,
        findings=findings,
        score=score,
        risk_label=risk_label,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)