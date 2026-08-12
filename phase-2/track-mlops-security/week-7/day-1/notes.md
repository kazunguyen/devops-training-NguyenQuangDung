# MLOps - Argo Workflows (Train Pipeline)

## 1. Giới thiệu về Argo Workflows
Argo Workflows là một công cụ mã nguồn mở Kubernetes-native, được thiết kế để điều phối các workflows một cách song song. 
Trong lĩnh vực MLOps, Argo Workflows thường được sử dụng để tự động hóa toàn bộ quy trình từ Data Prep, Train, Eval cho đến Deploy.

## 2. Các khái niệm quan trọng
- **Workflow**: Là một Custom Resource Definition của Kubernetes định nghĩa một quy trình từ lúc bắt đầu tới khi kết thúc. Mỗi step trong workflow thực chất là một Pod độc lập.
- **Template**: Khối xây dựng cơ bản của một Workflow. Có nhiều loại template phổ biến:
  - Container template: Khởi chạy một Container cụ thể với Image chỉ định.
  - Script template: Chạy một đoạn mã (Python, Bash,...) trực tiếp.
  - DAG template: Xác định cấu trúc và sự phụ thuộc giữa các Task (Task nào chạy trước, Task nào chạy sau, Task nào chạy song song).
  - Steps template: Chạy các Task theo dạng mảng tuần tự.
- **Artifacts và Parameters**: Khả năng truyền dữ liệu giữa các Pod trong quá trình chạy. Parameters dành cho dữ liệu nhỏ (string, số), trong khi Artifacts dành cho dữ liệu lớn (file, folder, model weights) thường thông qua một kho lưu trữ như S3/MinIO.

## 3. Tại sao chọn Argo Workflows cho MLOps?
- **Container-native**: Mỗi step là một Container riêng biệt, đảm bảo tính cô lập và tái sử dụng môi trường.
- **Tối ưu chi phí và hiệu suất**: Khả năng scale ra hàng nghìn Pod song song, chạy xong tự động giải phóng tài nguyên.
- **Tích hợp sâu với Kubernetes**: Quản lý Pipeline bằng các file YAML tương tự như các Resource thông thường của Kubernetes, dễ dàng kết hợp với ArgoCD (GitOps).
