

# Cấu trúc Dự án FastAPI
- Prompt:
```
"Tạo một ứng dụng FastAPI với các yêu cầu sau:  
1. **Cấu trúc thư mục**: Đặt toàn bộ mã nguồn trong thư mục app, bao gồm các file:  
   - main.py (điểm vào của ứng dụng)  
   - model.py (định nghĩa các model User và Item)  
   - router.py (xử lý các tuyến đường API)  
   - database.py (quản lý kết nối cơ sở dữ liệu)  
   - config.py (lưu trữ cấu hình ứng dụng)  
   Thêm các file hoặc thư mục bổ sung nếu cần (ví dụ: core, api, test, email-template, hoặc các file liên quan đến migrations).  

2. **Thư viện sử dụng**:  
   - Sử dụng **SQLAlchemy** để kết nối cơ sở dữ liệu:  
     - SQLite cho môi trường test/phát triển.  
     - PostgreSQL cho môi trường production.  
   - Triển khai ghi log với mức độ khác nhau (DEBUG cho phát triển, INFO cho sản xuất).  

3. **Dockerfile**:  
   - Sử dụng image cơ sở ubuntu:24.04.  
   - Hỗ trợ hai chế độ:  
     - **Development**: Chạy với tính năng reload để phát triển.  
     - **Production**: Chạy với nhiều worker để tối ưu hiệu suất.  

4. **docker-compose.yml**:  
   - Bao gồm các dịch vụ:  
     - **PostgreSQL**: Cơ sở dữ liệu cho production.  
     - **NGINX**: Proxy đến server API.  
     - **API server**: Xây dựng từ FastAPI, kết nối với PostgreSQL trong production.  

Hãy cung cấp mã nguồn chi tiết cho từng file, bao gồm cách triển khai SQLAlchemy với migrations (nếu cần), cấu hình log, và cách chạy ứng dụng trong cả hai chế độ (development và production)."

Yêu cầu:
1. **Phiên bản SQLAlchemy**: sử dụng SQLAlchemy 2.x 
2. **Công cụ di trú CSDL**: sử dụng Alembic 
3. **Xác thực và ủy quyền**: cần tích hợp JWT
4. **Các endpoints API**: định nghĩa sẵn một số endpoint cụ thể (ví dụ: /users, /items)
5. **Công cụ logging**:  tích hợp logging với một dịch vụ cụ thể như ELK, Prometheus 
6. **Nginx cấu hình**: yêu cầu cụ thể về proxy, caching, hoặc load balancing 
```

Dự án được tổ chức trong thư mục **`app/`** với các tệp mã nguồn chính như sau:

```plaintext
app/
├── main.py         # Điểm vào của ứng dụng FastAPI
├── model.py        # Định nghĩa các model cơ sở dữ liệu (User, Item)
├── router.py       # Định nghĩa các tuyến (endpoints) API /users và /items
├── database.py     # Cấu hình kết nối cơ sở dữ liệu (SQLAlchemy)
├── config.py       # Cấu hình ứng dụng (cơ sở dữ liệu, JWT, etc.)
├── auth.py         # Chức năng xác thực JWT (tạo/kiểm tra token)
├── logger.py       # Cấu hình logging (tích hợp ELK/Prometheus)
└── nginx.conf      # Cấu hình Nginx (proxy, caching, load balancing)
docker-compose.yml  # Cấu hình Docker Compose (PostgreSQL, Nginx, API)
Dockerfile          # Định nghĩa image Docker cho API (dev và prod)
```

Dưới đây là nội dung chi tiết cho từng thành phần và hướng dẫn triển khai.

## 1. Tệp config.py – Cấu hình Ứng dụng

Tệp **`config.py`** lưu trữ các cấu hình cần thiết cho ứng dụng, bao gồm chuỗi kết nối cơ sở dữ liệu, khóa bí mật JWT, thuật toán mã hóa, thời gian hết hạn token, v.v. Bạn có thể sử dụng biến môi trường hoặc đặt giá trị cố định tại đây. Ví dụ:

```python
# app/config.py
import os

# URL kết nối cơ sở dữ liệu (PostgreSQL trong production, có thể là SQLite trong development)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydatabase")

# Cấu hình JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Khóa bí mật để mã hóa JWT
JWT_ALGORITHM = "HS256"                                          # Thuật toán mã hóa JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30                                 # Thời gian hết hạn token (30 phút)

# Cấu hình logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Mức log mặc định (DEBUG/INFO/WARNING/ERROR)
```

Trong cấu hình trên, ta sử dụng biến môi trường (nếu có) cho **DATABASE_URL** và **JWT_SECRET_KEY** để thuận tiện khi triển khai. Các tham số khác như thuật toán JWT và thời hạn token có thể cố định hoặc cũng đưa vào config.

## 2. Tệp database.py – Kết nối Cơ sở Dữ liệu (SQLAlchemy 2.x)

Tệp **`database.py`** chịu trách nhiệm thiết lập kết nối tới cơ sở dữ liệu sử dụng SQLAlchemy. Ta tạo engine, Session và Base (cho ORM model) cũng như một hàm tiện ích `get_db` để lấy session cho mỗi request. Ví dụ:

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app import config

# Tạo engine kết nối tới cơ sở dữ liệu (SQLAlchemy 2.x)
engine = create_engine(config.DATABASE_URL, future=True)  # future=True cho SQLAlchemy 2.x

# Tạo sessionmaker để tạo Session cho mỗi phiên làm việc
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class cho các model ORM
Base = declarative_base()

