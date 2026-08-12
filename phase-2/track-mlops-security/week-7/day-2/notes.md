# MLOps - Event Trigger (Argo Events)

## 1. Giới thiệu tổng quan về Argo Events
Argo Events là một framework event-driven dành riêng cho hệ sinh thái Kubernetes, cho phép quản lý sự kiện và tự động hóa các phụ thuộc (Dependency Manager).
Trọng tâm của Argo Events là giúp tự động hóa hoàn toàn các tiến trình bằng cách lắng nghe sự kiện từ hơn 20 nguồn khác nhau (AWS SQS, S3, GitHub, Webhook, Kafka, v.v.), sau đó đưa ra quyết định dựa trên logic và thực thi các hành động tương ứng.

Trong kiến trúc MLOps, Argo Events là thành phần trung gian (Middleware) kết nối giữa các công cụ quản lý dữ liệu (như DVC, S3) và các công cụ thực thi (Argo Workflows, KServe). Bất kỳ thay đổi nào từ phía dữ liệu hoặc model registry đều có thể được tự động nhận diện và đẩy thành một Pipeline huấn luyện hoặc triển khai mới mà không cần sự can thiệp thủ công.

## 2. Kiến trúc 4 thành phần lõi của Argo Events
Theo tài liệu chính thức, kiến trúc của Argo Events được chia làm 4 Resource type riêng biệt:

### 2.1. EventSource (Nguồn phát sự kiện)
- **Chức năng**: EventSource chịu trách nhiệm giao tiếp với hệ thống bên ngoài để "bắt" các sự kiện.
- **Hoạt động**: Mỗi EventSource khi deploy sẽ sinh ra một Pod chạy dưới dạng Deployment trên Kubernetes. Nó lắng nghe hoặc pull sự kiện, sau đó biến đổi dữ liệu nhận được thành chuẩn **CloudEvents** và đẩy vào EventBus.
- **Các loại phổ biến trong MLOps**: S3/MinIO (khi có file dataset mới), Webhook (khi DVC push data xong gọi API), GitHub/GitLab (khi code mới được merge).

### 2.2. EventBus (Trục giao tiếp sự kiện)
- **Chức năng**: Là hệ thống Message Broker trung tâm, nhận sự kiện từ tất cả các EventSource và phân phối (publish/subscribe) tới các Sensor tương ứng.
- **Engine**: Argo Events hỗ trợ 2 loại EventBus:
  - `Native`: Sử dụng NATS mặc định, phù hợp cho môi trường Lab, Test, quy mô nhỏ.
  - `JetStream`: Sử dụng NATS JetStream, có khả năng lưu trữ liên tục (Persistence), đảm bảo không mất mát sự kiện (At-least-once delivery) và hỗ trợ High Availability cho Production.

### 2.3. Sensor (Bộ xử lý logic)
- **Chức năng**: Sensor là "bộ não" của Argo Events. Nó đăng ký (subscribe) lắng nghe các sự kiện từ EventBus.
- **Dependencies & Logic**: Một Sensor có thể định nghĩa nhiều phụ thuộc (Dependencies). Ta có thể thiết lập các biểu thức logic (ví dụ: `Event A AND (Event B OR Event C)`) để quyết định xem sự kiện tổng hợp đã đủ điều kiện kích hoạt hay chưa.
- **Filters**: Sensor cung cấp khả năng lọc sự kiện (Data filters, Time filters). Ví dụ: Chỉ kích hoạt nếu payload của Webhook có chứa trường `{"model": "resnet50"}`.
- Mỗi Sensor cũng chạy như một Pod độc lập trên Cluster.

### 2.4. Trigger (Hành động phản hồi)
- **Chức năng**: Nằm bên trong cấu hình của Sensor. Khi các điều kiện (Dependencies/Filters) đã thỏa mãn, Sensor sẽ thực thi các Trigger này.
- **Khả năng**:
  - `Argo Workflow`: Sinh ra một Workflow mới (ứng dụng chính trong MLOps).
  - `Kubernetes Objects`: Tạo, cập nhật, xóa bất kỳ Resource nào (Pod, Job, Deployment).
  - `HTTP Requests`: Bắn API ra bên ngoài (ví dụ gọi sang KServe).
  - `Slack/Teams`: Gửi thông báo tự động cho kỹ sư.

## 3. Ứng dụng thực tế: MLOps Automation Workflow
Kịch bản phổ biến nhất khi tích hợp DVC và Argo Events trong MLOps:
1. **Trigger từ Client**: Kỹ sư Dữ liệu chạy lệnh `dvc push` đẩy Dataset mới lên S3. Sau đó, CI/CD pipeline hoặc một script hook nội bộ bắn HTTP POST request chứa metadata đến địa chỉ IP của Webhook EventSource.
2. **Tiếp nhận (Ingestion)**: Pod EventSource nhận payload, bọc nó vào cấu trúc CloudEvents và đẩy vào luồng (Topic) của EventBus (NATS).
3. **Phân tích (Evaluation)**: Sensor lắng nghe Topic này. Nó bóc tách payload, kiểm tra xem trường `project_name` có đúng là `fraud-detection` hay không (sử dụng Filter).
4. **Thực thi (Action)**: Nếu khớp, Sensor lấy các tham số từ payload (ví dụ: đường dẫn S3 của Dataset) truyền vào dưới dạng `Parameters` của một `Argo Workflow` template. Sensor tự động tạo Workflow này.
5. **Huấn luyện (Training)**: Argo Workflows nhận lệnh, kéo Dataset từ S3 về, chạy script huấn luyện mô hình và lưu Model Registry.

Nhờ cơ chế chia tách (Decoupling) giữa EventSource và Sensor, ta có thể dễ dàng mở rộng hệ thống (thêm nhiều nguồn trigger khác nhau cùng gọi đến 1 Pipeline, hoặc 1 nguồn trigger gọi ra nhiều Pipeline song song) mà không làm phá vỡ kiến trúc cũ.
