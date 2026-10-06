# Philobiblus

Philobiblus là ứng dụng quản lý tiến độ đọc, chia sẻ sách và đề xuất sách.
Phiên bản được mô tả trong tài liệu này là phiên bản đang được triển khai trên
Google Cloud, với workload chạy trong GKE Autopilot. Các cấu hình Docker Compose,
k3d và Prometheus/Grafana trong repository chỉ phục vụ phát triển hoặc kiểm thử
local; chúng không đại diện cho môi trường triển khai cuối cùng.

## Trạng thái triển khai cuối cùng

| Thành phần | Trạng thái và vai trò |
|---|---|
| Frontend | React/Vite được build và phát hành trên GitHub Pages. Frontend không chạy thành Pod trong GKE. |
| Cloud Run proxy | Service philobiblus-dev-proxy làm HTTPS entrypoint/proxy công khai tới Gateway của GKE. |
| GKE | Cluster Autopilot philobiblus-dev-gke tại asia-southeast1. |
| Namespace philobiblus | Backend FastAPI, recommendation service độc lập, Redis, Gateway/HTTPRoute, ServiceAccount, NetworkPolicy và các ConfigMap phục vụ model release. |
| Namespace philobiblus-mlops | MLflow Deployment/Service và CronJob philobiblus-retrain cho quy trình retrain, đánh giá và phát hành model. |
| Cơ sở dữ liệu | Cloud SQL for PostgreSQL; backend và workload MLOps kết nối qua Cloud SQL Auth Proxy. PostgreSQL không chạy trong GKE production. |
| Model/artifact | GCS bucket MLOps lưu snapshot, model release và artifact MLflow. Recommendation service chỉ đọc vùng model được cấp quyền. |
| Cache và giới hạn tải | Redis lưu catalog/rate-limit; recommendation request có load shedding dùng chung để tránh làm nghẽn backend và Cloud SQL. |
| Observability | Cloud Logging, Cloud Monitoring và Managed Service for Prometheus/GKE PodMonitoring. Không dùng Grafana/Prometheus local trong kiến trúc production. |
| Secret và quyền | Secret Manager + GKE Secret Manager add-on/CSI, Workload Identity và ServiceAccount tách theo workload. |

Frontend người dùng truy cập tại:
https://kazunguyen.github.io/philobiblus/

Mã nguồn nằm tại repository GitHub của dự án:
https://github.com/kazunguyen/philobiblus

## Kiến trúc request và dữ liệu

~~~text
Browser
  │
  └── GitHub Pages (React/Vite)
        │ gọi API
        ▼
Cloud Run proxy (philobiblus-dev-proxy)
        │
        ▼
GKE Gateway + Cloud Armor
        │
        └── namespace philobiblus
              ├── Backend Deployment (2 replica, HPA 2–6)
              │     ├── Cloud SQL PostgreSQL qua Auth Proxy
              │     ├── Redis cache/rate-limit
              │     └── Recommendation Deployment (1 replica)
              │
              └── namespace philobiblus-mlops
                    ├── MLflow Deployment (1 replica)
                    └── philobiblus-retrain CronJob

GCS MLOps bucket ──► model-fetcher/initContainer ──► Recommendation Pod
CronJob ──► MLflow (run/metric/model version)
CronJob ──► GCS (snapshot/model release)
Workloads ──► Cloud Logging/Monitoring/Managed Prometheus
~~~

Luồng request người dùng chỉ đi qua namespace philobiblus. Namespace
philobiblus-mlops không nằm trên đường phục vụ request; nó tạo và quản lý model
được recommendation service sử dụng.

## Cấu trúc mã nguồn chính

~~~text
backend/                         FastAPI, SQLAlchemy, JWT, Redis và API nghiệp vụ
frontend/                        React/Vite và các trang giao diện
ml/recommendation-service/       API recommendation và TF-IDF recommender
ml/training/                     pipeline snapshot, train, evaluate, promote
ml/model-fetcher/                tải model release từ GCS
ml/mlflow/                       image MLflow server
kubernetes/helm/philobiblus/    Helm chart workload ứng dụng
kubernetes/helm/philobiblus-mlops/
                                  Helm chart MLflow và retrain CronJob
infrastructure/terraform/        Terraform cho nền tảng GKE, app và MLOps
proxy/                            image cấu hình Cloud Run proxy
monitoring/                       cấu hình phục vụ môi trường local, không phải GKE production
docs/                             báo cáo, runbook và bằng chứng triển khai
screenshots/                      ảnh minh chứng giao diện và Google Cloud Console
~~~