# Dependency: Lấy session database cho mỗi request (dùng với FastAPI Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Giải thích: `engine` được tạo với URL từ config. `SessionLocal` là một factory để tạo các session kết nối database. Hàm `get_db` sẽ được sử dụng trong các tuyến API để lấy session, và đảm bảo đóng session sau khi xử lý request xong. Mỗi model ORM sẽ kế thừa từ `Base` để SQLAlchemy biết và quản lý.

> **Lưu ý:** Khi triển khai thực tế, bạn cần chạy **migration** để tạo các bảng trong cơ sở dữ liệu. Dự án này sử dụng **Alembic** để quản lý schema, chi tiết sẽ được nói ở phần hướng dẫn triển khai.

## 3. Tệp model.py – Định nghĩa Model `User` và `Item`

Tệp **`model.py`** định nghĩa các model ORM cho bảng **User** và **Item** trong cơ sở dữ liệu, sử dụng SQLAlchemy ORM. Mỗi model là một class kế thừa `Base` từ `database.py`, với các thuộc tính ánh xạ tới cột trong bảng.

```python
# app/model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive (ví dụ trạng thái người dùng)

    # Quan hệ 1-n: một user có thể có nhiều item
    items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Quan hệ ngược: mỗi item thuộc về một owner (user)
    owner = relationship("User", back_populates="items")

    def __repr__(self):
        return f"<Item(title='{self.title}', owner_id={self.owner_id})>"
```

Giải thích:

- **User** có các cột: `username`, `email` là duy nhất và không được null, `hashed_password` để lưu mật khẩu đã băm (hash), và `is_active` để đánh dấu tình trạng hoạt động. Trường `items` sử dụng `relationship` để lấy danh sách các Item thuộc về user đó.
- **Item** có các cột: `title`, `description` mô tả hàng hóa/nội dung, và `owner_id` là khóa ngoại tham chiếu đến `users.id`. Trường `owner` là `relationship` để truy cập user sở hữu item.

Khai báo `__repr__` giúp in ra thông tin model dễ đọc (hữu ích cho debug/logging).

## 4. Tệp auth.py – Xác thực JWT

Tệp **`auth.py`** quản lý việc tạo và xác minh JSON Web Token (JWT) cho người dùng. Nó bao gồm các hàm băm mật khẩu, kiểm tra mật khẩu, tạo token, và phụ thuộc (dependency) để lấy người dùng hiện tại từ token.

```python
# app/auth.py
from datetime import datetime, timedelta

import jwt  # PyJWT library
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app import config, model, database

# Schema OAuth2PasswordBearer để lấy token từ Header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def create_access_token(data: dict, expires_delta: int = None):
    """Tạo JWT token từ thông tin người dùng."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Sinh token JWT
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu plaintext với mật khẩu đã băm."""
    # Ở đây dùng giải pháp đơn giản để minh họa, khuyến nghị dùng bcrypt trong thực tế
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    """Băm mật khẩu (hash password) để lưu vào DB."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(db: database.SessionLocal = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    """Dependency: Lấy đối tượng User hiện tại dựa trên JWT token."""
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("sub")  # 'sub' sẽ chứa định danh người dùng (vd: username)
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Lấy người dùng từ DB
    user = db.query(model.User).filter(model.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

Giải thích:

- **oauth2_scheme**: Sử dụng OAuth2PasswordBearer để trích xuất token JWT từ header `Authorization: Bearer <token>`. `tokenUrl="/users/login"` chỉ ra đường dẫn để lấy token (ở đây là endpoint đăng nhập).
- **create_access_token**: Tạo một JWT chứa thông tin người dùng (**payload**). Ở đây, ta mong muốn payload chứa `sub` (subject) là username của user và `exp` (expiration) là thời điểm hết hạn. Sử dụng PyJWT (`jwt.encode`) với khóa bí mật và thuật toán từ config.
- **verify_password** và **get_password_hash**: Sử dụng hàm băm SHA256 để hash mật khẩu cho đơn giản. **Lưu ý:** Trong thực tế nên dùng thư viện **bcrypt** hoặc **passlib** để lưu mật khẩu an toàn hơn (SHA256 thuần túy chưa đủ an toàn để lưu mật khẩu).
- **get_current_user**: Đây là hàm dependency sử dụng trong các endpoint yêu cầu xác thực. Nó decode token JWT, lấy `username` (hoặc id) của user từ payload (ở đây giả sử ta lưu username vào claim `sub` khi tạo token). Sau đó truy vấn database tìm user. Nếu token không hợp lệ hoặc user không tồn tại, ném ra HTTP 401. Nếu hợp lệ, trả về đối tượng user tương ứng.

Khi đăng nhập, ta sẽ tạo token với payload gồm `sub=username`. Ví dụ trong endpoint login (xem phần router.py bên dưới), sau khi xác thực user, ta gọi `create_access_token({"sub": user.username})` để tạo token.

## 5. Tệp router.py – Định nghĩa các Endpoint /users và /items

Tệp **`router.py`** khai báo các tuyến API cho **/users** và **/items** theo yêu cầu đề bài. Sử dụng FastAPI APIRouter để tách biệt logic. Các endpoint bao gồm: đăng ký người dùng, đăng nhập, lấy thông tin người dùng hiện tại; tạo, xem, sửa, xóa Item. Mô tả chi tiết như sau:

```python
# app/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import model, database, auth

# Tạo các router cho user và item
users_router = APIRouter(prefix="/users")
items_router = APIRouter(prefix="/items")

