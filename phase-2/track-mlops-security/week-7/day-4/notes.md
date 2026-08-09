# Security - Triage Findings

## 1. Tổng quan về Triage
Trong an toàn thông tin, Triage là quy trình phân loại, đánh giá và ưu tiên xử lý các Findings. Khi các hệ thống giám sát liên tục (như Amazon GuardDuty, Macie, Inspector) phát hiện ra hàng ngàn sự kiện mỗi ngày, kỹ sư DevSecOps phải có khả năng đọc hiểu, phân tích rủi ro để quyết định xem cảnh báo nào là False Positive và cảnh báo nào là mối đe dọa thực sự cần Action Plan khẩn cấp.

## 2. Đi sâu vào chuẩn ASFF (AWS Security Finding Format)
ASFF (AWS Security Finding Format) là một chuẩn JSON schema khổng lồ do AWS quy định. Mục đích của ASFF là chuẩn hóa mọi dữ liệu cảnh báo từ hàng chục dịch vụ AWS và công cụ của bên thứ ba (như Splunk, Palo Alto, CrowdStrike) về một định dạng thống nhất duy nhất trên Security Hub. Điều này giúp loại bỏ hoàn toàn chi phí chuyển đổi dữ liệu khi phân tích.

Một bản ghi ASFF hoàn chỉnh chứa rất nhiều object, trong đó các thành phần trọng tâm nhất bao gồm:

### 2.1. Nhóm thông tin cốt lõi (Core Attributes)
- **Id**: Chuỗi định danh duy nhất của cảnh báo.
- **ProductArn**: ARN của dịch vụ sinh ra cảnh báo (ví dụ: `arn:aws:securityhub:us-east-1::product/aws/guardduty`).
- **GeneratorId**: ID của Rule hoặc kịch bản phát hiện (ví dụ: `aws-foundational-security-best-practices` hoặc mã signature của GuardDuty).
- **AwsAccountId**: ID của tài khoản AWS xảy ra sự cố.
- **CreatedAt / UpdatedAt**: Dấu thời gian khi cảnh báo được tạo ra và cập nhật lần cuối.

### 2.2. Nhóm thông tin phân loại (Classification & Status)
- **Title & Description**: Tiêu đề ngắn gọn và phần mô tả chi tiết giải thích tại sao sự kiện này lại là một rủi ro bảo mật.
- **Severity**: Đánh giá mức độ rủi ro, thường bao gồm Label (`INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) và điểm Normalized (từ 0 đến 100).
- **Types**: Phân loại taxonomy của rủi ro, ví dụ `Software and Configuration Checks/Vulnerabilities/CVE` hoặc `TTPs/Execution/Cryptocurrency Mining`.
- **Compliance**: Chứa thông tin về tiêu chuẩn tuân thủ bị vi phạm (như CIS AWS Foundations, PCI-DSS) và trạng thái tuân thủ (PASSED, FAILED, WARNING).
- **Workflow**: Trạng thái luồng xử lý của kỹ sư bảo mật (`NEW`, `NOTIFIED`, `RESOLVED`, `SUPPRESSED`).
- **RecordState**: Trạng thái vòng đời của bản ghi (`ACTIVE` hoặc `ARCHIVED`).

### 2.3. Nhóm thông tin tài nguyên (Resources)
Mảng `Resources` chứa danh sách các tài nguyên điện toán bị ảnh hưởng trực tiếp bởi sự kiện. Mỗi phần tử bao gồm:
- **Type**: Loại tài nguyên, ví dụ `AwsEc2Instance`, `AwsS3Bucket`, `AwsIamUser`.
- **Id**: ARN hoặc ID cụ thể của tài nguyên.
- **Details**: Cung cấp cấu hình chuyên sâu của tài nguyên tại thời điểm xảy ra sự cố (ví dụ: thông tin Image ID, VPC, Network Interfaces của một EC2 Instance).

### 2.4. Nhóm thông tin hành vi tấn công (Action & Detection)
Thường xuất hiện trong các cảnh báo từ GuardDuty, giúp mô tả chính xác kẻ tấn công đã làm gì:
- **Action**: Mô tả hành động mạng, như `NetworkConnectionAction` (kết nối inbound/outbound trái phép), `DnsRequestAction` (truy vấn tên miền độc hại), hoặc `AwsApiCallAction` (gọi API AWS bất thường). 
- Các Action này cung cấp chi tiết về IP nguồn (RemoteIpDetails), vị trí địa lý (Geolocation) và cổng kết nối (Port).
- **Detection**: Chứa thông tin về chuỗi sự kiện (Sequence), bao gồm Actor (kẻ tấn công), Endpoints và Signals.

### 2.5. Nhóm thông tin khắc phục (Remediation)
- **Remediation**: Cung cấp văn bản hướng dẫn (`Recommendation.Text`) và đường link (`Recommendation.Url`) dẫn đến tài liệu chuẩn để khắc phục lỗ hổng.

## 3. Quy trình Triage chuyên sâu
Để không bị ngợp trước lượng lớn ASFF JSON, kỹ sư thường tuân theo quy trình Triage 5 bước:

1. **Tiếp nhận & Sàng lọc**: Nhìn vào `Title` và `Severity.Label`. Ưu tiên xử lý các cảnh báo `CRITICAL` và `HIGH` trước.
2. **Khoanh vùng ảnh hưởng**: Phân tích mảng `Resources` để xem tài nguyên nào bị ảnh hưởng. Nếu đó là một EC2 Instance chứa Database quan trọng, mức độ nguy hiểm sẽ nhân lên nhiều lần.
3. **Điều tra nguyên nhân gốc rễ (Root Cause)**: 
   - Đọc kỹ `Description`.
   - Nếu là lỗi cấu hình (Configuration Check), kiểm tra phần `Compliance` để biết rule nào bị vi phạm.
   - Nếu là dấu hiệu bị hack (như Malware, Mining), kiểm tra phần `Action` để dò ngược IP và hành vi truy cập.
4. **Xác minh & Phân loại cuối cùng**: Kết luận đây là False Positive (ví dụ: máy chủ quét lỗ hổng nội bộ đang hoạt động) hay True Positive (một cuộc tấn công thật sự). Chuyển `Workflow` sang trạng thái tương ứng.
5. **Thực thi Action Plan**: Dựa vào `Remediation` và chuyên môn, đưa ra các bước sửa lỗi triệt để (như cấu hình lại IAM Policy, chặn Security Group, hoặc Terminate máy chủ).
