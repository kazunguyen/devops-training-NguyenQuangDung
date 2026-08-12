import json

def generate_threat_model():
    print("Initializing Threat Modeling as Code (TMAC)...")
    architecture = [
        "Client",
        "Cloud Load Balancing",
        "Compute Engine Web Server",
        "Cloud SQL"
    ]
    print(f"Analyzing Data Flow: {' -> '.join(architecture)}")

    stride_risks = [
        {
            "category": "Spoofing",
            "component": "Client -> Cloud Load Balancing",
            "description": "Attacker impersonates a valid user or steals session cookies.",
            "severity": "HIGH",
            "mitigation": "Enable Identity-Aware Proxy (IAP) for central authentication."
        },
        {
            "category": "Tampering",
            "component": "Cloud Load Balancing -> Compute Engine Web Server",
            "description": "Data modification in transit or malicious payload (e.g. SQLi).",
            "severity": "CRITICAL",
            "mitigation": "Enforce HTTPS/TLS and attach Cloud Armor security policy."
        },
        {
            "category": "Repudiation",
            "component": "Compute Engine Web Server",
            "description": "User performs administrative actions without leaving a trace.",
            "severity": "MEDIUM",
            "mitigation": "Enable Cloud Audit Logs for the backend services."
        },
        {
            "category": "Information Disclosure",
            "component": "Compute Engine Web Server -> Cloud SQL",
            "description": "Hard-coded database credentials in environment variables.",
            "severity": "HIGH",
            "mitigation": "Store credentials in Google Cloud Secret Manager."
        },
        {
            "category": "Denial of Service",
            "component": "Cloud Load Balancing",
            "description": "Volumetric attack exhausting Compute Engine resources.",
            "severity": "HIGH",
            "mitigation": "Configure Rate Limiting in Cloud Armor."
        },
        {
            "category": "Elevation of Privilege",
            "component": "Cloud SQL",
            "description": "Compromised service account has Editor role, allowing DB deletion.",
            "severity": "CRITICAL",
            "mitigation": "Apply IAM Least Privilege with Custom Roles."
        }
    ]

    # Export to JSON
    with open("stride_report.json", "w", encoding="utf-8") as f:
        json.dump(stride_risks, f, indent=4, ensure_ascii=False)
    print("=> Generated stride_report.json")

    # Export to Graphviz DOT
    dot_content = """digraph G {
    rankdir=LR;
    node [shape=box, style=filled, color=lightblue];
    Client -> CloudLoadBalancing [label="HTTPS / Spoofing & DoS"];
    CloudLoadBalancing -> ComputeEngine [label="Internal / Tampering"];
    ComputeEngine -> CloudSQL [label="TCP / Info Disclosure"];
    
    CloudLoadBalancing [color=lightgreen];
    CloudSQL [color=lightyellow];
}
"""
    with open("architecture.dot", "w", encoding="utf-8") as f:
        f.write(dot_content)
    print("=> Generated architecture.dot")
    print("Threat modeling analysis complete.")

if __name__ == "__main__":
    generate_threat_model()