# Endpoint: Đăng ký người dùng (Register)
@users_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(username: str, email: str, password: str, db: Session = Depends(database.get_db)):
    # Kiểm tra username hoặc email đã tồn tại
    existing_user = db.query(model.User).filter((model.User.username == username) | (model.User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    # Tạo đối tượng User mới
    hashed_pw = auth.get_password_hash(password)
    new_user = model.User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

# Endpoint: Đăng nhập (Login) – trả về JWT token
@users_router.post("/login")
def login(username: str, password: str, db: Session = Depends(database.get_db)):
    # Kiểm tra thông tin đăng nhập
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Tạo JWT token
    access_token = auth.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint: Lấy thông tin người dùng hiện tại
@users_router.get("/me")
def read_current_user(current_user: model.User = Depends(auth.get_current_user)):
    # current_user được lấy qua dependency, ở đây ta chỉ trả về thông tin cơ bản
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}

# Endpoint: Lấy danh sách tất cả Item (có thể không yêu cầu đăng nhập)
@items_router.get("/", response_model=list[dict])
def get_items(db: Session = Depends(database.get_db)):
    items = db.query(model.Item).all()
    # Trả về danh sách item (chỉ bao gồm các trường cơ bản)
    return [{"id": item.id, "title": item.title, "description": item.description, "owner_id": item.owner_id} for item in items]

# Endpoint: Tạo Item mới (yêu cầu xác thực)
@items_router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(title: str, description: str = None,
                db: Session = Depends(database.get_db),
                current_user: model.User = Depends(auth.get_current_user)):
    # Tạo một item mới gắn với user hiện tại
    new_item = model.Item(title=title, description=description, owner_id=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"id": new_item.id, "title": new_item.title, "description": new_item.description, "owner_id": new_item.owner_id}

# Endpoint: Xem chi tiết một Item theo ID
@items_router.get("/{item_id}")
def read_item(item_id: int, db: Session = Depends(database.get_db), current_user: model.User = Depends(auth.get_current_user)):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # Nếu muốn giới hạn, có thể kiểm tra quyền: chỉ cho phép chủ sở hữu xem, ở đây cho phép mọi user đã đăng nhập đều có thể xem
    return {"id": item.id, "title": item.title, "description": item.description, "owner_id": item.owner_id}

# Endpoint: Cập nhật Item (yêu cầu chủ sở hữu)
@items_router.put("/{item_id}")
def update_item(item_id: int, title: str = None, description: str = None,
                db: Session = Depends(database.get_db),
                current_user: model.User = Depends(auth.get_current_user)):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this item")
    # Cập nhật các trường được cung cấp
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    db.commit()
    db.refresh(item)
    return {"message": "Item updated successfully", "item": {
                "id": item.id, "title": item.title,
                "description": item.description, "owner_id": item.owner_id}
            }

# Endpoint: Xóa Item (yêu cầu chủ sở hữu)
@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(database.get_db),
                current_user: model.User = Depends(auth.get_current_user)):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
```

Giải thích các endpoint quan trọng:

- **POST /users/register**: Tạo mới user. Yêu cầu `username`, `email`, `password` (có thể chuyển thành body model bằng Pydantic cho gọn, nhưng ở đây dùng tham số đơn giản cho dễ hiểu). Kiểm tra trùng lặp username/email, sau đó băm mật khẩu và lưu user. Trả về thông tin cơ bản của user vừa tạo.
- **POST /users/login**: Xác thực user. Tìm user theo username, kiểm tra mật khẩu. Nếu sai trả về 401. Nếu đúng, tạo JWT token (với `sub` là username) và trả về cho client. Client sẽ dùng token này cho các yêu cầu tiếp theo (đính kèm trong header `Authorization`).
- **GET /users/me**: Lấy thông tin người dùng hiện tại. Sử dụng dependency `get_current_user` trong `Depends` để tự động kiểm tra token và lấy user. Nếu token hợp lệ, trả về thông tin user (id, username, email).
- **GET /items/**: Trả về danh sách tất cả Item trong database. (Tùy nhu cầu, có thể không bắt buộc đăng nhập cho endpoint này. Ở đây không dùng `get_current_user` nên bất kỳ ai cũng gọi được. Nếu muốn chỉ user đã đăng nhập mới xem được, thêm `current_user: User = Depends(get_current_user)`.)
- **POST /items/**: Tạo một item mới. Bắt buộc người gọi phải đăng nhập (vì có `current_user = Depends(auth.get_current_user)`). Lấy thông tin người dùng hiện tại, dùng `current_user.id` làm `owner_id` cho item. Lưu item vào DB và trả về chi tiết item.
- **GET /items/{item_id}**: Xem thông tin chi tiết item có id tương ứng. Ở đây yêu cầu phải có token (vì dùng `current_user = Depends(...)`), sau đó trả về item. Nếu muốn _public_ (bất kỳ ai cũng xem được item), có thể bỏ yêu cầu `current_user`.
- **PUT /items/{item_id}**: Cập nhật một item. Yêu cầu đăng nhập và phải **đúng chủ sở hữu** thì mới được cập nhật. Kiểm tra `item.owner_id` với `current_user.id`. Nếu không khớp, trả về 403. Sau đó cập nhật các trường được truyền vào (title/description).
- **DELETE /items/{item_id}**: Tương tự cập nhật, yêu cầu đăng nhập và chỉ chủ sở hữu item mới xóa được. Thực hiện xóa khỏi DB nếu hợp lệ.

Tất cả các endpoint **đều trả về dữ liệu dạng JSON**. Mã trạng thái HTTP cũng được thiết lập (201 Created khi tạo mới, 204 No Content khi xóa thành công, 401 Unauthorized, 403 Forbidden, v.v.). FastAPI hỗ trợ các mã này thông qua `status` module.

## 6. Tệp main.py – Điểm vào của Ứng dụng FastAPI

Tệp **`main.py`** tạo ứng dụng FastAPI, bao gồm router, cấu hình middleware nếu cần và chạy ứng dụng. Trong **Dockerfile**, tệp này sẽ được gọi khi khởi chạy container. Dưới đây là ví dụ nội dung:

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import users_router, items_router
from app import logger, config, database, model

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="FastAPI Application", version="1.0.0")

# Cấu hình CORS (nếu cần thiết cho front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi domain (cân nhắc thu hẹp trong production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các router cho users và items vào ứng dụng
app.include_router(users_router)
app.include_router(items_router)

# Sự kiện khởi động ứng dụng
@app.on_event("startup")
def startup_event():
    # Khởi tạo cấu hình logging
    logger.setup_logging()
    # Tạo bảng trong DB nếu chưa có (chỉ nên dùng trong môi trường phát triển)
    # Trong production, nên dùng Alembic migrations thay vì create_all.
    database.Base.metadata.create_all(bind=database.engine)
    print("Application startup: Database tables checked/created.")

# Sự kiện tắt ứng dụng
@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown.")
```

