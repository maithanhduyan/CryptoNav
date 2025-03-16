Dưới đây là hướng dẫn chi tiết cách tích hợp và hoàn thiện quản lý migrations cho dự án của bạn với công cụ **Alembic**:

---

## ✅ **Bước 1: Cài đặt Alembic**

Trước hết, đảm bảo đã thêm `alembic` vào file `requirements.txt`:

```
alembic
```

và cài đặt:

```bash
pip install alembic
```

---

## ✅ **Bước 2: Khởi tạo Alembic (lần đầu tiên)**

Tại thư mục gốc (`fastapi/`):

```bash
alembic init alembic
```

Lệnh trên sẽ tạo cấu trúc mặc định:

```
fastapi/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
```

---

## ✅ **Bước 3: Cấu hình alembic.ini**

File `alembic.ini` cần cấu hình kết nối đến database:

### `alembic.ini`

```ini
[alembic]
script_location = alembic

sqlalchemy.url = postgresql://appuser:apppassword@db:5432/app

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

> Lưu ý: URL database có thể đặt trong biến môi trường bằng cách:  
> `sqlalchemy.url = ${DATABASE_URL}`

---

## ✅ **Bước 4: Sửa file `env.py` để sử dụng model đã có**

File `alembic/env.py` cần import và dùng metadata của models trong dự án.

### `alembic/env.py`

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys, os

# Thêm đường dẫn thư mục gốc dự án vào PYTHONPATH
sys.path.append(os.getcwd())

from app.database import Base  # Import Base từ app.database
from app.config import DATABASE_URL

config = context.config
fileConfig(config.config_file_name)

# Gán metadata của các models để Alembic biết khi migrate
target_metadata = Base.metadata

def run_migrations_offline():
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

> **Giải thích:**
>
> - Import metadata (`Base.metadata`) từ model của bạn.
> - Cấu hình lại DATABASE_URL từ config của ứng dụng để Alembic có thể migrate đúng database đang được dùng.

---

## ✅ **Bước 5: Tạo migration đầu tiên (tự động)**

Sau khi đã cấu hình đúng, chạy lệnh sau để Alembic tạo file migration tự động dựa trên model hiện có:

```bash
alembic revision --autogenerate -m "Initial migration"
```

Alembic sẽ tạo file trong `alembic/versions/`.

---

## ✅ **Bước 6: Chạy migration**

Chạy lệnh này để áp dụng migration vào database:

```bash
alembic upgrade head
```

Migration sẽ tạo các bảng tương ứng trong DB.

---

## ✅ **Bước 7: Chạy migration qua Docker-compose**

Bạn có thể chạy migration qua docker-compose dễ dàng như sau:

```bash
docker-compose run --rm cryptonav-api alembic upgrade head
```

**Chú ý:** Dockerfile/Docker-compose của bạn phải đảm bảo Alembic được cài đặt và truy cập được vào file cấu hình Alembic.

---

## ✅ **Cấu trúc hoàn chỉnh sau khi tích hợp Alembic:**

```
fastapi/
├── alembic/
│   ├── versions/
│   │   └── <migration_id>_initial_migration.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── model.py
│   ├── crud.py
│   ├── router.py
│   ├── auth.py
│   ├── logger.py
│   └── main.py
├── requirements.txt
├── Dockerfile
└── script/
    ├── setup.sh
    └── start.sh
```

---

## 🎯 **Hoàn tất!**

Bạn đã hoàn thiện quản lý migrations database sử dụng Alembic. Bây giờ mỗi khi model database thay đổi, bạn chỉ cần chạy:

```bash
alembic revision --autogenerate -m "Your change description"
alembic upgrade head
```

để cập nhật schema database dễ dàng và an toàn.

---

## Bonus: Tạo task migration trong .vscode

Dưới đây là cấu hình hoàn chỉnh cho file `.vscode/tasks.json`, tạo một task để chạy nhanh hai lệnh Alembic (revision và upgrade) chỉ với một click:

**`.vscode/tasks.json`**

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Alembic: Auto Revision & Upgrade",
      "type": "shell",
      "command": "alembic revision --autogenerate -m \"${input:migrationMessage}\" && alembic upgrade head",
      "options": {
        "cwd": "${workspaceFolder}/fastapi"
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      },
      "group": {
        "kind": "build",
        "isDefault": false
      }
    }
  ],
  "inputs": [
    {
      "id": "migrationMessage",
      "type": "promptString",
      "description": "Enter migration description:"
    }
  ]
}
```

### ⚙️ **Hướng dẫn sử dụng:**

- Nhấn tổ hợp phím: **`Ctrl+Shift+P`** (Windows/Linux) hoặc **`Cmd+Shift+P`** (macOS).
- Gõ `Tasks: Run Task`, sau đó chọn task **`Alembic: Auto Revision & Upgrade`**.
- VSCode sẽ hỏi bạn nhập mô tả migration. Nhập nội dung vào và Enter.
- Hai lệnh Alembic sẽ được thực thi tự động ngay sau đó.

Task này giúp bạn dễ dàng quản lý migrations trực tiếp trong VSCode rất thuận tiện!