## Các workload Kubernetes trên GKE

### Namespace philobiblus

- **Backend Deployment/Service**: xử lý xác thực, sách, tiến độ đọc, chia sẻ,
  bình luận và gọi recommendation service khi cần.
- **Recommendation Deployment/Service**: chạy FastAPI và model TF-IDF độc lập;
  model-fetcher tải model release đã được phát hành từ GCS.
- **Redis Deployment/Service**: cache catalog trong thời gian ngắn và lưu state
  cho rate limit/load shedding. Backend có đường lui khi Redis tạm thời lỗi.
- **Gateway và HTTPRoute**: nhận traffic từ proxy, sau đó chuyển vào Service
  backend; frontend được phát hành riêng nên chart production không bật frontend
  Deployment.
- **SecretProviderClass/ServiceAccount/NetworkPolicy/ConfigMap**: cấp secret từ
  Secret Manager, giới hạn quyền Pod và lưu model release hiện hành.

Backend production được cấu hình pool cơ sở dữ liệu nhỏ, timeout hữu hạn, cache
catalog 30 giây và giới hạn recommendation theo cửa sổ 10 giây. Khi recommendation
service quá tải hoặc bị tắt bằng biến vận hành, API trả trạng thái unavailable
thay vì làm hỏng toàn bộ trang sách.

### Namespace philobiblus-mlops

- **MLflow Deployment/Service**: nhận run, parameter, metric, artifact và model
  version; metadata nằm trong schema MLflow của Cloud SQL, artifact nằm trên GCS.
- **philobiblus-retrain CronJob**: lấy snapshot catalog, huấn luyện, đánh giá,
  ghi run vào MLflow và chỉ phát hành model khi quality gate hợp lệ.
- **Trainer ServiceAccount, Role và RoleBinding**: chỉ cho trainer đọc/patch
  Deployment recommendation và ConfigMap model-release trong phạm vi cần thiết.
- **SecretProviderClass và Cloud SQL Auth Proxy**: cung cấp database URI mà
  không đưa credential vào Helm values hoặc image.

CronJob dùng lịch 0 20 * * * (03:00 ngày hôm sau theo giờ Việt Nam) khi được
bật. Job sinh thủ công có hậu tố manual; chúng là lần chạy kiểm tra riêng,
không phải một CronJob khác.

## Quy trình build và triển khai

### 1. Build image

Backend, recommendation service, model-fetcher, trainer, MLflow và proxy đều
được đóng gói bằng Docker. Image production nên được tham chiếu bằng digest
SHA-256 thay vì tag thay đổi.

Workflow MLOps build image trainer/model-fetcher/MLflow, đẩy image vào Artifact
Registry, ký image bằng Cosign/OIDC rồi truyền digest bất biến vào Helm release.
Các giá trị mẫu trong chart không chứa secret.

### 2. Phát hành frontend

Workflow frontend/.github/workflows/deploy-pages.yaml build React/Vite và
đưa static site lên GitHub Pages. Địa chỉ backend được truyền lúc build qua
VITE_API_URL; không dùng localhost trong bản phát hành công khai.

### 3. Provision hạ tầng bằng Terraform

Các module chính nằm dưới infrastructure/terraform/:

- **gke-platform**: cluster Autopilot, Gateway address, Certificate Manager và
  các thành phần nền tảng;
- **gke-app**: namespace ứng dụng, quota/limit range, Workload Identity, Helm
  release backend/recommendation/Redis và liên kết Cloud SQL;
- **gke-mlops**: GCS bucket MLOps, ServiceAccount, IAM theo prefix, Secret Manager
  access và quyền cho MLflow/trainer;
- **https-proxy**: tài nguyên proxy công khai nếu cần quản lý bằng Terraform.

Terraform state được lưu trong GCS backend. Các giá trị thật như project ID,
state bucket, database URI, secret ID và image digest phải được truyền qua biến
môi trường hoặc protected GitHub Environment; không commit file *.tfvars
chứa credential.

### 4. Deploy Helm

Chart ứng dụng:

~~~bash
helm upgrade --install philobiblus \
  kubernetes/helm/philobiblus \
  --namespace philobiblus \
  --create-namespace \
  --wait --wait-for-jobs --timeout 20m
~~~

Chart MLOps:

~~~bash
helm upgrade --install philobiblus-mlops \
  kubernetes/helm/philobiblus-mlops \
  --namespace philobiblus-mlops \
  --create-namespace \
  --wait --timeout 10m
~~~

Trong triển khai thật, các lệnh trên được workflow gọi với project, Cloud SQL
connection name, secret ID, bucket và image digest từ protected variables.
Không dùng lệnh trên với values local để thay thế release GKE production.

## Kiểm tra trạng thái GKE

~~~bash
gcloud container clusters get-credentials philobiblus-dev-gke \
  --region asia-southeast1

kubectl get deployments,pods,services -n philobiblus
kubectl get deployments,pods,services,cronjobs -n philobiblus-mlops
kubectl get gateway,httproute -n philobiblus
~~~

Các trạng thái cần kiểm tra sau triển khai:

- backend đạt số replica tối thiểu và HPA có metric CPU;
- recommendation Deployment có Pod Ready;
- Redis và MLflow có readiness probe thành công;
- Cloud SQL Auth Proxy sidecar kết nối được database;
- CronJob không có Job thất bại tồn đọng ngoài giới hạn lịch sử;
- Gateway/HTTPRoute có địa chỉ và proxy trả health 200;
- PodMonitoring xuất hiện trong Cloud Monitoring.

Xem log mà không in secret:

~~~bash
kubectl logs -n philobiblus deployment/philobiblus-backend --tail=200
kubectl logs -n philobiblus deployment/philobiblus-recommendation --tail=200
kubectl logs -n philobiblus-mlops deployment/mlflow --tail=200
kubectl get jobs -n philobiblus-mlops
~~~

## Observability trên Google Cloud

GKE production dùng Cloud Logging, Cloud Monitoring và Managed Service for
Prometheus. Metric ứng dụng được khai báo bằng PodMonitoring; log, CPU, memory,
restart, Gateway và Cloud SQL được xem từ Google Cloud Console. Các dashboard
Prometheus/Grafana trong thư mục monitoring/ chỉ dành cho môi trường local và
không nên được dùng làm bằng chứng cho cluster GKE.

Khi điều tra lỗi 5xx hoặc recommendation unavailable, xem theo thứ tự:

1. Cloud Run proxy và Gateway/Cloud Armor;
2. log backend và trạng thái HPA;
3. Redis và recommendation Deployment;
4. Cloud SQL connection/CPU/connection count;
5. MLflow, CronJob, GCS model release và model version.

## Bảo mật và vận hành

- Secret được lưu ở Secret Manager, không đặt trong source, image hoặc GitHub
  workflow log.
- Workload Identity cấp quyền GCP riêng cho backend, recommendation, seed,
  trainer và MLflow.
- NetworkPolicy giới hạn traffic giữa namespace ứng dụng, MLOps và hệ thống
  Managed Prometheus.
- Container chạy non-root, hạn chế capability, dùng filesystem read-only ở các
  workload phù hợp và có readiness/liveness/startup probe.
- Image production được pin bằng digest; pipeline MLOps ký image trước khi
  deploy.
- Cloud Armor được quản lý ở lớp Gateway; khi rule ở preview cần xem log và
  false positive trước khi chuyển sang enforce.

## Kiểm thử

Kiểm thử mã nguồn được thực hiện riêng cho backend, recommendation/ML và
frontend build. Helm lint/template kiểm tra manifest trước triển khai; GKE
Console và kubectl kiểm tra rollout, Pod readiness, CronJob và resource cloud.
Load test phải được đọc cùng điều kiện đo: mốc 150 người dùng đồng thời trước
đây được đo khi recommendation service tắt, nên không đại diện cho toàn bộ luồng
production khi recommendation hoạt động. Khi demo, ưu tiên theo dõi Cloud
Monitoring và giữ ngưỡng load shedding để bảo vệ Cloud SQL.

## Phân biệt môi trường

Các thư mục sau vẫn được giữ để phục vụ học tập và phát triển, nhưng không phải
trạng thái production được mô tả ở trên:

- docker-compose.yaml, nginx/: chạy toàn bộ stack local;
- kubernetes/manifests/: manifest Kubernetes nguyên bản;
- scripts/local-kubernetes/: k3d/k3s và Prometheus/Grafana local;
- monitoring/: values/dashboard cho stack monitoring local.

Khi cập nhật hệ thống, hãy cập nhật đồng thời Terraform, Helm values, workflow
triển khai và tài liệu bằng chứng để README không mô tả nhầm một môi trường
khác với cluster GKE đang vận hành.