Giải thích:

- Tạo thực thể FastAPI `app` với tiêu đề và phiên bản.
- **CORS** middleware được thêm (không bắt buộc, nhưng thường cần nếu có frontend gọi API). Ở đây cho phép tất cả nguồn (`*`), trong thực tế nên giới hạn vào domain cụ thể.
- **include_router**: Gắn các router từ `router.py` vào ứng dụng. Các endpoint giờ sẽ khả dụng (/users/..., /items/...).
- **Startup event**: Khi ứng dụng khởi chạy, ta gọi `logger.setup_logging()` để cấu hình logging (sẽ định nghĩa trong logger.py). Ngoài ra, gọi `Base.metadata.create_all` để tạo bảng nếu chưa tồn tại - cái này hữu ích khi phát triển hoặc chạy thử (dev). Trong môi trường production, **nên sử dụng Alembic** để update schema thay vì create_all (tránh mất dữ liệu).
- **Shutdown event**: Chỉ log ra thông báo đơn giản. Bạn có thể thêm logic giải phóng tài nguyên nếu cần.

## 7. Tệp logger.py – Cấu hình Logging (ELK/Prometheus)

Tệp **`logger.py`** cấu hình hệ thống log cho ứng dụng. Mục tiêu là để log của ứng dụng có thể được thu thập bởi ELK stack hoặc hệ thống giám sát (Prometheus). Ở mức cơ bản, ta sẽ cấu hình log gửi ra **stdout** với định dạng phù hợp (ELK thường thu thập log từ stdout của container). Ta cũng có thể xuất log dưới dạng JSON để dễ dàng phân tích. Ví dụ:

```python
# app/logger.py
import logging
import sys
from pythonjsonlogger import jsonlogger  # Thư viện hỗ trợ format JSON (cài qua pip)

from app import config

def setup_logging():
    """Cấu hình logging cho ứng dụng."""
    log_level = config.LOG_LEVEL

    # Tạo logger gốc
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Cấu hình handler gửi log ra stdout
    handler = logging.StreamHandler(sys.stdout)
    # Định dạng log: ở đây dùng JSONFormatter để phù hợp với ELK
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Ví dụ log ban đầu
    logging.info("Logging is configured. Level: %s", log_level)
```

Giải thích:

- **pythonjsonlogger.JsonFormatter**: là format chuyển log record thành JSON (cần cài thư viện **python-json-logger**). Mẫu format bao gồm thời gian, mức log, tên logger, và nội dung thông báo. Log dưới dạng JSON sẽ trông như:

```json
{
  "asctime": "2025-03-15 06:17:06,123",
  "levelname": "INFO",
  "name": "root",
  "message": "Logging is configured. Level: INFO"
}
```

Đây là định dạng dễ dàng cho Logstash/Elasticsearch phân tích. Nếu không muốn dùng JSON, ta có thể dùng format chuỗi thông thường (`logging.Formatter`).

- Log được đưa ra `sys.stdout`, Docker sẽ lấy log này. Trong ELK, ta cấu hình filebeat hoặc log driver để tập hợp log container.
- Về **Prometheus**: Prometheus thường thu thập **metrics** hơn là log. Để tích hợp Prometheus, có thể thêm một endpoint `/metrics` cung cấp số liệu (nhờ thư viện **prometheus_client**). Tuy nhiên, điều đó thuộc phần monitoring/metrics, không trực tiếp trong file logger.py. Ở đây ta tập trung cấu hình log cho ELK. (Nếu cần, bạn có thể bổ sung **metrics endpoint** sau bằng cách sử dụng `prometheus_client` hoặc `fastapi_prometheus`.)

Sau khi gọi `setup_logging()` trong `main.py`, toàn bộ ứng dụng sẽ log theo cấu hình trên. Mọi sự kiện (như các request FastAPI, hoặc log thủ công `logging.info/debug/error`) sẽ tuân theo format JSON.

## 8. Tệp nginx.conf – Cấu hình Nginx Proxy, Caching, Load Balancing

