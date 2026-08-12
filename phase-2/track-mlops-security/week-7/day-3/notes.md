# Security - Cloud Security (AWS)

## 1. Tổng quan về bảo mật đám mây
Trong môi trường Cloud, bảo mật là trách nhiệm chia sẻ giữa nhà cung cấp (AWS) và khách hàng. Trọng tâm của bảo mật DevSecOps trên AWS là tự động hóa việc giám sát, phát hiện mối đe dọa và đánh giá cấu hình dựa trên các tiêu chuẩn quốc tế. Bộ 3 dịch vụ được sử dụng phổ biến nhất để thực hiện mục tiêu này là Amazon GuardDuty, AWS Security Hub và IAM Access Analyzer.

## 2. Amazon GuardDuty
Amazon GuardDuty là dịch vụ phát hiện mối đe dọa liên tục, sử dụng Machine Learning và Threat Intelligence để bảo vệ tài khoản và Workload trên AWS.
- **Nguồn dữ liệu phân tích**: GuardDuty âm thầm thu thập và phân tích hàng tỷ sự kiện từ AWS CloudTrail, VPC Flow Logs và DNS Logs mà không cần cài đặt thêm Agent hay ảnh hưởng đến hiệu suất hệ thống.
- **Khả năng phát hiện**: 
  - Khai thác tiền ảo độc hại.
  - Truy cập trái phép từ các IP độc hại.
  - Hành vi bất thường (như một tài khoản IAM đột ngột tạo hàng loạt Instance ở Region lạ).

## 3. AWS Security Hub
AWS Security Hub đóng vai trò là giải pháp quản lý thế trận bảo mật đám mây. Nó giúp tổ chức có một cái nhìn toàn cảnh về trạng thái bảo mật của toàn bộ tài khoản AWS.
- **Tổng hợp dữ liệu**: Thu thập các cảnh báo từ nhiều dịch vụ khác nhau như GuardDuty, Amazon Inspector, Amazon Macie và đưa về một định dạng chuẩn chung là AWS Finding Format.
- **Kiểm tra tự động**: Tự động đánh giá cấu hình tài khoản liên tục dựa trên các tiêu chuẩn bảo mật khắt khe như CIS AWS Foundations Benchmark hoặc PCI DSS. Nhờ đó, nhanh chóng phát hiện các lỗi cấu hình như S3 Bucket đang public hay IAM User không bật MFA.

## 4. IAM Access Analyzer
Quản lý danh tính và quyền truy cập là phòng tuyến đầu tiên. IAM Access Analyzer là công cụ giúp phân tích xem có tài nguyên nào đang bị cấp quyền truy cập thừa ra bên ngoài hay không.
- **Công nghệ áp dụng**: Sử dụng mô hình logic toán học tự động để phân tích toàn bộ các Policy.
- **Phát hiện rủi ro**: Quét tự động để tìm ra các S3 Bucket, IAM Role, KMS Key hoặc Lambda Function đang được cấp quyền cho một tài khoản AWS ngoài tổ chức hoặc cấp quyền public trên Internet. Điều này giúp ngăn chặn các cuộc tấn công rò rỉ dữ liệu.
