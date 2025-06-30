# SaaS Analytics API (Phiên bản thực tế theo code)

## 🎯 Tính năng chính

- Đăng ký, đăng nhập, xác thực người dùng (JWT)
- Quản lý dữ liệu bán hàng (SalesData)
- Tổng hợp doanh thu, chi tiêu quảng cáo, ROAS
- Thống kê top user theo doanh thu
- **Structured Logging** với request tracking
- **Health Check & Monitoring** system metrics
- **Redis Caching** với cache hit/miss logging

## 🚀 Hướng dẫn chạy

### 1. Local Development

```bash
cd saas-analytics-api
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📱 Truy cập API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Auth

- `POST /register` - Đăng ký tài khoản
- `POST /login` - Đăng nhập, trả về access token
- `GET /me` - Lấy thông tin user hiện tại

### Sales

- `POST /sales-data/` - Tạo dữ liệu bán hàng mới (yêu cầu xác thực)
- `GET /sales-data/` - Lấy danh sách dữ liệu bán hàng
- `POST /sales-data/generate-fake` - Tạo dữ liệu fake để test (tham số: count)

### Analytics

- `GET /analytics/summary` - Tổng hợp doanh thu, chi tiêu, ROAS (yêu cầu xác thực)
- `GET /analytics/top_users` - Top user theo doanh thu (yêu cầu xác thực)

### Health Check & Monitoring

- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed health check (DB + Redis)
- `GET /health/metrics` - System metrics (CPU, Memory, Disk, Network)
- `GET /health/redis-info` - Redis performance metrics

## 🗄️ Database Models

### User

- `id`: int, primary key
- `email`: string, unique
- `hashed_password`: string

### Store

- `id`: int, primary key
- `name`: string
- `owner_id`: int (liên kết User)

### SalesData

- `id`: int, primary key
- `date`: date
- `revenue`: float
- `ad_spend`: float
- `store_id`: int (liên kết Store)
- `user_id`: int (liên kết User)

## 📦 Schema (Pydantic)

### UserCreate, UserLogin, UserOut

- `email`: EmailStr
- `password`: str (chỉ với UserCreate/UserLogin)
- `id`: int (chỉ với UserOut)

### SalesDataCreate, SalesDataOut

- `date`: date
- `revenue`: float
- `ad_spend`: float
- `store_id`: int
- `user_id`: int
- `id`: int (chỉ với SalesDataOut)

### SummaryResponse

- `total_revenue`: float
- `total_ad_spend`: float
- `roas`: float

### TopUserResponse

- `user_id`: int
- `email`: str
- `total_revenue`: float

## 🛠️ Công nghệ sử dụng

### Backend & API

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM với advanced indexing
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Database & Caching

- **PostgreSQL** - Primary database với performance optimization
- **Redis** - Caching layer và session management

### DevOps & Infrastructure

- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Pytest** - Comprehensive testing framework

### Data & Analytics

- **Pandas & Numpy** - Data processing
- **Faker** - Test data generation

### Monitoring & Orchestration

- **Structlog** - Structured logging system
- **Psutil** - System metrics monitoring
- **Prefect 2.0** - Modern workflow orchestration (Industry standard)
- **ETL Pipelines** - Automated data processing workflows

### Security & Auth

- **JWT** - Token-based authentication
- **Bcrypt** - Password hashing
- **OAuth2** - Security scheme

## 🧪 Test API

### 1. Tạo dữ liệu fake để test

```bash
# Tạo 50 record fake (mặc định)
curl -X POST "http://localhost:8000/sales-data/generate-fake"

# Tạo 100 record fake
curl -X POST "http://localhost:8000/sales-data/generate-fake?count=100"
```

### 2. Xem tổng hợp analytics

```bash
# Cần đăng nhập trước để lấy token
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_email@example.com&password=your_password"

# Sau đó dùng token để xem analytics
curl -X GET "http://localhost:8000/analytics/summary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Kiểm tra health check và monitoring

```bash
# Basic health check
curl "http://localhost:8000/health/"

# Detailed health check (kiểm tra DB + Redis)
curl "http://localhost:8000/health/detailed"

# System metrics
curl "http://localhost:8000/health/metrics"

# Redis performance
curl "http://localhost:8000/health/redis-info"
```

## 📝 Logging Features

- **Request/Response Logging**: Mỗi API call được log với request ID, response time
- **Database Operation Logging**: Track CRUD operations với performance metrics
- **Cache Logging**: Log cache hits/misses với query times
- **Error Logging**: Structured error logs với stack traces
- **System Monitoring**: CPU, memory, disk usage tracking

## 🔄 Prefect Orchestration Features

### **Tính năng chính của Prefect:**

- ✅ **Modern Python-first design** - Không cần XML/YAML config
- ✅ **Dynamic workflows** - Flow có thể thay đổi runtime
- ✅ **Better observability** - Real-time monitoring và UI hiện đại
- ✅ **Cloud-native** - Dễ deploy và scale trên cloud
- ✅ **Enhanced error handling** - Automatic retry và recovery
- ✅ **Faster development** - Nhanh hơn trong việc develop và test

### **Workflows đã implement:**

#### 1. **Daily Analytics ETL Pipeline**

```
Extract → Transform → Load → Report
   ↓         ↓         ↓       ↓
Database  Pandas   Redis   Insights
```

- **Extract**: Lấy dữ liệu từ PostgreSQL
- **Transform**: Xử lý với Pandas (aggregations, metrics)
- **Load**: Cache vào Redis với TTL
- **Report**: Generate insights và recommendations

#### 2. **Data Quality Check Flow**

- Validate data consistency
- Check data freshness (7 days)
- Monitor record counts
- Alert on quality issues

### **Prefect API Endpoints:**

- `GET /prefect/flows/status` - Thông tin workflows
- `POST /prefect/flows/daily-etl/run` - Trigger ETL pipeline
- `POST /prefect/flows/data-quality/run` - Run quality checks
- `GET /prefect/analytics/cached` - Analytics từ Prefect ETL
- `GET /prefect/monitoring/system` - Prefect system info

### **Setup Prefect:**

```bash
# Chạy setup script
python scripts/setup_prefect.py

# Hoặc manual setup
pip install prefect==2.14.0
prefect server start --host 0.0.0.0
prefect worker start --pool analytics-pool
```

### **Prefect UI Dashboard:**

- 📊 **URL**: http://localhost:4200
- 🔍 **Features**: Flow runs, task monitoring, logs, scheduling

---