Tệp **`nginx.conf`** cấu hình máy chủ Nginx hoạt động như proxy chuyển tiếp yêu cầu đến ứng dụng FastAPI. Nó cũng thiết lập caching và load balancing. Trong Docker Compose, Nginx sẽ chạy tách biệt và trỏ đến dịch vụ FastAPI. Dưới đây là một ví dụ cấu hình Nginx cơ bản:

```nginx
# app/nginx.conf
# Định nghĩa upstream cho các server FastAPI
upstream fastapi_app {
    server api:8000;  # 'api' là tên service của FastAPI trong docker-compose (chạy trên cổng 8000)
    # Nếu có nhiều instance app, liệt kê chúng tại đây để Nginx load balance
    # server api2:8000;
}

# Thiết lập vùng lưu cache cho proxy (10 MB, có thể tăng tuỳ nhu cầu)
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=fastapi_cache:10m max_size=100m;

server {
    listen 80;
    server_name _;  # Lắng nghe trên tất cả tên miền (có thể thay bằng domain cụ thể)

    # Proxy tất cả request tới FastAPI
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # Xác định header cho WebSocket (nếu ứng dụng dùng WebSocket)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Kết nối tới upstream
        proxy_pass http://fastapi_app;

        # Caching: chỉ cache các request GET/HEAD, bỏ qua nếu có Authorization (nội dung cá nhân hoá)
        proxy_cache fastapi_cache;
        proxy_cache_methods GET HEAD;
        proxy_cache_valid 200 1m;  # Cache phản hồi HTTP 200 trong 1 phút
        proxy_cache_bypass $http_authorization;  # Bypass cache nếu có header Authorization

        # Thời gian chờ và số lần thử khi proxy
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }

    # (Tùy chọn) Caching cho các nội dung tĩnh nếu có
    # location /static {
    #    alias /app/app/static;
    #    expires 30d;
    # }
}
```

Giải thích:

- **upstream fastapi_app**: Khai báo cụm các server FastAPI mà Nginx sẽ phân phối request đến. Ở đây có một server `api:8000` (ứng với container ứng dụng). Nếu bạn mở rộng ứng dụng thành nhiều bản (scale nhiều container), liệt kê tất cả trong upstream. Nginx sẽ tự động **load balance** (cân bằng tải) giữa các server theo round-robin.
- **proxy_pass**: Chuyển tiếp mọi request từ client đến upstream FastAPI. Các `proxy_set_header` đảm bảo chuyển đúng thông tin host và IP client, và hỗ trợ nâng cấp kết nối (cho WebSocket).
- **Caching**:
  - `proxy_cache_path` định nghĩa vùng lưu cache (dung lượng, vị trí).
  - Trong `location /`, `proxy_cache fastapi_cache` bật cache, với `proxy_cache_methods` giới hạn cache cho GET/HEAD. `proxy_cache_valid 200 1m` nghĩa là cache phản hồi HTTP 200 trong 1 phút. Tùy nhu cầu, bạn có thể tăng thời gian cache lên (ví dụ dữ liệu ít thay đổi có thể cache vài phút hoặc hơn).
  - `proxy_cache_bypass $http_authorization` đảm bảo **không dùng cache cho request có header Authorization** (vì các request có JWT token thường là thông tin cá nhân hóa, không nên dùng bản cache dùng chung).
- **Timeout và failover**: Thiết lập thời gian chờ khi kết nối đến upstream, thời gian đọc, và cho phép Nginx thử lại một server khác nếu gặp lỗi (các mã 500, 502, 503).
- **Static files**: Nếu ứng dụng có phục vụ file tĩnh (như ảnh, CSS, v.v.), ta có thể dùng Nginx phục vụ trực tiếp (như cấu hình khối `location /static` ví dụ). Nginx xử lý file tĩnh hiệu quả hơn Uvicorn.

Tệp `nginx.conf` này sẽ được sử dụng trong container Nginx (sẽ cấu hình trong docker-compose.yml). Lưu ý mount file cấu hình vào đúng đường dẫn Nginx trong container (thường `/etc/nginx/conf.d/default.conf` như bên dưới).

## 9. Dockerfile – Định nghĩa Image cho FastAPI (Development & Production)

Tệp **`Dockerfile`** mô tả cách xây dựng image Docker cho ứng dụng FastAPI. Yêu cầu đề bài: sử dụng `ubuntu:24.04` làm base, và hỗ trợ 2 chế độ **Development** (tự động reload) và **Production** (nhiều worker). Ta có thể sử dụng biến môi trường hoặc tham số build để điều chỉnh chế độ chạy. Dưới đây là nội dung Dockerfile mẫu:

```dockerfile
# Dockerfile
FROM ubuntu:24.04

# Cập nhật và cài đặt Python3, pip, và các phụ thuộc cần thiết (ví dụ psycopg2)
RUN apt-get update && apt-get install -y python3 python3-pip build-essential libpq-dev

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép file yêu cầu (để cài đặt thư viện Python)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của ứng dụng vào image
COPY app/ ./app

# Sử dụng biến môi trường để xác định chế độ (dev hay prod)
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}

# Mặc định, expose cổng 8000 (ứng dụng FastAPI sẽ chạy trên cổng này)
EXPOSE 8000

# Sao chép script khởi động (script này sẽ kiểm tra ENVIRONMENT để chạy tương ứng)
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Điểm khởi chạy container: chạy script start.sh
ENTRYPOINT ["/start.sh"]
```

**Giải thích Dockerfile:**

