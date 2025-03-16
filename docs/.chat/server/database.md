Dưới đây là phiên bản cập nhật của thiết kế database theo yêu cầu, trong đó:

- Một user có thể tạo nhiều portfolio.
- Bảng **CryptoAsset** được đổi tên thành **Asset**.

---

## 1. Các thực thể (Entities) chính

### a. Người dùng (User)

- **Thông tin lưu trữ:** id, username, email, mật khẩu (được mã hoá), thông tin cá nhân (họ tên, ngày sinh, vv), cài đặt bảo mật.
- **Vai trò:** Một người dùng có thể quản lý nhiều danh mục đầu tư (portfolio).

### b. Danh mục đầu tư (Portfolio)

- **Thông tin lưu trữ:** id, user_id, tên danh mục, mô tả, ngày tạo, trạng thái (đang hoạt động, tạm ngưng, vv).
- **Quan hệ:** Mỗi portfolio thuộc về một user (quan hệ 1-nhiều giữa User và Portfolio).

### c. Tài sản (Asset)

- **Thông tin lưu trữ:** id, mã tài sản (ví dụ: BTC, ETH), tên tài sản, mô tả, thông tin kỹ thuật (blockchain, thuật toán, vv).
- **Vai trò:** Dữ liệu tham chiếu để gán cho các giao dịch và theo dõi hiệu suất của tài sản.

### d. Giao dịch (Transaction)

- **Thông tin lưu trữ:** id, portfolio_id, asset_id, loại giao dịch (mua, bán, chuyển khoản, vv), số lượng, giá giao dịch tại thời điểm thực hiện, phí giao dịch, ngày giao dịch.
- **Quan hệ:**
  - Liên kết giữa portfolio và asset.
  - Hỗ trợ lưu trữ các giao dịch từ nhiều nguồn hoặc sàn giao dịch khác nhau nếu cần.

### e. Lịch sử giá (PriceHistory)

- **Thông tin lưu trữ:** asset_id, thời gian, giá mở cửa, giá đóng cửa, giá cao, giá thấp, khối lượng giao dịch.
- **Vai trò:** Hỗ trợ phân tích biến động giá và hiệu suất của asset theo thời gian.

---

## 2. Mối quan hệ giữa các bảng

- **User - Portfolio:** Một user có thể tạo nhiều portfolio.
- **Portfolio - Transaction:** Một portfolio có thể chứa nhiều giao dịch.
- **Asset - Transaction:** Mỗi giao dịch liên quan đến một asset cụ thể.
- **Asset - PriceHistory:** Một asset có thể có nhiều bản ghi lịch sử giá theo thời gian.

> **Ghi chú:** Thiết kế có thể mở rộng để hỗ trợ các tính năng bổ sung như quản lý ví (Wallet), tích hợp API từ các sàn giao dịch hoặc theo dõi chuyển khoản giữa các portfolio.

---

## 3. Sơ đồ ER (Entity Relationship Diagram)

```
User
 └──< Portfolio
        └──< Transaction >── Asset
                             └──< PriceHistory
```

- **User:** Quản lý thông tin cá nhân và danh mục đầu tư.
- **Portfolio:** Liên kết trực tiếp với User, chứa danh sách các giao dịch.
- **Transaction:** Ghi nhận các giao dịch mua, bán hoặc chuyển khoản liên quan đến Asset.
- **Asset & PriceHistory:** Asset lưu trữ thông tin cơ bản của tài sản, còn PriceHistory cung cấp dữ liệu thị trường theo thời gian.

---

## 4. Ví dụ thiết kế bảng

### Bảng User

| Trường     | Kiểu dữ liệu         | Ràng buộc                 |
| ---------- | -------------------- | ------------------------- |
| id         | INT (AUTO_INCREMENT) | PRIMARY KEY               |
| username   | VARCHAR(50)          | UNIQUE, NOT NULL          |
| email      | VARCHAR(100)         | UNIQUE, NOT NULL          |
| password   | VARCHAR(255)         | NOT NULL                  |
| created_at | DATETIME             | DEFAULT CURRENT_TIMESTAMP |

### Bảng Portfolio

