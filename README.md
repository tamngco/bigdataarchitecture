## Hướng dẫn tải về và sử dụng Big Data WebApp (demo) và API
### Bước 1: Tải về source code Docker
```
git clone https://github.com/tamngco/bigdata_webapp_and_api.git
```
### Step 2:Chuẩn bị dữ liệu
- Tải về dữ liệu Logistics tại: https://drive.google.com/drive/folders/1X3RFIvtMTrzpKYakYzLGeuNwumThGlgB?usp=sharing
  - Sau khi tải về, bạn sẽ có 02 files:
    logistics.mdf và logistics_log.ldf
- Copy 02 file này vào thư mục docker:
    ./sqlserver/data

### Step 3: Run
- Chạy docker với dòng lệnh:
```
docker-compose up
```
### Step 4: Restore dữ liệu Clickhouse


### Setup Superset
- Trong command prompt, chạy các lệnh sau:
  - Tạo tài khoản và phân quyền cho admin: (username: admin; password: admin)
```
docker exec -it superset-app superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin
```
  - Nâng cấp db của Superset lên phiên bản mới nhất
```
docker exec -it superset-app superset db upgrade
```

  - Load một số các template mẫu
```
docker exec -it superset-app superset load_examples
```

  - Khởi tạo superset
```
docker exec -it superset-app superset init
```

  - Cài đặt plugin kết nối superset với Clickhouse
```
pip install clickhouse-connect
```

### Step 4: Truy cập và dùng thử ứng dụng Thương mại điện tử (demo)
- WebApp Demo: http://localhost:82