- **Base image**: Sử dụng `ubuntu:24.04`. Đầu tiên cập nhật và cài đặt Python 3, pip, cũng như một số gói cần thiết (như `build-essential` và `libpq-dev` để có thể cài `psycopg2` kết nối PostgreSQL).
- **Copy requirements và cài đặt**: Tệp `requirements.txt` liệt kê các thư viện Python cần thiết (FastAPI, Uvicorn, SQLAlchemy, Alembic, PyJWT, etc.). Sử dụng pip để cài đặt.
- **Copy source code**: Chép toàn bộ thư mục `app` vào image.
- **ENVIRONMENT**: Sử dụng `ARG` và `ENV` để cấu hình biến môi trường **ENVIRONMENT**. Mặc định đặt là `production`. Khi build hoặc chạy container, có thể thay đổi giá trị này để chuyển chế độ.
- **Expose & start script**: Expose cổng 8000 (cổng ứng dụng sẽ lắng nghe). Sao chép file `start.sh` (sẽ viết bên dưới) và dùng nó làm ENTRYPOINT.

**Nội dung tệp start.sh:** (script dùng để chạy đúng lệnh tùy theo chế độ)

```bash
#!/bin/bash
# app/start.sh
set -e

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode (reload enabled)"
    exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting in production mode (multiple workers)"
    # Chạy Uvicorn với 4 worker (số lượng worker tùy chỉnh theo tài nguyên)
    exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
```

Script `start.sh` kiểm tra biến môi trường `ENVIRONMENT`:

- Nếu là `development`, chạy Uvicorn với cờ `--reload` để tự động tải lại khi mã nguồn thay đổi (tiện cho việc phát triển).
- Nếu là `production`, chạy Uvicorn với `--workers 4` (4 worker processes) để tận dụng đa nhân CPU, tăng khả năng phục vụ. Bạn có thể điều chỉnh số worker tùy cấu hình máy chủ. (Ngoài ra, trong môi trường production có thể dùng **Gunicorn** kết hợp Uvicorn workers, nhưng ở đây dùng trực tiếp Uvicorn cho đơn giản).

Với Dockerfile này, bạn có thể build hai phiên bản image:

- **Dev image**: `docker build -t myapp:dev --build-arg ENVIRONMENT=development .`
- **Prod image**: `docker build -t myapp:latest --build-arg ENVIRONMENT=production .`

Hoặc chỉ build một image duy nhất và khi chạy container, đặt biến ENVIRONMENT=development để chế độ dev (vì Dockerfile đã gắn ENV default production, nhưng ENTRYPOINT check giá trị runtime).

## 10. docker-compose.yml – Dịch vụ PostgreSQL, Nginx, API server

Tệp **`docker-compose.yml`** định nghĩa cách chạy nhiều container cùng nhau: bao gồm **PostgreSQL** (cơ sở dữ liệu), **API server** (ứng dụng FastAPI chúng ta), và **NGINX** (proxy). Các container này sẽ kết nối với nhau qua mạng nội bộ Docker. Dưới đây là mẫu cấu hình:

```yaml
# docker-compose.yml
version: "3.9"
services:
  db:
    image: postgres:15-alpine
    container_name: fastapi_db
    restart: always
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydatabase
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - fastapi_net

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fastapi_app
    restart: always
    environment:
      ENVIRONMENT: "production" # hoặc "development" tùy mục đích
      DATABASE_URL: "postgresql://myuser:mypassword@db:5432/mydatabase"
      JWT_SECRET_KEY: "your-secret-key" # nên thay bằng khóa thực sự và bảo mật
      LOG_LEVEL: "INFO"
    depends_on:
      - db
    networks:
      - fastapi_net

  nginx:
    image: nginx:latest
    container_name: fastapi_nginx
    restart: always
    ports:
      - "80:80" # Mapped port: truy cập http://localhost:80 sẽ vào Nginx
    volumes:
      - ./app/nginx.conf:/etc/nginx/conf.d/default.conf:ro # Gắn file cấu hình nginx
      - nginx_cache:/var/cache/nginx # Tùy chọn: gắn thư mục cache để giữ cache
    depends_on:
      - api
    networks:
      - fastapi_net

networks:
  fastapi_net:
    driver: bridge

volumes:
  db_data:
  nginx_cache:
```

Giải thích:

- **db (PostgreSQL)**: Sử dụng image Postgres 15 (alpine). Thiết lập user, password, database qua biến môi trường. Volume `db_data` để lưu trữ dữ liệu DB bền vững (giúp dữ liệu không mất khi container restart).
- **api (FastAPI app)**: Sử dụng Dockerfile để build image ứng dụng. Truyền các biến môi trường cần thiết:
  - `ENVIRONMENT`: đặt `"production"` hoặc `"development"` để script start.sh chạy đúng chế độ.
  - `DATABASE_URL`: chuỗi kết nối tới DB Postgres container (sử dụng service name `db` làm hostname).
  - `JWT_SECRET_KEY`: khóa bí mật JWT (cần đặt giá trị mạnh, và có thể khác nhau giữa môi trường).
  - `LOG_LEVEL`: mức log (INFO/DEBUG...).  
    `depends_on: db` đảm bảo container DB khởi động trước.  
    Container **api** join vào mạng `fastapi_net` để có thể giao tiếp với **db** và **nginx**. (Docker sẽ tự tạo DNS tên `db` và `api` cho các container trong cùng network).