| Trường      | Kiểu dữ liệu         | Ràng buộc                       |
| ----------- | -------------------- | ------------------------------- |
| id          | INT (AUTO_INCREMENT) | PRIMARY KEY                     |
| user_id     | INT                  | FOREIGN KEY REFERENCES User(id) |
| name        | VARCHAR(100)         | NOT NULL                        |
| description | TEXT                 |                                 |
| created_at  | DATETIME             | DEFAULT CURRENT_TIMESTAMP       |

### Bảng Asset

| Trường      | Kiểu dữ liệu         | Ràng buộc        |
| ----------- | -------------------- | ---------------- |
| id          | INT (AUTO_INCREMENT) | PRIMARY KEY      |
| symbol      | VARCHAR(10)          | UNIQUE, NOT NULL |
| name        | VARCHAR(100)         | NOT NULL         |
| description | TEXT                 |                  |

### Bảng Transaction

| Trường           | Kiểu dữ liệu         | Ràng buộc                             |
| ---------------- | -------------------- | ------------------------------------- |
| id               | INT (AUTO_INCREMENT) | PRIMARY KEY                           |
| portfolio_id     | INT                  | FOREIGN KEY REFERENCES Portfolio(id)  |
| asset_id         | INT                  | FOREIGN KEY REFERENCES Asset(id)      |
| transaction_type | VARCHAR(10)          | (mua, bán, vv.) NOT NULL              |
| amount           | DECIMAL(18,8)        | NOT NULL                              |
| price            | DECIMAL(18,8)        | Giá giao dịch tại thời điểm thực hiện |
| fee              | DECIMAL(18,8)        | Phí giao dịch (nếu có)                |
| transaction_date | DATETIME             | NOT NULL                              |

### Bảng PriceHistory

| Trường      | Kiểu dữ liệu         | Ràng buộc                        |
| ----------- | -------------------- | -------------------------------- |
| id          | INT (AUTO_INCREMENT) | PRIMARY KEY                      |
| asset_id    | INT                  | FOREIGN KEY REFERENCES Asset(id) |
| date        | DATETIME             | NOT NULL                         |
| open_price  | DECIMAL(18,8)        |                                  |
| close_price | DECIMAL(18,8)        |                                  |
| high_price  | DECIMAL(18,8)        |                                  |
| low_price   | DECIMAL(18,8)        |                                  |
| volume      | DECIMAL(18,8)        |                                  |

---

## 5. Các điểm cần lưu ý mở rộng và tối ưu

- **Index và tối ưu hóa truy vấn:**

  - Tạo chỉ mục trên các trường khóa chính và khóa ngoại (user_id, portfolio_id, asset_id).
  - Chỉ mục trên trường `date` của bảng PriceHistory để tối ưu truy vấn theo thời gian.

- **Phân mảnh (Partitioning):**

  - Với bảng PriceHistory chứa dữ liệu lớn theo thời gian, có thể sử dụng phân mảnh (ví dụ: theo tháng hoặc quý) để cải thiện hiệu suất truy vấn.

- **Caching và tích hợp API:**

  - Sử dụng caching cho dữ liệu giá của asset để giảm tải truy vấn từ cơ sở dữ liệu.
  - Tích hợp dữ liệu từ API các sàn giao dịch để cập nhật thông tin giá và khối lượng giao dịch.

- **Bảo mật và sao lưu dữ liệu:**
  - Mã hoá mật khẩu và các thông tin nhạy cảm.
  - Thiết lập phân quyền truy cập hợp lý cho từng user.
  - Thiết lập chiến lược backup định kỳ để đảm bảo an toàn dữ liệu.

---

## 6. Tổng kết

Phiên bản cập nhật này giữ nguyên mối quan hệ giữa các bảng và nhấn mạnh rằng một user có thể tạo nhiều portfolio. Đồng thời, bảng **Asset** thay thế cho **CryptoAsset** để làm rõ rằng dự án có thể mở rộng ra nhiều loại tài sản chứ không chỉ giới hạn ở tiền điện tử. Thiết kế này đảm bảo tính linh hoạt, khả năng mở rộng và hiệu năng truy vấn, đồng thời cho phép tích hợp các tính năng bổ sung trong tương lai như quản lý ví, tích hợp API sàn giao dịch, hay báo cáo phân tích hiệu suất đầu tư.

Hy vọng thiết kế cập nhật này sẽ đáp ứng được yêu cầu của dự án quản lý danh mục đầu tư.
