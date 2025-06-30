# SaaS Analytics Dashboard API

🚀 **API mô phỏng dịch vụ Cigro** - Thu thập và phân tích dữ liệu từ cửa hàng online

## 🎯 Tính năng chính

- **📊 Analytics Dashboard**: Tổng quan dữ liệu bán hàng real-time
- **💰 KPI Tracking**: ROAS, tỉ lệ chuyển đổi, doanh thu theo platform
- **🔄 Data Pipeline**: Đồng bộ dữ liệu từ nhiều nguồn (Shopee, Lazada, Facebook Ads)
- **⚡ Redis Cache**: Cache kết quả analytics để tăng tốc độ
- **📈 Real-time Metrics**: Metrics và alerts real-time
- **🔍 Data Quality**: Báo cáo chất lượng dữ liệu
- **🗄️ PostgreSQL**: Database mạnh mẽ cho production

## 🚀 Cách chạy nhanh

### Cách 1: Docker (Khuyến nghị)

```bash
# Chạy với Docker Compose
docker-compose up --build -d

# Hoặc sử dụng script
chmod +x docker-start.sh
./docker-start.sh
```

### Cách 2: Local Development

```bash
# Di chuyển vào thư mục dự án
cd saas-analytics-api

# Kích hoạt virtual environment
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📱 Truy cập API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔗 API Endpoints

### Analytics

- `GET /api/v1/analytics/data-sources` - Danh sách nguồn dữ liệu
- `POST /api/v1/analytics/sync-data` - Đồng bộ dữ liệu
- `GET /api/v1/analytics/real-time-metrics` - Metrics real-time
- `GET /api/v1/analytics/data-quality` - Báo cáo chất lượng dữ liệu

### Sales

- `GET /api/v1/sales/` - Danh sách đơn hàng
- `POST /api/v1/sales/` - Tạo đơn hàng mới
- `GET /api/v1/sales/summary` - Tổng quan bán hàng
- `POST /api/v1/sales/generate-fake-data` - Tạo dữ liệu fake

### KPI

- `GET /api/v1/kpi/roas` - Tính ROAS
- `GET /api/v1/kpi/conversion-rate` - Tỉ lệ chuyển đổi
- `GET /api/v1/kpi/revenue-summary` - Tổng quan doanh thu
- `GET /api/v1/kpi/platform-performance` - Hiệu suất platform
- `GET /api/v1/kpi/dashboard` - Dữ liệu dashboard

### Cache

- `GET /api/v1/cache/status` - Trạng thái cache
- `DELETE /api/v1/cache/clear` - Xóa tất cả cache
- `GET /api/v1/cache/keys` - Danh sách cache keys

## 🧪 Test API

1. **Tạo dữ liệu fake**:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/sales/generate-fake-data"
   ```

2. **Xem dashboard**:

   ```bash
   curl "http://localhost:8000/api/v1/kpi/dashboard"
   ```

3. **Tính ROAS**:
   ```bash
   curl "http://localhost:8000/api/v1/kpi/roas?platform=shopee"
   ```

## 🛠️ Công nghệ sử dụng

- **FastAPI** - Web framework
- **PostgreSQL** - Database chính
- **Redis** - Cache
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 📊 Database Schema

### SalesData

- `id` - Primary key
- `order_id` - ID đơn hàng (unique)
- `customer_id` - ID khách hàng
- `product_name` - Tên sản phẩm
- `quantity` - Số lượng
- `unit_price` - Đơn giá
- `total_amount` - Tổng tiền
- `platform` - Platform (shopee, lazada, tiktok)
- `campaign_id` - ID chiến dịch quảng cáo
- `ad_cost` - Chi phí quảng cáo
- `created_at` - Thời gian tạo
- `updated_at` - Thời gian cập nhật

### AdCampaign

- `id` - Primary key
- `campaign_id` - ID chiến dịch (unique)
- `campaign_name` - Tên chiến dịch
- `platform` - Platform
- `budget` - Ngân sách
- `spent` - Đã chi
- `impressions` - Lượt hiển thị
- `clicks` - Lượt click
- `conversions` - Lượt chuyển đổi
- `start_date` - Ngày bắt đầu
- `end_date` - Ngày kết thúc
- `status` - Trạng thái
- `created_at` - Thời gian tạo

## 🔧 Cấu hình

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://admin:admin123@postgres:5432/saas_analytics

# Redis
REDIS_URL=redis://redis:6379
```

### Docker Services

- **PostgreSQL**: Port 5432
- **Redis**: Port 6379
- **FastAPI**: Port 8000

## 📈 KPI được tính toán

- **ROAS** (Return on Ad Spend) = Doanh thu / Chi phí quảng cáo
- **Tỉ lệ chuyển đổi** = Số đơn hàng / Số lượt click
- **Doanh thu trung bình** = Tổng doanh thu / Số đơn hàng
- **Hiệu suất platform** = Doanh thu theo từng platform

## 🚨 Lưu ý

- Sử dụng PostgreSQL cho production
- Redis cần được cài đặt và chạy để cache hoạt động
- Dữ liệu fake được tạo để test API
- Các metrics real-time được giả lập
- Database data được persist qua Docker volumes

## 🤝 Đóng góp

1. Fork dự án
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request