- **nginx**: Sử dụng image Nginx chuẩn. Map cổng 80 của host vào cổng 80 container (nghĩa là truy cập máy chủ ở cổng 80 sẽ vào Nginx). Gắn file cấu hình `nginx.conf` từ thư mục `app` của project vào Nginx (dùng `:ro` để chỉ read-only). Gắn thêm volume `nginx_cache` để Nginx có nơi lưu cache proxy (như đã cấu hình trong nginx.conf). `depends_on: api` để Nginx khởi động sau khi app đã sẵn sàng. Tham gia cùng network để có thể truy cập service `api` qua hostname.
- **networks**: Tạo network bridge tùy chỉnh `fastapi_net` cho các service. Tất cả dịch vụ trong cùng network này có thể truy cập nhau qua tên service.
- **volumes**: Khai báo volume `db_data` và `nginx_cache` dùng ở trên. Volume `db_data` giữ dữ liệu Postgres. Volume `nginx_cache` giúp cache Nginx không bị mất nếu container Nginx restart (tùy chọn).

## 11. Hướng dẫn Triển khai và Chạy Ứng dụng

Với các tệp cấu hình và mã nguồn trên, dưới đây là hướng dẫn để triển khai và chạy ứng dụng trong cả môi trường phát triển và sản xuất:

### a. Chuẩn bị Môi trường

- Đảm bảo đã cài **Docker** và **Docker Compose** trên máy của bạn.
- Tạo file `requirements.txt` liệt kê các thư viện Python cần thiết, ví dụ:
  ```text
  fastapi==0.95.2
  uvicorn[standard]==0.22.0
  sqlalchemy==2.0.5
  alembic==1.10.2
  PyJWT==2.6.0
  python-json-logger==2.0.4
  psycopg2-binary==2.9.6
  ```
  (Phiên bản chỉ là minh họa, bạn có thể cập nhật mới hơn. `psycopg2-binary` để SQLAlchemy kết nối PostgreSQL, `PyJWT` để tạo JWT, v.v.)
- (Tuỳ chọn) Tạo file `.env` để lưu các biến môi trường như mật khẩu DB, secret key, v.v., và update docker-compose để load từ `.env` file. Điều này giúp bảo mật thông tin nhạy cảm.

### b. Chạy ứng dụng trong **Môi trường Phát triển** (Development)

1. Đảm bảo mã nguồn trong thư mục `app/` như cấu trúc đã trình bày.
2. Để chạy ở chế độ dev (tự động reload, code hot-reload khi thay đổi):
   - Mở `docker-compose.yml`, đặt biến môi trường `ENVIRONMENT: "development"` cho service **api**.
   - Thêm `volumes` mount mã nguồn để việc thay đổi code bên ngoài được phản ánh trong container:
     ```yaml
     api:
       ...
       volumes:
         - ./app:/app/app  # Gắn thư mục code local vào thư mục /app/app trong container
     ```
     (Lưu ý: Vì trong Dockerfile ta copy code vào `/app/app`, việc mount sẽ đè mã nguồn bằng mã trên host, giúp reload hiệu lực).
   - Chạy lệnh: `docker-compose up --build`  
     Tham số `--build` để build lại image (vì có thể chế độ dev khác với prod). Docker Compose sẽ khởi chạy 3 dịch vụ: db, api, nginx.
   - Kiểm tra log:
     - **fastapi_app**: log của Uvicorn cho thấy ứng dụng khởi động ở chế độ reload (sẽ có thông báo "Starting in development mode (reload enabled)").
     - **fastapi_nginx**: log Nginx cho biết đã start và lắng trên cổng 80.
   - Truy cập thử API: Mở trình duyệt hoặc dùng curl `http://localhost:80/docs` sẽ thấy giao diện tài liệu tương tác Swagger của FastAPI (thông qua Nginx proxy). Bạn có thể thử các endpoint đăng ký, đăng nhập, tạo item ngay trên giao diện này.
   - Thử chỉnh sửa mã (ví dụ, thay đổi nội dung `print` trong startup_event ở main.py) và lưu, Uvicorn (ở chế độ reload) sẽ tự động tải lại ứng dụng.
3. Khi đang phát triển, nếu thay đổi mô hình cơ sở dữ liệu (model), bạn cần tạo migration bằng Alembic:
   - Đầu tiên, khởi tạo Alembic (nếu chưa): `alembic init alembic`. Sửa `alembic.ini` để trỏ đến `DATABASE_URL` phù hợp, và sửa file `env.py` để import `Base` từ `app.database`.
   - Tạo file migration: `alembic revision --autogenerate -m "Description of changes"`
   - Áp dụng migration: `alembic upgrade head`.  
     Khi chạy trong Docker, có thể thực hiện bằng cách: `docker-compose run api alembic upgrade head`.  
     _Lưu ý:_ Trong giai đoạn dev, bạn cũng có thể dùng `Base.metadata.create_all()` (như trong startup_event) để tạo nhanh bảng, nhưng Alembic sẽ quản lý lịch sử schema tốt hơn khi dự án lớn lên.

### c. Triển khai **Production**

