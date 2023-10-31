## Hướng dẫn tải về và sử dụng Big Data WebApp (demo) và API
### Bước 1: Tải về source code Docker
```
git clone https://github.com/tamngco/bigdata_webapp_and_api.git
```
### Step 2:Chuẩn bị dữ liệu
- Tải về dữ liệu Logistics tại: https://drive.google.com/drive/folders/1EoWVyDO4Iokex_uqLvPwYyf9uP49NK9T?usp=sharing
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
- Tải về database tại đây: https://drive.google.com/drive/folders/1EzoNTRPcsjf17EDU0wPY-0mT_iM_Zn0F?usp=sharing
  - Sau khi tải về, bạn sẽ có 01 file: logistic_data_FN_Oct04.csv
- Sử dụng một công cụ quản lý database (vd: DBeaver) để restore file CSV vừa tải về vào database có tên là **logistics_bi**
  - Expand logistics_bi -> Tables
  - Chuột phải lên Tables -> Chọn **Import Data**
  - Browse file logistic_data_FN_Oct04.csv, click Next -> Proceed

### Step 5: Setup Superset
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

  - Khởi tạo superset
```
docker exec -it superset-app superset init
```

  - Cài đặt plugin kết nối superset với Clickhouse
```
pip install clickhouse-connect
```

- Khởi động lại container của superset để plugin hiệu lực
```
docker restart superset-app
```
- Đăng nhập vào superset:
  - Truy cập: http://localhost:8088
  - Đăng nhập với user là **admin**, pass là **admin**
 
- Restore dashboard
  - Vào tab **Dashboard**, chọn biểu tượng **Import** (mũi tên chỉ xuống) và browse file dashboards.zip trong thư mục ./superset/dashboard-to-import
  - Bấm nút **Import** và chờ dashboard được import xong.

- Bấm vào [Logistics_dashboard] để xem.

### Hướng dẫn demo
## Load dữ liệu từ Apache Nifi vào Data Lake (lớp Bronze)
- Truy cập Apache Nifi tại địa chỉ: https://localhost:8443/nifi/login
  - Đăng nhập với user là **admin**, pass là **Password123qwe**
  - Nhấn chuột phải vào processor **ExecuteSQL** chọn **Run once** (chờ cho đến khi Out của PutS3Object hiển thị số 1 là thành công)

## Transform dữ liệu từ Bronze -> Silver
- Chạy dòng lệnh:
```
docker exec -it spark_master spark-submit /dev/scripts/airflow_bronze_to_silver.py
```

## Transform dữ liệu từ Silver -> Gold
- Chạy dòng lệnh:
```
docker exec -it spark_master spark-submit /dev/scripts/airflow_silver_to_gold.py
```

## Kiểm tra dữ liệu trong Data Lake
- Truy cập MinIO Object Storage tại: http://localhost:9001/login
- Đăng nhập với user là **minioadmin**, pass là **minioadmin**
- Xem các bucket: Bronze, Silver, Gold, MLModel

## Load dữ liệu từ Gold sang Clickhouse
- Truy cập Airflow tại địa chỉ: http://localhost:8085
- Đăng nhập với user là **airflow**, pass là **airflow**
- Chọn DAG **Gold To ClickHouse** và bấm **Trigger DAG** (biểu tượng Play)

## Sử dụng Dashboard
- Truy cập superset tại địa chỉ: http://localhost:8088
- Đăng nhập với user là **admin**, pass là **admin**

## Truy cập ứng dụng Thương mại điện tử (demo)
- Truy cập tại địa chỉ: http://localhost:82
- Bấm nút **Tính toán thời gian giao hàng**

### Mọi thắc mắc vui lòng email về: tamgr.nguyen@gmail.com
