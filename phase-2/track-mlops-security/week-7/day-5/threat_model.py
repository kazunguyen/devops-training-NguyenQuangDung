#!/usr/bin/env python3
"""
Threat Modeling as Code cho Web App trên Google Cloud dựa trên mô hình STRIDE.
"""

import json
import os
import sys

# Thiết lập stdout encoding cho Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

class ThreatModel:
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.flows = []
        self.threats = []

    def add_element(self, element_id, name, element_type, boundary):
        element = {
            "id": element_id,
            "name": name,
            "type": element_type,
            "boundary": boundary
        }
        self.elements.append(element)
        return element

    def add_flow(self, source_id, target_id, protocol, data_description):
        flow = {
            "source": source_id,
            "target": target_id,
            "protocol": protocol,
            "data": data_description
        }
        self.flows.append(flow)
        return flow

    def analyze_stride(self):
        self.threats = []
        
        # Phân tích từng luồng dữ liệu (Data Flow) trong hệ thống
        for flow in self.flows:
            source = next(e for e in self.elements if e["id"] == flow["source"])
            target = next(e for e in self.elements if e["id"] == flow["target"])
            
            # 1. Spoofing
            if source["type"] == "External Actor":
                self.threats.append({
                    "category": "Spoofing",
                    "target": source["name"],
                    "description": f"Kẻ tấn công giả mạo danh tính {source['name']} khi gửi request đến {target['name']}.",
                    "severity": "HIGH",
                    "mitigation": "Triển khai Identity-Aware Proxy (IAP) và mã hóa Token xác thực."
                })
                
            # 2. Tampering
            if flow["protocol"] in ["HTTP", "Unencrypted"]:
                self.threats.append({
                    "category": "Tampering",
                    "target": f"Flow: {source['name']} -> {target['name']}",
                    "description": f"Dữ liệu {flow['data']} truyền qua giao thức {flow['protocol']} có thể bị chỉnh sửa trái phép.",
                    "severity": "CRITICAL",
                    "mitigation": "Ép buộc sử dụng HTTPS mã hóa SSL/TLS trên Cloud Load Balancing."
                })
                
            # 3. Repudiation
            if target["type"] in ["Server", "Database"]:
                self.threats.append({
                    "category": "Repudiation",
                    "target": target["name"],
                    "description": f"Các thao tác thay đổi dữ liệu tại {target['name']} không được ghi nhận danh tính chi tiết.",
                    "severity": "MEDIUM",
                    "mitigation": "Kích hoạt Cloud Audit Logs và đẩy log về Cloud Logging."
                })

            # 4. Information Disclosure
            if target["type"] == "Database" or "Credential" in flow["data"]:
                self.threats.append({
                    "category": "Information Disclosure",
                    "target": target["name"],
                    "description": f"Thông tin nhạy cảm {flow['data']} tại {target['name']} nguy cơ bị rò rỉ ra ngoài.",
                    "severity": "HIGH",
                    "mitigation": "Lưu trữ mật khẩu trong Secret Manager và mã hóa dữ liệu Cloud SQL tại chỗ."
                })

            # 5. Denial of Service
            if source["boundary"] != target["boundary"] and target["type"] == "Server":
                self.threats.append({
                    "category": "Denial of Service",
                    "target": target["name"],
                    "description": f"Lượng lớn request có thể gây quá tải và làm ngưng trệ {target['name']}.",
                    "severity": "HIGH",
                    "mitigation": "Cấu hình Cloud Armor Rate Limiting và MIG Autoscaling."
                })

            # 6. Elevation of Privilege
            if source["boundary"] == "Internal VPC" and target["type"] == "Database":
                self.threats.append({
                    "category": "Elevation of Privilege",
                    "target": target["name"],
                    "description": f"Service Account sở hữu quyền quá rộng để thao tác với {target['name']}.",
                    "severity": "CRITICAL",
                    "mitigation": "Áp dụng nguyên tắc Least Privilege qua Cloud IAM Custom Roles."
                })

    def export_report(self, filepath):
        report = {
            "model_name": self.name,
            "elements_count": len(self.elements),
            "flows_count": len(self.flows),
            "threats_count": len(self.threats),
            "stride_threats": self.threats
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Exported Threat Model report to file: {filepath}")

    def generate_dot(self, filepath):
        lines = ["digraph ThreatModel {", "  rankdir=LR;", "  node [shape=box, style=filled, fillcolor=white];"]
        for e in self.elements:
            color = "lightgrey" if e["boundary"] == "External" else "lightblue"
            lines.append(f'  "{e["id"]}" [label="{e["name"]}\\n({e["type"]})", fillcolor={color}];')
        for f in self.flows:
            lines.append(f'  "{f["source"]}" -> "{f["target"]}" [label="{f["protocol"]}: {f["data"]}"];')
        lines.append("}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Exported Graphviz DOT diagram to file: {filepath}")

if __name__ == "__main__":
    tm = ThreatModel("GCP Web Application Threat Model")
    
    # Định nghĩa các thành phần trong hệ thống
    tm.add_element("client", "Client Browser", "External Actor", "External")
    tm.add_element("clb", "Cloud Load Balancing", "Reverse Proxy", "Edge Boundary")
    tm.add_element("web", "Compute Engine Web Server", "Server", "Internal VPC")
    tm.add_element("db", "Cloud SQL PostgreSQL", "Database", "Internal VPC")
    tm.add_element("secret", "Secret Manager", "Database", "GCP Service Boundary")

    # Định nghĩa các luồng dữ liệu (Data Flow)
    tm.add_flow("client", "clb", "HTTPS", "HTTP Request & Auth Cookie")
    tm.add_flow("clb", "web", "HTTP", "Proxied Request")
    tm.add_flow("web", "secret", "gRPC", "DB Credentials Request")
    tm.add_flow("web", "db", "PostgreSQL TCP", "SQL Query & Sensitive Data")

    # Phân tích STRIDE và ghi kết quả ra file
    tm.analyze_stride()
    tm.export_report("stride_report.json")
    tm.generate_dot("architecture.dot")