1. Đảm bảo cấu hình trong `docker-compose.yml` cho **api** service để `ENVIRONMENT: "production"`. Điều này sẽ khiến container chạy Uvicorn với multiple workers, không có reload. Cũng có thể tắt mount volume code (sử dụng code đã build sẵn trong image để đảm bảo tính ổn định).
2. Thiết lập `JWT_SECRET_KEY` đủ mạnh và an toàn (ví dụ chuỗi random 32 ký tự), không dùng giá trị mặc định. Tương tự, đặt `POSTGRES_PASSWORD` mạnh. Các giá trị này có thể đặt trong biến môi trường hoặc file `.env` trên server.
3. Build và chạy: `docker-compose up --build -d`. Tham số `-d` để chạy dưới nền.
4. Chạy migrations (nếu áp dụng): `docker-compose run --rm api alembic upgrade head` để cập nhật schema DB theo phiên bản mới nhất. (Trong tương lai, có thể tự động hóa bước này bằng cách thêm vào entrypoint của container hoặc dùng tool quản lý).
5. Đảm bảo Nginx container đang lắng nghe trên cổng 80 của host. Bạn có thể cấu hình domain trỏ tới máy chủ và bổ sung `server_name` trong `nginx.conf` cho phù hợp (để phục vụ sản phẩm thật). Nếu cần HTTPS, có thể tích hợp chứng chỉ SSL (sử dụng nginx để terminat SSL hoặc dùng một proxy khác như Traefik, Caddy...).
6. Kiểm tra ứng dụng: Gửi yêu cầu tới các endpoint (qua domain hoặc IP máy chủ) để đảm bảo mọi thứ hoạt động: đăng ký user, đăng nhập lấy token, dùng token để tạo item, v.v. Kiểm tra log container `fastapi_app` (được định dạng JSON) xem có gửi lên hệ thống ELK hay chưa (nếu ELK được cấu hình để lấy log Docker). Kiểm tra Nginx xem có cache response (có thể gửi vài lần request GET /items và xem log hoặc thư mục cache).

### d. Giám sát và Logging

- Trong môi trường production, bạn nên có giải pháp giám sát:
  - **Logging**: Dữ liệu log JSON từ ứng dụng (qua stdout) có thể được thu thập bởi **Elasticsearch** (với Logstash/Fluentd) để theo dõi lỗi và hoạt động. Log từ Nginx cũng nên được thu thập (có thể chỉnh định dạng log Nginx sang JSON hoặc dùng Filebeat).
  - **Metrics**: Triển khai **Prometheus** để thu thập số liệu hiệu năng (số request, độ trễ...). Bạn có thể thêm endpoint `/metrics` vào FastAPI (bằng cách tích hợp **prometheus_client**) và cấu hình Prometheus scrape. Ngoài ra, Prometheus có thể lấy metric từ **PostgreSQL** (nhờ exporter) và **Nginx** (nghiên cứu nginx-prometheus-exporter).
  - **Monitoring**: Sử dụng Grafana để trực quan hóa metrics, Kibana để xem log, và cài cảnh báo (alerts) khi có sự cố (như CPU cao, nhiều lỗi 500...).

### e. Các Bước Bổ Sung

- **Bảo mật**:
  - Sử dụng HTTPS cho Nginx (bắt buộc cho môi trường thực tế). Có thể tích hợp Let's Encrypt cho chứng chỉ SSL tự động.
  - Cài đặt tường lửa cho server, chỉ mở các cổng cần thiết (80/443).
  - Triển khai cơ chế reload/ngưng server không downtime nếu cập nhật (có thể dùng Docker Compose rolling update hoặc Kubernetes nếu tiến xa hơn).
- **Kiểm thử**: Viết các test (ví dụ với `pytest`) để kiểm tra các API (đăng ký, đăng nhập, CRUD item) hoạt động đúng. Có thể tích hợp CI/CD để tự động test và deploy.
- **Tối ưu hóa**: Cân nhắc sử dụng **Gunicorn** kết hợp **Uvicorn workers** cho production để quản lý worker tốt hơn (Gunicorn có cơ chế giám sát worker, tự động restart khi lỗi, v.v.). Trong Dockerfile, bạn có thể thay lệnh chạy bằng: `gunicorn -k uvicorn.workers.UvicornWorker -w 4 app.main:app`.

---

**Tóm lại**, với cấu trúc trên, chúng ta có một ứng dụng FastAPI chuẩn gồm các thành phần: **model** (ORM cho User, Item), **router** (khai báo endpoint), **auth** (JWT), **database** (kết nối DB), **config** (cấu hình), **logger** (logging JSON cho ELK), cùng với cấu hình **Nginx** và container hóa qua **Docker**. Bạn có thể mở rộng thêm tùy nhu cầu (ví dụ thêm endpoint refresh token, phân trang cho danh sách items, v.v.). Triển khai Docker Compose giúp dễ dàng chạy ứng dụng nhất quán trong các môi trường. Chúc bạn thành công trong việc xây dựng ứng dụng FastAPI của mình!

---
### Dev References

- [VSCode FastAPI](https://code.visualstudio.com/docs/python/tutorial-fastapi)

### uv install

- Install [uv](https://docs.astral.sh/uv/) with our official standalone installer:
  Windows:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

- Linux:
  > curl -LsSf https://astral.sh/uv/install.sh | sh
  > or
  > wget -qO- https://astral.sh/uv/install.sh | sh

> source $HOME/.local/bin/env

- Dễ dàng tái tạo: Dùng uv pip freeze > requirements.txt để lưu danh sách gói, sau đó cài lại bằng uv pip install -r requirements.txt.

- Requires Python 3.12 or higher. First, we recommend using uv to setup the Python environment.

> uv venv .venv --python 3.12

or

> uv venv windows --python 3.12

activate virtual python environment

> .venv\Scripts\activate

> uv pip install -r requirements.txt


```
uv pip install alembic PyJWT uvicorn[standard] python-json-logger psycopg2-binary fastapi
```
- Run Server

> python src/server.py

- fastapi

> fastapi run src/main.py

- uvicorn

>  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload