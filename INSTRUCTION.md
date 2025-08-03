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

```plaintext
[LLM Agent] <--mTLS--> [Envoy Sidecar] <--HTTP--> [FastAPI + OPA]

                      [SPIRE Agent] <---> [SPIRE Server]
```

- Agent được cấp danh tính bằng SPIFFE ID (qua SPIRE Agent).
- Agent kết nối tới Envoy proxy bằng mTLS.
- Envoy chuyển tiếp request tới REST API và đính kèm SPIFFE ID.
- FastAPI + OPA xác thực và kiểm soát quyền truy cập dựa trên policy.

### 3. Công nghệ sử dụng

- Python: triển khai LLM agent.
- FastAPI: triển khai REST API.
- SPIFFE/SPIRE: cấp danh tính cho agent.
- Envoy Proxy: làm gateway mTLS + policy forwarding.
- OPA: kiểm soát quyền truy cập theo policy JSON Rego.
- Docker Compose: tạo môi trường thử nghiệm nhất quán.

## IV. Triển khai PoC

### 1. Chuẩn bị môi trường

- Cài đặt Docker, Docker Compose.
- Cấu hình SPIRE Server và SPIRE Agent.
- Tạo registration entry cho LLM agent và REST API.
- Cài Envoy proxy và cấu hình listener mTLS + OPA external auth.

### 2. Xây dựng các thành phần

- LLM Agent (Python):
- Kết nối mTLS với Envoy (SVID từ SPIRE).
- Gửi request GET/POST tới API /users.
- REST API (FastAPI):
- Nhận request từ Envoy.
- Extract SPIFFE ID từ header.
- Gửi request tới OPA để kiểm tra quyền truy cập.
- OPA Policy (Rego):
- Quy định: chỉ cho phép SPIFFE ID cụ thể truy cập resource cụ thể.
- Envoy Proxy:
- Cấu hình TLS context với chứng chỉ SPIRE.
- Forward SPIFFE ID trong header.
- Dùng ext_authz gọi tới OPA để xác thực.

### 3. Demo luồng hoạt động

- Agent gửi request truy cập tài nguyên.
- Envoy xác thực mTLS, chuyển tiếp kèm SPIFFE ID.
- FastAPI xác minh và chuyển SPIFFE ID tới OPA.
- OPA quyết định cho phép hoặc từ chối.
- Trả kết quả về cho agent.

## V. Đánh giá và Bài học rút ra

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

## VI. Kết luận

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
