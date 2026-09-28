import streamlit as st
import mysql.connector
from mysql.connector import Error, errorcode
import pandas as pd
from datetime import date, datetime


# ============================================================
# CẤU HÌNH STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Quản lý Tour Du lịch",
    page_icon="🚌",
    layout="wide"
)


# ============================================================
# CẤU HÌNH MYSQL AIVEN
# ============================================================

# Thông tin kết nối lấy trực tiếp từ Aiven.
DB_CONFIG = {
    "host": "mysql-25a34fbe-ngctruc5-4830.e.aivencloud.com",
    "port": 26716,
    "database": "defaultdb",
    "user": "avnadmin",
    "password": "AVNS_1JPNssDgmO_BqXf9Rmf",
    "ssl_disabled": False,
    "connection_timeout": 15,
}


# ============================================================
# KẾT NỐI DATABASE
# ============================================================

def get_connection():
    """
    Tạo một kết nối MySQL mới.
    Không giữ connection toàn cục để tránh lỗi connection cũ
    khi Streamlit chạy lại ứng dụng.
    """
    return mysql.connector.connect(**DB_CONFIG)


def test_connection():
    """Kiểm tra kết nối Aiven MySQL."""
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True, "Kết nối MySQL Aiven thành công."

    except Error as e:
        return False, str(e)

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass

        try:
            if conn:
                conn.close()
        except Exception:
            pass


# ============================================================
# HÀM DATABASE
# ============================================================

def get_data(query, params=()):
    """Đọc dữ liệu MySQL và trả về DataFrame."""
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass

        try:
            if conn:
                conn.close()
        except Exception:
            pass


def execute_query(query, params=()):
    """Thực thi INSERT / UPDATE / DELETE."""
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)
        conn.commit()

        return cursor.lastrowid

    except Exception:
        if conn:
            conn.rollback()
        raise

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass

        try:
            if conn:
                conn.close()
        except Exception:
            pass


# ============================================================
# TẠO DATABASE / BẢNG
# ============================================================

def init_database():
    """
    Tạo các bảng nếu chưa tồn tại.

    Lưu ý:
    - MySQL không cho TEXT DEFAULT.
    - Các cột trạng thái dùng VARCHAR(100).
    """

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # BẢNG TOUR
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tours (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ma_tour VARCHAR(50) NOT NULL UNIQUE,
                ten_tour VARCHAR(255) NOT NULL,
                diem_den VARCHAR(255) NOT NULL,
                thoi_gian VARCHAR(100),
                so_ngay INT DEFAULT 1,
                ngay_khoi_hanh VARCHAR(100),
                ngay_ket_thuc VARCHAR(100),
                so_cho INT DEFAULT 0,
                gia_tour DECIMAL(15,2) DEFAULT 0,
                huong_dan_vien VARCHAR(255),
                trang_thai VARCHAR(100) DEFAULT 'Đang hoạt động',
                mo_ta TEXT,
                ngay_tao DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ----------------------------------------------------
        # BẢNG KHÁCH HÀNG
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ma_khach VARCHAR(50) NOT NULL UNIQUE,
                ho_ten VARCHAR(255) NOT NULL,
                so_dien_thoai VARCHAR(50),
                email VARCHAR(255),
                dia_chi TEXT,
                ngay_tao DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ----------------------------------------------------
        # BẢNG ĐẶT TOUR
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ma_dat_tour VARCHAR(50) NOT NULL UNIQUE,
                ma_tour VARCHAR(50) NOT NULL,
                ma_khach VARCHAR(50) NOT NULL,
                so_nguoi INT DEFAULT 1,
                tong_tien DECIMAL(15,2) DEFAULT 0,
                ngay_dat DATE,
                trang_thai VARCHAR(100) DEFAULT 'Chờ xác nhận',
                ghi_chu TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ----------------------------------------------------
        # TỰ SỬA CỘT trang_thai NẾU DATABASE CŨ TỪNG DÙNG TEXT
        # ----------------------------------------------------

        for table_name, default_value in [
            ("tours", "Đang hoạt động"),
            ("bookings", "Chờ xác nhận"),
        ]:
            cursor.execute(
                """
                SELECT DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = %s
                  AND COLUMN_NAME = 'trang_thai'
                """,
                (DB_CONFIG["database"], table_name)
            )

            row = cursor.fetchone()

            if row and row[0].lower() in ("text", "tinytext", "mediumtext", "longtext", "blob"):
                cursor.execute(
                    f"""
                    ALTER TABLE `{table_name}`
                    MODIFY COLUMN trang_thai VARCHAR(100)
                    DEFAULT %s
                    """,
                    (default_value,)
                )

        conn.commit()

        # ----------------------------------------------------
        # DỮ LIỆU TOUR CÓ SẴN
        # ----------------------------------------------------

        tours_data = [
            (
                "DL001",
                "Đà Lạt 3N3Đ (Xe giường nằm)",
                "Đà Lạt",
                "3 ngày 3 đêm",
                3,
                "01/10/2026",
                "04/10/2026",
                40,
                2090000,
                "",
                "Đang hoạt động",
                """🚌 Phương tiện: Xe giường nằm

🗓 Khởi hành: Tối 01/10 (Thứ 5)

💰 Giá chỉ: 2.090.000đ"""
            ),
            (
                "PT001",
                "Phan Thiết 2N1Đ (Xe ghế)",
                "Phan Thiết",
                "2 ngày 1 đêm",
                2,
                "03/10/2026",
                "04/10/2026",
                40,
                1650000,
                "",
                "Đang hoạt động",
                """🚌 Phương tiện: Xe ghế

🗓 Khởi hành: Sáng 03/10 (Thứ 7)

💰 Giá chỉ từ: 1.650.000đ"""
            ),
            (
                "MT001",
                "Miền Tây 2N1Đ (Xe ghế)",
                "Miền Tây",
                "2 ngày 1 đêm",
                2,
                "Hàng ngày",
                "Hàng ngày",
                40,
                1590000,
                "",
                "Đang hoạt động",
                """🚌 Phương tiện: Xe ghế

🗓 Khởi hành: Hàng ngày

💰 Giá chỉ từ: 1.590.000đ"""
            ),
            (
                "MT002",
                "Miền Tây 1N (Xe ghế)",
                "Miền Tây",
                "1 ngày",
                1,
                "Hàng ngày",
                "Hàng ngày",
                40,
                500000,
                "",
                "Đang hoạt động",
                """🚌 Phương tiện: Xe ghế

🗓 Khởi hành: Hàng ngày

💰 Giá chỉ từ: 500.000đ"""
            ),
            (
                "TN001",
                "Tây Ninh - Buffet Trưa - Đỉnh Vân Sơn 1N",
                "Tây Ninh",
                "1 ngày",
                1,
                "Thứ 2 - Chủ nhật",
                "Trong ngày",
                40,
                890000,
                "",
                "Đang hoạt động",
                """🛕 Tây Ninh - Buffet Trưa - Đỉnh Vân Sơn 1N

📆 Khởi hành:

• Sáng thứ 2 đến thứ 5:
💸 Giá 890.000đ
Chưa bao gồm Buffet

• Sáng thứ 6, thứ 7, chủ nhật:
💸 Giá 1.090.000đ"""
            )
        ]

        for tour in tours_data:
            cursor.execute(
                """
                SELECT id
                FROM tours
                WHERE ma_tour = %s
                """,
                (tour[0],)
            )

            exists = cursor.fetchone()

            if exists is None:
                cursor.execute(
                    """
                    INSERT INTO tours (
                        ma_tour,
                        ten_tour,
                        diem_den,
                        thoi_gian,
                        so_ngay,
                        ngay_khoi_hanh,
                        ngay_ket_thuc,
                        so_cho,
                        gia_tour,
                        huong_dan_vien,
                        trang_thai,
                        mo_ta,
                        ngay_tao
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        tour[0],
                        tour[1],
                        tour[2],
                        tour[3],
                        tour[4],
                        tour[5],
                        tour[6],
                        tour[7],
                        tour[8],
                        tour[9],
                        tour[10],
                        tour[11],
                        datetime.now()
                    )
                )

        conn.commit()

        return True, "Database và dữ liệu mẫu đã sẵn sàng."

    except Error as e:
        if conn:
            conn.rollback()
        return False, str(e)

    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass

        try:
            if conn:
                conn.close()
        except Exception:
            pass


# ============================================================
# KHỞI TẠO DATABASE
# ============================================================

db_ok, db_message = init_database()

if not db_ok:
    st.error("❌ Không thể kết nối hoặc khởi tạo MySQL Aiven.")
    st.code(db_message)

    st.info(
        "Hãy kiểm tra Aiven đang ở trạng thái RUNNING, "
        "máy tính có Internet và đã cài mysql-connector-python."
    )

    st.stop()


# ============================================================
# HÀM HỖ TRỢ
# ============================================================

def format_money(value):
    if value is None or pd.isna(value):
        return "0đ"

    return f"{float(value):,.0f}đ"


def safe_text(value):
    if value is None or pd.isna(value):
        return ""
    return str(value)


def get_tour_label(tours, code):
    row = tours[tours["ma_tour"] == code]

    if row.empty:
        return code

    return f"{code} - {row.iloc[0]['ten_tour']}"


def get_customer_label(customers, code):
    row = customers[customers["ma_khach"] == code]

    if row.empty:
        return code

    return f"{code} - {row.iloc[0]['ho_ten']}"


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 32px;
    font-weight: bold;
}

.sub-title {
    color: #666;
    margin-bottom: 20px;
}

.tour-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    margin-bottom: 15px;
    background-color: #ffffff;
}

.tour-name {
    font-size: 20px;
    font-weight: bold;
}

.tour-price {
    font-size: 22px;
    font-weight: bold;
}

.db-ok {
    color: #00a86b;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🚌 QUẢN LÝ TOUR")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "CHỨC NĂNG",
    [
        "🏠 Trang chủ",
        "🗺️ Quản lý Tour",
        "👥 Khách hàng",
        "📋 Đặt Tour",
        "📊 Thống kê",
        "ℹ️ Thông tin"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    '<div class="db-ok">🟢 MySQL Aiven: Đã kết nối</div>',
    unsafe_allow_html=True
)

st.sidebar.caption("Hệ thống quản lý tour du lịch")
st.sidebar.caption("Python + Streamlit + MySQL + Aiven")


# ============================================================
# TRANG CHỦ
# ============================================================

if menu == "🏠 Trang chủ":

    st.markdown(
        '<div class="main-title">🚌 HỆ THỐNG QUẢN LÝ TOUR DU LỊCH</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Quản lý tour - khách hàng - đặt tour - doanh thu'
        '</div>',
        unsafe_allow_html=True
    )

    tours = get_data("SELECT * FROM tours")
    customers = get_data("SELECT * FROM customers")
    bookings = get_data("SELECT * FROM bookings")

    total_tours = len(tours)

    active_tours = len(
        tours[tours["trang_thai"] == "Đang hoạt động"]
    )

    total_customers = len(customers)
    total_bookings = len(bookings)

    revenue = 0

    if not bookings.empty:
        revenue = bookings[
            bookings["trang_thai"].isin(
                ["Đã xác nhận", "Đã hoàn thành"]
            )
        ]["tong_tien"].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🗺️ Tổng tour", total_tours)
    c2.metric("✅ Tour hoạt động", active_tours)
    c3.metric("👥 Khách hàng", total_customers)
    c4.metric("💰 Doanh thu", format_money(revenue))

    st.markdown("---")

    st.subheader("⭐ TOUR ĐANG CÓ")

    active = tours[
        tours["trang_thai"] == "Đang hoạt động"
    ]

    for i in range(0, len(active), 2):

        cols = st.columns(2)

        for j in range(2):

            index = i + j

            if index >= len(active):
                continue

            tour = active.iloc[index]

            with cols[j]:

                st.markdown(
                    f"""
                    <div class="tour-card">

                    <div class="tour-name">
                    🚌 {safe_text(tour['ten_tour'])}
                    </div>

                    <br>

                    📍 <b>Điểm đến:</b>
                    {safe_text(tour['diem_den'])}

                    <br><br>

                    ⏱️ <b>Thời gian:</b>
                    {safe_text(tour['thoi_gian'])}

                    <br><br>

                    🗓️ <b>Khởi hành:</b>
                    {safe_text(tour['ngay_khoi_hanh'])}

                    <br><br>

                    <div class="tour-price">
                    💰 {format_money(tour['gia_tour'])}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander("Xem thông tin tour"):
                    st.write(safe_text(tour["mo_ta"]))


# ============================================================
# QUẢN LÝ TOUR
# ============================================================

elif menu == "🗺️ Quản lý Tour":

    st.title("🗺️ QUẢN LÝ TOUR")

    tab1, tab2, tab3 = st.tabs(
        ["📋 Danh sách", "➕ Thêm tour", "✏️ Sửa / Xóa"]
    )

    # ========================================================
    # DANH SÁCH
    # ========================================================

    with tab1:

        tours = get_data(
            "SELECT * FROM tours ORDER BY id DESC"
        )

        search = st.text_input(
            "🔎 Tìm kiếm",
            placeholder="Nhập mã tour, tên tour hoặc điểm đến..."
        )

        if search:
            tours = tours[
                tours["ma_tour"].astype(str).str.contains(
                    search, case=False, na=False
                )
                |
                tours["ten_tour"].astype(str).str.contains(
                    search, case=False, na=False
                )
                |
                tours["diem_den"].astype(str).str.contains(
                    search, case=False, na=False
                )
            ]

        if not tours.empty:

            display = tours[
                [
                    "ma_tour",
                    "ten_tour",
                    "diem_den",
                    "thoi_gian",
                    "ngay_khoi_hanh",
                    "so_cho",
                    "gia_tour",
                    "trang_thai"
                ]
            ].copy()

            display["gia_tour"] = display["gia_tour"].apply(
                format_money
            )

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("Không tìm thấy tour.")

    # ========================================================
    # THÊM TOUR
    # ========================================================

    with tab2:

        st.subheader("➕ Thêm tour mới")

        with st.form("add_tour"):

            col1, col2 = st.columns(2)

            with col1:

                ma_tour = st.text_input("Mã tour *")
                ten_tour = st.text_input("Tên tour *")
                diem_den = st.text_input("Điểm đến *")
                thoi_gian = st.text_input("Thời gian")

                so_ngay = st.number_input(
                    "Số ngày",
                    min_value=1,
                    value=1
                )

                gia_tour = st.number_input(
                    "Giá tour",
                    min_value=0,
                    value=0,
                    step=100000
                )

            with col2:

                ngay_khoi_hanh = st.text_input(
                    "Ngày khởi hành",
                    placeholder="VD: Hàng ngày hoặc 01/10/2026"
                )

                ngay_ket_thuc = st.text_input(
                    "Ngày kết thúc",
                    placeholder="VD: 04/10/2026"
                )

                so_cho = st.number_input(
                    "Số chỗ",
                    min_value=1,
                    value=40
                )

                huong_dan_vien = st.text_input(
                    "Hướng dẫn viên"
                )

                trang_thai = st.selectbox(
                    "Trạng thái",
                    [
                        "Đang hoạt động",
                        "Tạm dừng",
                        "Đã kết thúc"
                    ]
                )

                mo_ta = st.text_area("Thông tin tour")

            submit = st.form_submit_button(
                "💾 LƯU TOUR",
                use_container_width=True
            )

            if submit:

                if not ma_tour or not ten_tour or not diem_den:
                    st.error(
                        "Vui lòng nhập đầy đủ các trường bắt buộc."
                    )

                else:

                    try:

                        execute_query(
                            """
                            INSERT INTO tours (
                                ma_tour,
                                ten_tour,
                                diem_den,
                                thoi_gian,
                                so_ngay,
                                ngay_khoi_hanh,
                                ngay_ket_thuc,
                                so_cho,
                                gia_tour,
                                huong_dan_vien,
                                trang_thai,
                                mo_ta,
                                ngay_tao
                            )
                            VALUES (
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s
                            )
                            """,
                            (
                                ma_tour,
                                ten_tour,
                                diem_den,
                                thoi_gian,
                                so_ngay,
                                ngay_khoi_hanh,
                                ngay_ket_thuc,
                                so_cho,
                                gia_tour,
                                huong_dan_vien,
                                trang_thai,
                                mo_ta,
                                datetime.now()
                            )
                        )

                        st.success("✅ Thêm tour thành công!")
                        st.rerun()

                    except Error as e:

                        if e.errno == errorcode.ER_DUP_ENTRY:
                            st.error("❌ Mã tour đã tồn tại.")
                        else:
                            st.error(f"❌ Không thể thêm tour: {e}")

    # ========================================================
    # SỬA / XÓA
    # ========================================================

    with tab3:

        tours = get_data(
            "SELECT * FROM tours ORDER BY id"
        )

        if tours.empty:

            st.info("Chưa có tour.")

        else:

            selected_id = st.selectbox(
                "Chọn tour",
                tours["id"].tolist(),
                format_func=lambda x: get_tour_label(
                    tours,
                    tours.loc[tours["id"] == x, "ma_tour"].iloc[0]
                )
            )

            tour = tours[
                tours["id"] == selected_id
            ].iloc[0]

            status_options = [
                "Đang hoạt động",
                "Tạm dừng",
                "Đã kết thúc"
            ]

            current_status = safe_text(
                tour["trang_thai"]
            )

            status_index = (
                status_options.index(current_status)
                if current_status in status_options
                else 0
            )

            with st.form("edit_tour"):

                ma = st.text_input(
                    "Mã tour",
                    value=safe_text(tour["ma_tour"])
                )

                ten = st.text_input(
                    "Tên tour",
                    value=safe_text(tour["ten_tour"])
                )

                diem = st.text_input(
                    "Điểm đến",
                    value=safe_text(tour["diem_den"])
                )

                thoi_gian_edit = st.text_input(
                    "Thời gian",
                    value=safe_text(tour["thoi_gian"])
                )

                gia = st.number_input(
                    "Giá tour",
                    min_value=0.0,
                    value=float(tour["gia_tour"] or 0),
                    step=100000.0
                )

                so_cho_edit = st.number_input(
                    "Số chỗ",
                    min_value=1,
                    value=int(tour["so_cho"] or 1)
                )

                khoi_hanh = st.text_input(
                    "Ngày khởi hành",
                    value=safe_text(tour["ngay_khoi_hanh"])
                )

                ket_thuc = st.text_input(
                    "Ngày kết thúc",
                    value=safe_text(tour["ngay_ket_thuc"])
                )

                hdv = st.text_input(
                    "Hướng dẫn viên",
                    value=safe_text(tour["huong_dan_vien"])
                )

                status = st.selectbox(
                    "Trạng thái",
                    status_options,
                    index=status_index
                )

                mota = st.text_area(
                    "Thông tin tour",
                    value=safe_text(tour["mo_ta"])
                )

                col1, col2 = st.columns(2)

                update = col1.form_submit_button(
                    "💾 CẬP NHẬT",
                    use_container_width=True
                )

                delete = col2.form_submit_button(
                    "🗑️ XÓA TOUR",
                    use_container_width=True
                )

                if update:

                    try:

                        execute_query(
                            """
                            UPDATE tours
                            SET
                                ma_tour = %s,
                                ten_tour = %s,
                                diem_den = %s,
                                thoi_gian = %s,
                                ngay_khoi_hanh = %s,
                                ngay_ket_thuc = %s,
                                so_cho = %s,
                                gia_tour = %s,
                                huong_dan_vien = %s,
                                trang_thai = %s,
                                mo_ta = %s
                            WHERE id = %s
                            """,
                            (
                                ma,
                                ten,
                                diem,
                                thoi_gian_edit,
                                khoi_hanh,
                                ket_thuc,
                                so_cho_edit,
                                gia,
                                hdv,
                                status,
                                mota,
                                selected_id
                            )
                        )

                        st.success("✅ Cập nhật tour thành công!")
                        st.rerun()

                    except Error as e:

                        if e.errno == errorcode.ER_DUP_ENTRY:
                            st.error("❌ Mã tour đã tồn tại.")
                        else:
                            st.error(f"❌ Không thể cập nhật: {e}")

                if delete:

                    try:

                        execute_query(
                            """
                            DELETE FROM tours
                            WHERE id = %s
                            """,
                            (selected_id,)
                        )

                        st.success("🗑️ Đã xóa tour.")
                        st.rerun()

                    except Error as e:
                        st.error(f"❌ Không thể xóa tour: {e}")


# ============================================================
# KHÁCH HÀNG
# ============================================================

elif menu == "👥 Khách hàng":

    st.title("👥 QUẢN LÝ KHÁCH HÀNG")

    tab1, tab2 = st.tabs(
        ["📋 Danh sách", "➕ Thêm khách hàng"]
    )

    # --------------------------------------------------------
    # DANH SÁCH
    # --------------------------------------------------------

    with tab1:

        customers = get_data(
            """
            SELECT *
            FROM customers
            ORDER BY id DESC
            """
        )

        if not customers.empty:

            st.dataframe(
                customers[
                    [
                        "ma_khach",
                        "ho_ten",
                        "so_dien_thoai",
                        "email",
                        "dia_chi"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("Chưa có khách hàng.")

    # --------------------------------------------------------
    # THÊM
    # --------------------------------------------------------

    with tab2:

        with st.form("customer_form"):

            ma_khach = st.text_input("Mã khách hàng *")
            ho_ten = st.text_input("Họ và tên *")
            so_dien_thoai = st.text_input("Số điện thoại")
            email = st.text_input("Email")
            dia_chi = st.text_area("Địa chỉ")

            submit = st.form_submit_button(
                "💾 LƯU KHÁCH HÀNG",
                use_container_width=True
            )

            if submit:

                if not ma_khach or not ho_ten:

                    st.error(
                        "Vui lòng nhập mã khách hàng và họ tên."
                    )

                else:

                    try:

                        execute_query(
                            """
                            INSERT INTO customers (
                                ma_khach,
                                ho_ten,
                                so_dien_thoai,
                                email,
                                dia_chi,
                                ngay_tao
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                ma_khach,
                                ho_ten,
                                so_dien_thoai,
                                email,
                                dia_chi,
                                datetime.now()
                            )
                        )

                        st.success(
                            "✅ Thêm khách hàng thành công!"
                        )
                        st.rerun()

                    except Error as e:

                        if e.errno == errorcode.ER_DUP_ENTRY:
                            st.error(
                                "❌ Mã khách hàng đã tồn tại."
                            )
                        else:
                            st.error(
                                f"❌ Không thể thêm khách hàng: {e}"
                            )


# ============================================================
# ĐẶT TOUR
# ============================================================

elif menu == "📋 Đặt Tour":

    st.title("📋 QUẢN LÝ ĐẶT TOUR")

    tours = get_data(
        """
        SELECT *
        FROM tours
        WHERE trang_thai = 'Đang hoạt động'
        ORDER BY ten_tour
        """
    )

    customers = get_data(
        """
        SELECT *
        FROM customers
        ORDER BY ho_ten
        """
    )

    if tours.empty:

        st.warning("⚠️ Chưa có tour.")

    elif customers.empty:

        st.warning(
            "⚠️ Chưa có khách hàng. Hãy thêm khách hàng trước."
        )

    else:

        # ----------------------------------------------------
        # CHỌN TOUR
        # ----------------------------------------------------

        tour_code = st.selectbox(
            "🚌 Chọn tour",
            tours["ma_tour"].tolist(),
            format_func=lambda x: get_tour_label(
                tours,
                x
            )
        )

        selected_tour = tours[
            tours["ma_tour"] == tour_code
        ].iloc[0]

        st.info(
            f"💰 Giá tour: "
            f"{format_money(selected_tour['gia_tour'])}"
        )

        # ----------------------------------------------------
        # KHÁCH HÀNG
        # ----------------------------------------------------

        customer_code = st.selectbox(
            "👤 Chọn khách hàng",
            customers["ma_khach"].tolist(),
            format_func=lambda x: get_customer_label(
                customers,
                x
            )
        )

        # ----------------------------------------------------
        # SỐ NGƯỜI
        # ----------------------------------------------------

        so_nguoi = st.number_input(
            "👥 Số người",
            min_value=1,
            value=1
        )

        tong_tien = (
            float(selected_tour["gia_tour"])
            * int(so_nguoi)
        )

        st.metric(
            "💰 TỔNG TIỀN",
            format_money(tong_tien)
        )

        ngay_dat = st.date_input(
            "📅 Ngày đặt",
            value=date.today()
        )

        trang_thai = st.selectbox(
            "Trạng thái",
            [
                "Chờ xác nhận",
                "Đã xác nhận",
                "Đã hoàn thành",
                "Đã hủy"
            ]
        )

        ghi_chu = st.text_area("Ghi chú")

        if st.button(
            "💾 TẠO ĐƠN ĐẶT TOUR",
            use_container_width=True
        ):

            try:

                # Lấy số thứ tự tiếp theo.
                row = get_data(
                    """
                    SELECT COUNT(*) AS total
                    FROM bookings
                    """
                )

                count = int(row.iloc[0]["total"]) + 1
                ma_dat = f"DT{count:04d}"

                execute_query(
                    """
                    INSERT INTO bookings (
                        ma_dat_tour,
                        ma_tour,
                        ma_khach,
                        so_nguoi,
                        tong_tien,
                        ngay_dat,
                        trang_thai,
                        ghi_chu
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        ma_dat,
                        tour_code,
                        customer_code,
                        int(so_nguoi),
                        tong_tien,
                        ngay_dat,
                        trang_thai,
                        ghi_chu
                    )
                )

                st.success(
                    f"✅ Đã tạo đơn {ma_dat} thành công!"
                )
                st.rerun()

            except Error as e:

                st.error(
                    f"❌ Không thể tạo đơn: {e}"
                )

        st.markdown("---")

        # ----------------------------------------------------
        # DANH SÁCH ĐẶT TOUR
        # ----------------------------------------------------

        st.subheader("📋 DANH SÁCH ĐẶT TOUR")

        bookings = get_data(
            """
            SELECT
                b.ma_dat_tour,
                b.ma_tour,
                t.ten_tour,
                b.ma_khach,
                c.ho_ten,
                b.so_nguoi,
                b.tong_tien,
                b.ngay_dat,
                b.trang_thai,
                b.ghi_chu
            FROM bookings b
            LEFT JOIN tours t
                ON b.ma_tour = t.ma_tour
            LEFT JOIN customers c
                ON b.ma_khach = c.ma_khach
            ORDER BY b.id DESC
            """
        )

        if not bookings.empty:

            display = bookings.copy()

            display["tong_tien"] = display[
                "tong_tien"
            ].apply(format_money)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("Chưa có đơn đặt tour.")


# ============================================================
# THỐNG KÊ
# ============================================================

elif menu == "📊 Thống kê":

    st.title("📊 THỐNG KÊ KINH DOANH")

    tours = get_data("SELECT * FROM tours")
    customers = get_data("SELECT * FROM customers")
    bookings = get_data("SELECT * FROM bookings")

    revenue = 0

    if not bookings.empty:

        revenue = bookings[
            bookings["trang_thai"].isin(
                ["Đã xác nhận", "Đã hoàn thành"]
            )
        ]["tong_tien"].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🚌 Tổng tour", len(tours))
    c2.metric("👥 Khách hàng", len(customers))
    c3.metric("📋 Đơn đặt tour", len(bookings))
    c4.metric("💰 Doanh thu", format_money(revenue))

    st.markdown("---")

    st.subheader("🚌 Thống kê số lượng tour")

    if not tours.empty:

        status = tours["trang_thai"].value_counts()

        for name, value in status.items():

            st.write(f"**{name}:** {value} tour")

            st.progress(
                float(value / len(tours))
            )

    st.subheader("💰 Doanh thu theo tour")

    if not bookings.empty:

        revenue_by_tour = (
            bookings[
                bookings["trang_thai"].isin(
                    ["Đã xác nhận", "Đã hoàn thành"]
                )
            ]
            .groupby("ma_tour")["tong_tien"]
            .sum()
            .sort_values(ascending=False)
        )

        if not revenue_by_tour.empty:

            max_value = revenue_by_tour.max()

            for tour_code, money in revenue_by_tour.items():

                st.write(
                    f"**{tour_code}** - "
                    f"{format_money(money)}"
                )

                if max_value > 0:
                    st.progress(
                        float(money / max_value)
                    )

        else:

            st.info("Chưa có doanh thu.")

    else:

        st.info("Chưa có đơn đặt tour.")


# ============================================================
# THÔNG TIN
# ============================================================

elif menu == "ℹ️ Thông tin":

    st.title("ℹ️ THÔNG TIN HỆ THỐNG")

    st.markdown("""
    ## 🚌 Hệ thống quản lý tour du lịch

    ### Công nghệ sử dụng

    - Python
    - Streamlit
    - MySQL
    - Aiven
    - Pandas

    ### Chức năng

    ✅ Quản lý tour

    ✅ Thêm / sửa / xóa tour

    ✅ Tìm kiếm tour

    ✅ Quản lý khách hàng

    ✅ Tạo đơn đặt tour

    ✅ Tự động tính tổng tiền

    ✅ Theo dõi trạng thái đơn đặt tour

    ✅ Thống kê doanh thu

    ### Các tour được cài đặt sẵn

    **1. Đà Lạt 3N3Đ (Xe giường nằm)**  
    Giá: 2.090.000đ  
    Khởi hành: Tối 01/10 (Thứ 5)

    **2. Phan Thiết 2N1Đ (Xe ghế)**  
    Giá từ: 1.650.000đ  
    Khởi hành: Sáng 03/10 (Thứ 7)

    **3. Miền Tây 2N1Đ (Xe ghế)**  
    Giá từ: 1.590.000đ  
    Khởi hành: Hàng ngày

    **4. Miền Tây 1N (Xe ghế)**  
    Giá từ: 500.000đ  
    Khởi hành: Hàng ngày

    **5. Tây Ninh - Buffet Trưa - Đỉnh Vân Sơn 1N**  
    Thứ 2 đến thứ 5: 890.000đ  
    Thứ 6, thứ 7, chủ nhật: 1.090.000đ
    """)

    st.markdown("---")

    st.subheader("🗄️ Thông tin Database")

    st.write("Database: `defaultdb`")
    st.write("Host: `mysql-25a34fbe-ngctruc5-4830.e.aivencloud.com`")
    st.write("Port: `26716`")
    st.write("User: `avnadmin`")
    st.write("SSL: `REQUIRED`")

    if st.button("🔄 Kiểm tra lại kết nối MySQL"):
        ok, message = test_connection()

        if ok:
            st.success(message)
        else:
            st.error(message)


# ============================================================
# KẾT THÚC
# ============================================================
