# Giáo trình tự học Track MLOps / Security (Week 5 - Week 9)

Tài liệu này định hướng lộ trình chuyên sâu cho **Track C (MLOps & Security)**, tuân thủ chặt chẽ thứ tự các chủ đề trong lộ trình cốt lõi. Giáo trình được chia theo từng ngày để bạn phân bổ thời gian hợp lý giữa hai khía cạnh MLOps và Security.

---

## 🗺️ Hướng đi tổng quan (Roadmap Week 5 - Week 9)
- **Week 5**: MLflow, DVC & CI/CD Pipeline (SAST, DAST, SCA)
- **Week 6**: KServe, Canary Deploy & K8s Hardening (PSA, OPA Gatekeeper)
- **Week 7**: Argo Workflows & Cloud Security (AWS, STRIDE)
- **Week 8 & 9**: Capstone Project

---

## 🛡️ Week 5: Data Versioning, Experiment Tracking & Secure Pipeline
*Kết hợp việc quản lý vòng đời Machine Learning (MLOps) và tích hợp các công cụ kiểm tra bảo mật vào pipeline (Security).*

### Day 1: MLOps - MLflow Tracking Server
*Cài đặt server tracking và ghi log các thực nghiệm model.*
- **Tổng quan MLflow**: [MLflow Docs](https://mlflow.org/docs/latest/index.html)
- **Log Experiment (sklearn / pytorch)**: [Tracking API](https://mlflow.org/docs/latest/tracking.html)

### Day 2: MLOps - Data Versioning với DVC
*Quản lý phiên bản cho dataset.*
- **Tổng quan DVC**: [DVC Docs](https://dvc.org/doc)
- **DVC Get Started**: [Data Versioning](https://dvc.org/doc/start/data-management)

### Day 3: Security - SCA & SAST
*Quét lỗ hổng mã nguồn và thư viện.*
- **SCA với Snyk / Grype**: Cấu hình quét dependencies.
- **SAST với Semgrep**: Tích hợp Semgrep vào pipeline để quét source code tĩnh.

### Day 4: Security - DAST & Gate Fail
*Kiểm thử động và thiết lập các ngưỡng chặn (Gate) trong CI/CD.*
- **DAST với OWASP ZAP**: Cấu hình quét ứng dụng đang chạy.
- **Đo Gate Fail**: Cấu hình pipeline thất bại (fail) nếu phát hiện lỗ hổng mức HIGH/CRITICAL CVE.

### Day 5: Mini Lab (Tích hợp)
*Thực hành tổng hợp kỹ năng của tuần.*
- **MLOps Lab**: Huấn luyện (train) 3 biến thể (variant) của mô hình và so sánh các metrics trên MLflow.
- **Security Lab**: Đẩy source code chứa lỗi lên để kiểm chứng hệ thống Pipeline chặn thành công.

---

## 🔐 Week 6: Model Serving & Kubernetes Hardening
*Triển khai mô hình AI trên Kubernetes (MLOps) và áp dụng các tiêu chuẩn bảo mật cho Cluster (Security).*

### Day 1: MLOps - Model Serving với KServe
*Đưa mô hình vào môi trường production bằng KServe.*
- **KServe Overview**: [KServe GitHub](https://github.com/kserve/kserve)
- **Deploy Model**: Triển khai một mô hình đơn giản lên K8s.

### Day 2: MLOps - Canary Deployment & Load Testing
*Phát hành phiên bản mới an toàn và đo đạc hiệu năng.*
- **Canary Deploy**: Triển khai 2 phiên bản model cùng lúc (vd: 90% traffic bản cũ, 10% bản mới).
- **Load Testing**: Đo Latency và RPS bằng `vegeta` hoặc `locust`.

### Day 3: Security - Pod Security Admission (PSA)
*Kiểm soát quyền chạy của Pod trên Kubernetes.*
- **PSA Standards**: [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- **Cấu hình**: Áp dụng chuẩn `baseline` và `restricted` cho các namespace.

### Day 4: Security - OPA Gatekeeper
*Xây dựng và áp dụng Policy as Code.*
- **Cài đặt Gatekeeper**: [Gatekeeper Docs](https://open-policy-agent.github.io/gatekeeper/website/docs/)
- **Viết Policy**: Từ chối privileged pod, yêu cầu `runAsNonRoot`, và cấm sử dụng tag `:latest`.

### Day 5: Security - Image Scanning & CI/CD Integration
*Bảo vệ chuỗi cung ứng phần mềm.*
- **Trivy & Cosign**: Tích hợp Trivy (quét image) và Cosign (ký số) vào CI.
- **Gate ArgoCD**: Dùng admission controller chặn các deployment không có chữ ký an toàn.

---

## ☁️ Week 7: Tự động hóa Pipeline & Cloud Security
*Xây dựng chuỗi tự động hoàn chỉnh và bảo vệ hệ thống trên Cloud.*

### Day 1: MLOps - Argo Workflows (Train Pipeline)
*Tạo DAG Workflow cho quy trình ML.*
- **Argo Workflows**: [Documentation](https://argoproj.github.io/argo-workflows/)
- **Pipeline Setup**: Build luồng tự động: Data prep → Train → Eval → Deploy.

### Day 2: MLOps - Event Trigger
*Kích hoạt Pipeline tự động.*
- **Argo Events**: [Documentation](https://argoproj.github.io/argo-events/)
- Cấu hình Event để kích hoạt Argo Workflows khi có thay đổi từ DVC pipeline.

### Day 3: Security - Cloud Security (AWS)
*Theo dõi và phát hiện các rủi ro bảo mật trên Cloud.*
- **Amazon GuardDuty**: [Documentation](https://docs.aws.amazon.com/guardduty/)
- **AWS Security Hub**: [Documentation](https://docs.aws.amazon.com/securityhub/)
- **IAM Access Analyzer**: [Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
- Bật và cấu hình các dịch vụ trên để giám sát rủi ro bảo mật trên một AWS account.

### Day 4: Security - Triage Findings
*Xử lý sự cố bảo mật.*
- **AWS Finding Format (ASFF)**: [Documentation](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html)
- Phân tích và triage (phân loại) 5 finding mẫu từ SecurityHub/GuardDuty.
- Viết action plan để xử lý các finding này.

### Day 5: Security - Threat Modeling
*Nhận diện rủi ro qua mô hình STRIDE.*
- **OWASP Threat Modeling**: [Documentation](https://owasp.org/www-community/Threat_Modeling)
- Phân tích và tạo Threat Model cho 1 hệ thống web app theo chuẩn STRIDE.

---

## 🎓 Week 8–9: Capstone Project
*Dành ra 2 tuần để thực hiện bài tập lớn (chọn 1 trong 2 đề theo hướng chuyên sâu).*

### Lựa chọn 1: MLOps — "End-to-end model lifecycle platform"
- **Data & Model Repo**: DVC (S3 backend) + MLflow (Postgres/S3) + Training script.
- **Inference Service**: KServe trên K8s load model từ MLflow.
- **Tự động hoá CI/CD**: Push dataset mới -> Trigger Argo Workflows -> Train & Log metric -> Auto promote (nếu tốt hơn baseline) -> KServe Canary rollout.
- **Monitoring**: Giám sát latency, RPS, phân phối dự đoán (data drift).

### Lựa chọn 2: Security — "DevSecOps end-to-end cho 1 app web"
- **Pre-commit**: Cài đặt gitleaks và secret scan.
- **CI**: Semgrep (SAST), Snyk/Grype (SCA), Trivy, Syft (SBOM), Cosign (Image sign).
- **CD k8s**: Cấu hình OPA Gatekeeper policy cứng, Network Policy deny-all, PSA restricted.
- **Runtime**: Falco ([Documentation](https://falco.org/docs/)) (phát hiện shell trong container) + Loki ([Documentation](https://grafana.com/docs/loki/latest/)) (Lưu audit log).
- **Cloud & Design**: Thiết lập AWS baseline (GuardDuty, SecHub) và Threat model 1 trang (STRIDE).
