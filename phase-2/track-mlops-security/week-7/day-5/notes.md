# Security - Threat Modeling

## 1. Giới thiệu về Threat Modeling
Threat Modeling là quá trình nhận diện, giao tiếp và phân tích các Threat cũng như Mitigation trong bối cảnh bảo vệ tài sản của hệ thống. 

Một Threat Model là bản biểu diễn có cấu trúc của tất cả thông tin ảnh hưởng đến Security của Application. Về cơ bản, nó là góc nhìn về Application và môi trường xung quanh dưới lăng kính Security.

Threat Modeling được áp dụng cho nhiều đối tượng, bao gồm Software, Application, System, Network, IoT và các quy trình kinh doanh.

## 2. Các thành phần quan trọng của Threat Model
Một Threat Model tiêu biểu bao gồm:
- **Mô tả đối tượng**: Xác định rõ System hoặc Application cần được mô hình hóa.
- **Giả định**: Các yếu tố được mặc định là đúng tại thời điểm hiện tại, có thể đánh giá lại trong tương lai khi bối cảnh thay đổi.
- **Threat**: Danh sách các mối đe dọa tiềm ẩn có thể tấn công vào System.
- **Action Plan**: Các hành động cụ thể để giảm thiểu từng Threat.
- **Xác thực**: Phương pháp xác nhận tính chính xác của mô hình và kiểm tra hiệu quả của các Action Plan đã triển khai.

## 3. Threat Modeling trong Lifecycle
Threat Modeling mang lại hiệu quả cao nhất khi được thực hiện liên tục trong suốt Lifecycle của Software. 

Quy trình này áp dụng chung cho nhiều mức độ trừu tượng, với mức độ chi tiết tăng dần theo tiến độ dự án. Một Threat Model tổng quan thường được thiết lập sớm ở giai đoạn lập kế hoạch, sau đó liên tục tinh chỉnh. Khi System mở rộng, các Attack Vector mới sẽ xuất hiện. Quá trình Threat Modeling liên tục giúp chẩn đoán và giải quyết kịp thời các rủi ro mới.

Threat Model cần được cập nhật sau các sự kiện sau:
- Phát hành tính năng mới.
- Xảy ra Security Incident.
- Thay đổi cấu trúc Infrastructure.

## 4. Four Question Framework
Một Threat có khả năng trở thành hiện thực khi hội tụ đủ xác suất xảy ra và Impact đối với tổ chức để tạo thành một Risk đáng kể. Quá trình Threat Modeling thường được triển khai thông qua Four Question Framework:

- **What are we working on?**: Xác định Scope đang làm việc, từ một Sprint nhỏ đến toàn bộ System.
- **What can go wrong?**: Xác định các kịch bản rủi ro, thông qua Brainstorming hoặc sử dụng các cấu trúc phân tích như STRIDE, Kill Chains, Attack Trees.
- **What are we going to do about it?**: Quyết định phương án xử lý từng Threat, bao gồm việc triển khai Mitigation hoặc áp dụng các chiến lược chấp nhận, chuyển giao, loại bỏ Risk.
- **Did we do a good job?**: Đánh giá lại toàn bộ công việc xử lý để đảm bảo System đạt đủ mức độ an toàn.

## 5. Lợi ích của Threat Modeling
Khi thực hiện đúng, Threat Modeling cung cấp cái nhìn rõ ràng xuyên suốt dự án, làm cơ sở hợp lý cho các nỗ lực Security. Quy trình này cho phép đưa ra các quyết định Security dựa trên dữ liệu và bối cảnh thực tế. 

Quy trình Threat Modeling cũng tạo ra một Assurance Argument dùng để giải thích và bảo vệ tính an toàn của Application, bắt đầu bằng các tuyên bố cấp cao và chứng minh thông qua bằng chứng cụ thể.
