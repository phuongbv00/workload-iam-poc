# Tìm hiểu và Triển khai Mẫu Workload IAM

## I. Giới thiệu

### Bối cảnh và động lực

- Trong hệ thống hiện đại, các **workload** như microservice, job scheduler, serverless function, container và agent
  phần mềm ngày càng phổ biến.
- Những workload này cần **truy cập vào tài nguyên** mà không có sự tham gia trực tiếp của con người.
- Kiểm soát danh tính và quyền truy cập cho workload là một yêu cầu bảo mật quan trọng, đặc biệt trong môi trường phân
  tán hoặc zero-trust.
- **Workload IAM** ra đời nhằm cung cấp danh tính và kiểm soát truy cập chuyên biệt cho các thực thể phi nhân.

### Mục tiêu của đề tài

- Tìm hiểu các khái niệm cốt lõi của Workload Identity and Access Management.
- Triển khai một kiến trúc mẫu áp dụng Workload IAM cho một LLM agent.
- Áp dụng các tiêu chuẩn công nghệ mới nhất như SPIFFE/SPIRE, OPA, mTLS, Envoy, FastAPI.

## II. Các khái niệm cơ bản

### 1. Workload là gì?

- Định nghĩa workload trong ngữ cảnh hệ thống phần mềm.
- Các loại workload phổ biến: container, microservice, function, agent, VM, v.v.

### 2. IAM cho workload

- Phân biệt IAM cho người dùng và workload.
- Vấn đề của các giải pháp cũ: hard-coded secrets, credential rotation, human-centric auth.
- Yêu cầu chính: non-human identity, temporary credential, dynamic trust, auditability.

### 3. Danh tính workload hiện đại

- **SPIFFE/SPIRE**: chuẩn mở cung cấp danh tính cho workload.
    - SPIFFE ID, SVID (SPIFFE Verifiable Identity Document).
    - Cách SPIRE cấp phát và xác minh danh tính.
    - x509/JWT SVID, mTLS.
- So sánh với OIDC, JWT, client secret truyền thống.

### 4. Kiểm soát truy cập cho workload

- Authorization theo role (RBAC), attribute (ABAC), policy (PBAC).
- Giới thiệu **Open Policy Agent (OPA)**.
- Cách OPA đánh giá yêu cầu dựa trên input (identity, method, resource...).
- Khái niệm **Zero Trust for Workload**.

### 5. Proxy-based IAM enforcement

- Giới thiệu **Envoy Proxy** làm lớp trung gian.
- Vai trò của Envoy: mTLS, SPIFFE ID forwarding, policy enforcement via OPA.
- Kiến trúc sidecar hoặc edge proxy trong kiểm soát IAM.

## III. Use Case: LLM Agent truy cập REST API

### 1. Mô tả hệ thống mẫu

- Một **LLM agent (Python)** thực hiện truy cập tới một **REST API (FastAPI)** để quản lý dữ liệu người dùng.
- Tất cả tương tác được kiểm soát thông qua danh tính workload, xác thực mTLS và policy kiểm soát chi tiết.

### 2. Kiến trúc tổng thể

- Agent uỷ quyền request cho Envoy proxy A.
- Envoy proxy A được cấp danh tính của Agent bằng SPIFFE ID (qua SPIRE Agent).
- Envoy proxy A kết nối tới Envoy proxy S bằng mTLS.
- Envoy proxy S + OPA xác thực và kiểm soát quyền truy cập dựa trên policy.
- Envoy proxy S chuyển tiếp request tới REST API.

### 3. Kiến trúc tham chiếu

- Envoy + SPIRE: https://spiffe.io/docs/latest/microservices/envoy/
- Envoy + OPA: https://www.openpolicyagent.org/docs/envoy

### 3. Công nghệ sử dụng

- Python: triển khai LLM agent.
- FastAPI: triển khai REST API.
- SPIFFE/SPIRE: cấp danh tính cho agent.
- Envoy Proxy: sidecar proxy, chịu trách nhiệm trung gian các kết nối mạng giữa các dịch vụ (service-to-service).
- OPA: kiểm soát quyền truy cập theo policy JSON Rego.
- Docker Compose: tạo môi trường thử nghiệm nhất quán.


## IV. Đánh giá và Bài học rút ra

### Ưu điểm

- Danh tính workload động, không dùng credential tĩnh.
- Tách biệt rõ giữa xác thực (mTLS, SPIRE) và ủy quyền (OPA).
- Triển khai theo mô hình zero trust.
- Dễ tích hợp vào môi trường có Kubernetes hoặc service mesh.

### Hạn chế

- Độ phức tạp triển khai cao, cần nhiều thành phần.
- Quản lý policy cần hiểu rõ logic Rego.
- SPIRE chưa phổ biến rộng rãi trong doanh nghiệp Việt Nam.

### Bài học

- IAM cho workload là bước đi tất yếu với các hệ thống tự động hóa.
- Mô hình kết hợp SPIFFE/SPIRE + Envoy + OPA cho thấy hiệu quả cao về bảo mật và kiểm soát.

## V. Kết luận

- Tóm tắt vai trò và giá trị của Workload IAM trong bối cảnh hiện đại.
- Khẳng định tính ứng dụng của các chuẩn như SPIFFE/SPIRE và proxy-based control.
- Đề xuất hướng mở rộng: tích hợp vào hệ thống lớn hơn, triển khai trên Kubernetes, hoặc hỗ trợ thêm nhiều loại agent.

## Phụ lục

- A. Mã nguồn demo LLM Agent
- B. Cấu hình Envoy Proxy
- C. Policy Rego của OPA
- D. File cấu hình SPIRE (registration entry)
- E. Docker Compose file
- F. Tài liệu tham khảo
