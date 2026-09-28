import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date, datetime

# ============================================================
# CẤU HÌNH APP
# ============================================================

st.set_page_config(
    page_title="Quản lý Tour Du lịch",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "quan_ly_tour.db"


# ============================================================
# KẾT NỐI DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


conn = get_connection()


# ============================================================
# TẠO CÁC BẢNG
# ============================================================

def init_database():
    cursor = conn.cursor()

    # Bảng tour
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_tour TEXT UNIQUE NOT NULL,
            ten_tour TEXT NOT NULL,
            diem_den TEXT NOT NULL,
            thoi_gian TEXT,
            so_ngay INTEGER,
            ngay_khoi_hanh TEXT,
            ngay_ket_thuc TEXT,
            so_cho INTEGER DEFAULT 0,
            gia_tour REAL DEFAULT 0,
            huong_dan_vien TEXT,
            trang_thai TEXT DEFAULT 'Đang hoạt động',
            mo_ta TEXT,
            ngay_tao TEXT
        )
    """)

    # Bảng khách hàng
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_khach TEXT UNIQUE NOT NULL,
            ho_ten TEXT NOT NULL,
            so_dien_thoai TEXT,
            email TEXT,
            dia_chi TEXT,
            ngay_tao TEXT
        )
    """)

    # Bảng đặt tour
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_dat_tour TEXT UNIQUE NOT NULL,
            ma_tour TEXT NOT NULL,
            ma_khach TEXT NOT NULL,
            so_nguoi INTEGER DEFAULT 1,
            tong_tien REAL DEFAULT 0,
            ngay_dat TEXT,
            trang_thai TEXT DEFAULT 'Chờ xác nhận',
            ghi_chu TEXT
        )
    """)

    conn.commit()


init_database()


# ============================================================
# HÀM TIỆN ÍCH
# ============================================================

def format_money(value):
    try:
        return f"{value:,.0f} VNĐ"
    except:
        return "0 VNĐ"


def get_data(query, params=()):
    return pd.read_sql_query(query, conn, params=params)


def execute_query(query, params=()):
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    return cursor


# ============================================================
# CSS GIAO DIỆN
# ============================================================

st.markdown("""
<style>

    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #666;
        font-size: 16px;
        margin-bottom: 25px;
    }

    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e5e5e5;
        padding: 15px;
        border-radius: 10px;
    }

    .stButton button {
        border-radius: 7px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("✈️ QUẢN LÝ TOUR")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU",
    [
        "🏠 Tổng quan",
        "🗺️ Quản lý Tour",
        "👥 Quản lý Khách hàng",
        "📋 Đặt Tour",
        "📊 Thống kê",
        "ℹ️ Thông tin"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption("Hệ thống quản lý tour du lịch")
st.sidebar.caption("Phát triển bằng Streamlit + SQLite")


# ============================================================
# TRANG TỔNG QUAN
# ============================================================

if menu == "🏠 Tổng quan":

    st.markdown(
        '<div class="main-title">🏠 TỔNG QUAN HỆ THỐNG</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Quản lý hoạt động kinh doanh tour du lịch</div>',
        unsafe_allow_html=True
    )

    tours = get_data("SELECT * FROM tours")
    customers = get_data("SELECT * FROM customers")
    bookings = get_data("SELECT * FROM bookings")

    tong_tour = len(tours)
    tour_hoat_dong = 0

    if not tours.empty:
        tour_hoat_dong = len(
            tours[tours["trang_thai"] == "Đang hoạt động"]
        )

    tong_khach = len(customers)
    tong_dat_tour = len(bookings)

    tong_doanh_thu = 0

    if not bookings.empty:
        confirmed = bookings[
            bookings["trang_thai"].isin(
                ["Đã xác nhận", "Đã hoàn thành"]
            )
        ]
        tong_doanh_thu = confirmed["tong_tien"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🗺️ Tổng số tour",
            tong_tour
        )

    with col2:
        st.metric(
            "✅ Tour đang hoạt động",
            tour_hoat_dong
        )

    with col3:
        st.metric(
            "👥 Khách hàng",
            tong_khach
        )

    with col4:
        st.metric(
            "💰 Doanh thu",
            format_money(tong_doanh_thu)
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📌 Trạng thái tour")

        if not tours.empty:

            status_count = (
                tours["trang_thai"]
                .value_counts()
                .reset_index()
            )

            status_count.columns = [
                "Trạng thái",
                "Số lượng"
            ]

            fig = px.pie(
                status_count,
                names="Trạng thái",
                values="Số lượng",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("Chưa có dữ liệu tour.")

    with col2:

        st.subheader("📋 Đơn đặt tour")

        if not bookings.empty:

            booking_count = (
                bookings["trang_thai"]
                .value_counts()
                .reset_index()
            )

            booking_count.columns = [
                "Trạng thái",
                "Số lượng"
            ]

            fig = px.bar(
                booking_count,
                x="Trạng thái",
                y="Số lượng",
                text="Số lượng"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("Chưa có đơn đặt tour.")

    st.markdown("---")

    st.subheader("🗓️ Các tour sắp khởi hành")

    if not tours.empty:

        upcoming = tours[
            tours["trang_thai"] == "Đang hoạt động"
        ].copy()

        upcoming["ngay_khoi_hanh_date"] = pd.to_datetime(
            upcoming["ngay_khoi_hanh"],
            errors="coerce"
        )

        upcoming = upcoming.sort_values(
            "ngay_khoi_hanh_date"
        ).head(10)

        if not upcoming.empty:

            display = upcoming[
                [
                    "ma_tour",
                    "ten_tour",
                    "diem_den",
                    "ngay_khoi_hanh",
                    "so_cho",
                    "gia_tour",
                    "huong_dan_vien"
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
            st.info("Không có tour sắp khởi hành.")


# ============================================================
# QUẢN LÝ TOUR
# ============================================================

elif menu == "🗺️ Quản lý Tour":

    st.title("🗺️ QUẢN LÝ TOUR")

    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Danh sách Tour",
            "➕ Thêm Tour",
            "✏️ Chỉnh sửa / Xóa"
        ]
    )

    # --------------------------------------------------------
    # DANH SÁCH
    # --------------------------------------------------------

    with tab1:

        tours = get_data(
            "SELECT * FROM tours ORDER BY id DESC"
        )

        if not tours.empty:

            search = st.text_input(
                "🔎 Tìm kiếm tour",
                placeholder="Nhập mã tour, tên tour hoặc điểm đến..."
            )

            if search:

                tours = tours[
                    tours["ma_tour"].astype(str).str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    tours["ten_tour"].astype(str).str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    tours["diem_den"].astype(str).str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]

            display = tours[
                [
                    "ma_tour",
                    "ten_tour",
                    "diem_den",
                    "thoi_gian",
                    "so_ngay",
                    "ngay_khoi_hanh",
                    "so_cho",
                    "gia_tour",
                    "huong_dan_vien",
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

            st.caption(
                f"Hiển thị {len(display)} tour."
            )

        else:
            st.info(
                "Chưa có tour. Hãy chuyển sang tab 'Thêm Tour'."
            )

    # --------------------------------------------------------
    # THÊM TOUR
    # --------------------------------------------------------

    with tab2:

        st.subheader("➕ Thêm tour mới")

        with st.form("add_tour_form"):

            col1, col2 = st.columns(2)

            with col1:

                ma_tour = st.text_input(
                    "Mã tour *",
                    placeholder="VD: TOUR001"
                )

                ten_tour = st.text_input(
                    "Tên tour *",
                    placeholder="VD: TP.HCM - Đà Lạt 3N2Đ"
                )

                diem_den = st.text_input(
                    "Điểm đến *",
                    placeholder="VD: Đà Lạt"
                )

                thoi_gian = st.text_input(
                    "Thời gian",
                    placeholder="VD: 3 ngày 2 đêm"
                )

                so_ngay = st.number_input(
                    "Số ngày",
                    min_value=1,
                    max_value=100,
                    value=3
                )

                gia_tour = st.number_input(
                    "Giá tour (VNĐ)",
                    min_value=0,
                    step=100000,
                    value=0
                )

            with col2:

                ngay_khoi_hanh = st.date_input(
                    "Ngày khởi hành",
                    value=date.today()
                )

                ngay_ket_thuc = st.date_input(
                    "Ngày kết thúc",
                    value=date.today()
                )

                so_cho = st.number_input(
                    "Số chỗ",
                    min_value=1,
                    value=30
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

                mo_ta = st.text_area(
                    "Mô tả tour"
                )

            submit = st.form_submit_button(
                "💾 Lưu Tour",
                use_container_width=True
            )

            if submit:

                if not ma_tour or not ten_tour or not diem_den:

                    st.error(
                        "Vui lòng nhập đầy đủ các trường có dấu *."
                    )

                elif ngay_ket_thuc < ngay_khoi_hanh:

                    st.error(
                        "Ngày kết thúc không được trước ngày khởi hành."
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
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                ma_tour,
                                ten_tour,
                                diem_den,
                                thoi_gian,
                                so_ngay,
                                str(ngay_khoi_hanh),
                                str(ngay_ket_thuc),
                                so_cho,
                                gia_tour,
                                huong_dan_vien,
                                trang_thai,
                                mo_ta,
                                datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            )
                        )

                        st.success(
                            "✅ Thêm tour thành công!"
                        )

                    except sqlite3.IntegrityError:

                        st.error(
                            "❌ Mã tour đã tồn tại."
                        )

    # --------------------------------------------------------
    # SỬA / XÓA TOUR
    # --------------------------------------------------------

    with tab3:

        tours = get_data(
            "SELECT * FROM tours ORDER BY id DESC"
        )

        if tours.empty:

            st.info("Chưa có dữ liệu tour.")

        else:

            selected_id = st.selectbox(
                "Chọn tour",
                tours["id"].tolist(),
                format_func=lambda x: (
                    tours.loc[
                        tours["id"] == x,
                        "ma_tour"
                    ].iloc[0]
                    + " - "
                    + tours.loc[
                        tours["id"] == x,
                        "ten_tour"
                    ].iloc[0]
                )
            )

            tour = tours[
                tours["id"] == selected_id
            ].iloc[0]

            with st.form("edit_tour_form"):

                col1, col2 = st.columns(2)

                with col1:

                    edit_ma = st.text_input(
                        "Mã tour",
                        value=tour["ma_tour"]
                    )

                    edit_ten = st.text_input(
                        "Tên tour",
                        value=tour["ten_tour"]
                    )

                    edit_diem = st.text_input(
                        "Điểm đến",
                        value=tour["diem_den"]
                    )

                    edit_thoi_gian = st.text_input(
                        "Thời gian",
                        value=tour["thoi_gian"] or ""
                    )

                    edit_so_ngay = st.number_input(
                        "Số ngày",
                        min_value=1,
                        value=int(tour["so_ngay"] or 1)
                    )

                    edit_gia = st.number_input(
                        "Giá tour",
                        min_value=0,
                        value=float(tour["gia_tour"] or 0),
                        step=100000.0
                    )

                with col2:

                    try:
                        start_date = datetime.strptime(
                            tour["ngay_khoi_hanh"],
                            "%Y-%m-%d"
                        ).date()
                    except:
                        start_date = date.today()

                    try:
                        end_date = datetime.strptime(
                            tour["ngay_ket_thuc"],
                            "%Y-%m-%d"
                        ).date()
                    except:
                        end_date = date.today()

                    edit_start = st.date_input(
                        "Ngày khởi hành",
                        value=start_date
                    )

                    edit_end = st.date_input(
                        "Ngày kết thúc",
                        value=end_date
                    )

                    edit_so_cho = st.number_input(
                        "Số chỗ",
                        min_value=1,
                        value=int(tour["so_cho"] or 1)
                    )

                    edit_hdv = st.text_input(
                        "Hướng dẫn viên",
                        value=tour["huong_dan_vien"] or ""
                    )

                    status_options = [
                        "Đang hoạt động",
                        "Tạm dừng",
                        "Đã kết thúc"
                    ]

                    current_status = (
                        tour["trang_thai"]
                        if tour["trang_thai"] in status_options
                        else status_options[0]
                    )

                    edit_status = st.selectbox(
                        "Trạng thái",
                        status_options,
                        index=status_options.index(
                            current_status
                        )
                    )

                    edit_mo_ta = st.text_area(
                        "Mô tả",
                        value=tour["mo_ta"] or ""
                    )

                col_a, col_b = st.columns(2)

                with col_a:

                    update_button = st.form_submit_button(
                        "💾 Cập nhật",
                        use_container_width=True
                    )

                with col_b:

                    delete_button = st.form_submit_button(
                        "🗑️ Xóa tour",
                        use_container_width=True
                    )

                if update_button:

                    execute_query(
                        """
                        UPDATE tours
                        SET
                            ma_tour = ?,
                            ten_tour = ?,
                            diem_den = ?,
                            thoi_gian = ?,
                            so_ngay = ?,
                            ngay_khoi_hanh = ?,
                            ngay_ket_thuc = ?,
                            so_cho = ?,
                            gia_tour = ?,
                            huong_dan_vien = ?,
                            trang_thai = ?,
                            mo_ta = ?
                        WHERE id = ?
                        """,
                        (
                            edit_ma,
                            edit_ten,
                            edit_diem,
                            edit_thoi_gian,
                            edit_so_ngay,
                            str(edit_start),
                            str(edit_end),
                            edit_so_cho,
                            edit_gia,
                            edit_hdv,
                            edit_status,
                            edit_mo_ta,
                            selected_id
                        )
                    )

                    st.success(
                        "✅ Cập nhật tour thành công!"
                    )

                if delete_button:

                    execute_query(
                        "DELETE FROM tours WHERE id = ?",
                        (selected_id,)
                    )

                    st.success(
                        "🗑️ Đã xóa tour."
                    )


# ============================================================
# QUẢN LÝ KHÁCH HÀNG
# ============================================================

elif menu == "👥 Quản lý Khách hàng":

    st.title("👥 QUẢN LÝ KHÁCH HÀNG")

    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Danh sách khách hàng",
            "➕ Thêm khách hàng",
            "✏️ Sửa / Xóa"
        ]
    )

    # --------------------------------------------------------
    # DANH SÁCH KHÁCH HÀNG
    # --------------------------------------------------------

    with tab1:

        customers = get_data(
            "SELECT * FROM customers ORDER BY id DESC"
        )

        if not customers.empty:

            search = st.text_input(
                "🔎 Tìm khách hàng",
                placeholder="Nhập mã khách, họ tên hoặc số điện thoại..."
            )

            if search:

                customers = customers[
                    customers["ma_khach"].astype(str).str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    customers["ho_ten"].astype(str).str.contains(
                        search,
                        case=False,
                        na=False
                    )
                    |
                    customers["so_dien_thoai"].astype(str).str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]

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
    # THÊM KHÁCH HÀNG
    # --------------------------------------------------------

    with tab2:

        st.subheader("➕ Thêm khách hàng")

        with st.form("add_customer"):

            col1, col2 = st.columns(2)

            with col1:

                ma_khach = st.text_input(
                    "Mã khách hàng *",
                    placeholder="VD: KH001"
                )

                ho_ten = st.text_input(
                    "Họ và tên *"
                )

                so_dien_thoai = st.text_input(
                    "Số điện thoại"
                )

            with col2:

                email = st.text_input(
                    "Email"
                )

                dia_chi = st.text_area(
                    "Địa chỉ"
                )

            submit = st.form_submit_button(
                "💾 Lưu khách hàng",
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
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                ma_khach,
                                ho_ten,
                                so_dien_thoai,
                                email,
                                dia_chi,
                                datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            )
                        )

                        st.success(
                            "✅ Thêm khách hàng thành công!"
                        )

                    except sqlite3.IntegrityError:

                        st.error(
                            "❌ Mã khách hàng đã tồn tại."
                        )


    # --------------------------------------------------------
    # SỬA / XÓA KHÁCH HÀNG
    # --------------------------------------------------------

    with tab3:

        customers = get_data(
            "SELECT * FROM customers ORDER BY id DESC"
        )

        if customers.empty:

            st.info("Chưa có khách hàng.")

        else:

            selected_customer = st.selectbox(
                "Chọn khách hàng",
                customers["id"].tolist(),
                format_func=lambda x: (
                    customers.loc[
                        customers["id"] == x,
                        "ma_khach"
                    ].iloc[0]
                    + " - "
                    + customers.loc[
                        customers["id"] == x,
                        "ho_ten"
                    ].iloc[0]
                )
            )

            customer = customers[
                customers["id"] == selected_customer
            ].iloc[0]

            with st.form("edit_customer"):

                edit_ma = st.text_input(
                    "Mã khách hàng",
                    value=customer["ma_khach"]
                )

                edit_name = st.text_input(
                    "Họ và tên",
                    value=customer["ho_ten"]
                )

                edit_phone = st.text_input(
                    "Số điện thoại",
                    value=customer["so_dien_thoai"] or ""
                )

                edit_email = st.text_input(
                    "Email",
                    value=customer["email"] or ""
                )

                edit_address = st.text_area(
                    "Địa chỉ",
                    value=customer["dia_chi"] or ""
                )

                col1, col2 = st.columns(2)

                with col1:

                    update = st.form_submit_button(
                        "💾 Cập nhật",
                        use_container_width=True
                    )

                with col2:

                    delete = st.form_submit_button(
                        "🗑️ Xóa",
                        use_container_width=True
                    )

                if update:

                    execute_query(
                        """
                        UPDATE customers
                        SET
                            ma_khach = ?,
                            ho_ten = ?,
                            so_dien_thoai = ?,
                            email = ?,
                            dia_chi = ?
                        WHERE id = ?
                        """,
                        (
                            edit_ma,
                            edit_name,
                            edit_phone,
                            edit_email,
                            edit_address,
                            selected_customer
                        )
                    )

                    st.success(
                        "✅ Cập nhật thành công!"
                    )

                if delete:

                    execute_query(
                        "DELETE FROM customers WHERE id = ?",
                        (selected_customer,)
                    )

                    st.success(
                        "🗑️ Đã xóa khách hàng."
                    )


# ============================================================
# ĐẶT TOUR
# ============================================================

elif menu == "📋 Đặt Tour":

    st.title("📋 QUẢN LÝ ĐẶT TOUR")

    tab1, tab2 = st.tabs(
        [
            "📋 Danh sách đặt tour",
            "➕ Tạo đơn đặt tour"
        ]
    )

    # --------------------------------------------------------
    # DANH SÁCH ĐẶT TOUR
    # --------------------------------------------------------

    with tab1:

        bookings = get_data(
            """
            SELECT
                b.id,
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
                display[
                    [
                        "ma_dat_tour",
                        "ma_tour",
                        "ten_tour",
                        "ma_khach",
                        "ho_ten",
                        "so_nguoi",
                        "tong_tien",
                        "ngay_dat",
                        "trang_thai"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("Chưa có đơn đặt tour.")


    # --------------------------------------------------------
    # TẠO ĐƠN
    # --------------------------------------------------------

    with tab2:

        tours = get_data(
            "SELECT * FROM tours ORDER BY ten_tour"
        )

        customers = get_data(
            "SELECT * FROM customers ORDER BY ho_ten"
        )

        if tours.empty:

            st.warning(
                "⚠️ Chưa có tour. Vui lòng thêm tour trước."
            )

        elif customers.empty:

            st.warning(
                "⚠️ Chưa có khách hàng. Vui lòng thêm khách hàng trước."
            )

        else:

            st.subheader("➕ Tạo đơn đặt tour")

            with st.form("booking_form"):

                ma_dat = st.text_input(
                    "Mã đặt tour *",
                    placeholder="VD: DT001"
                )

                tour_options = tours["ma_tour"].tolist()

                selected_tour = st.selectbox(
                    "Tour *",
                    tour_options,
                    format_func=lambda x: (
                        x
                        + " - "
                        + tours.loc[
                            tours["ma_tour"] == x,
                            "ten_tour"
                        ].iloc[0]
                    )
                )

                customer_options = customers[
                    "ma_khach"
                ].tolist()

                selected_customer = st.selectbox(
                    "Khách hàng *",
                    customer_options,
                    format_func=lambda x: (
                        x
                        + " - "
                        + customers.loc[
                            customers["ma_khach"] == x,
                            "ho_ten"
                        ].iloc[0]
                    )
                )

                col1, col2 = st.columns(2)

                with col1:

                    so_nguoi = st.number_input(
                        "Số người",
                        min_value=1,
                        value=1
                    )

                selected_price = tours.loc[
                    tours["ma_tour"] == selected_tour,
                    "gia_tour"
                ].iloc[0]

                tong_tien = selected_price * so_nguoi

                with col2:

                    st.metric(
                        "Tổng tiền",
                        format_money(tong_tien)
                    )

                ngay_dat = st.date_input(
                    "Ngày đặt",
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

                ghi_chu = st.text_area(
                    "Ghi chú"
                )

                submit = st.form_submit_button(
                    "💾 Tạo đơn đặt tour",
                    use_container_width=True
                )

                if submit:

                    if not ma_dat:

                        st.error(
                            "Vui lòng nhập mã đặt tour."
                        )

                    else:

                        try:

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
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    ma_dat,
                                    selected_tour,
                                    selected_customer,
                                    so_nguoi,
                                    tong_tien,
                                    str(ngay_dat),
                                    trang_thai,
                                    ghi_chu
                                )
                            )

                            st.success(
                                "✅ Tạo đơn đặt tour thành công!"
                            )

                        except sqlite3.IntegrityError:

                            st.error(
                                "❌ Mã đặt tour đã tồn tại."
                            )


# ============================================================
# THỐNG KÊ
# ============================================================

elif menu == "📊 Thống kê":

    st.title("📊 THỐNG KÊ")

    tours = get_data(
        "SELECT * FROM tours"
    )

    bookings = get_data(
        "SELECT * FROM bookings"
    )

    customers = get_data(
        "SELECT * FROM customers"
    )

    # --------------------------------------------------------
    # TỔNG QUAN
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🗺️ Số tour",
            len(tours)
        )

    with col2:
        st.metric(
            "👥 Khách hàng",
            len(customers)
        )

    with col3:
        st.metric(
            "📋 Đơn đặt tour",
            len(bookings)
        )

    doanh_thu = 0

    if not bookings.empty:

        doanh_thu = bookings[
            bookings["trang_thai"].isin(
                [
                    "Đã xác nhận",
                    "Đã hoàn thành"
                ]
            )
        ]["tong_tien"].sum()

    with col4:

        st.metric(
            "💰 Doanh thu",
            format_money(doanh_thu)
        )

    st.markdown("---")

    # --------------------------------------------------------
    # DOANH THU THEO TOUR
    # --------------------------------------------------------

    if not bookings.empty:

        revenue = bookings[
            bookings["trang_thai"].isin(
                [
                    "Đã xác nhận",
                    "Đã hoàn thành"
                ]
            )
        ]

        revenue = (
            revenue.groupby("ma_tour")[
                "tong_tien"
            ]
            .sum()
            .reset_index()
            .sort_values(
                "tong_tien",
                ascending=False
            )
        )

        st.subheader("💰 Doanh thu theo tour")

        if not revenue.empty:

            fig = px.bar(
                revenue,
                x="ma_tour",
                y="tong_tien",
                text_auto=".2s",
                labels={
                    "ma_tour": "Mã tour",
                    "tong_tien": "Doanh thu"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # SỐ LƯỢNG KHÁCH THEO TOUR
        # ----------------------------------------------------

        customers_by_tour = (
            bookings.groupby("ma_tour")[
                "so_nguoi"
            ]
            .sum()
            .reset_index()
            .sort_values(
                "so_nguoi",
                ascending=False
            )
        )

        st.subheader("👥 Số lượng khách theo tour")

        fig = px.bar(
            customers_by_tour,
            x="ma_tour",
            y="so_nguoi",
            text_auto=True,
            labels={
                "ma_tour": "Mã tour",
                "so_nguoi": "Số khách"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Chưa có dữ liệu đặt tour để thống kê."
        )


# ============================================================
# THÔNG TIN
# ============================================================

elif menu == "ℹ️ Thông tin":

    st.title("ℹ️ THÔNG TIN HỆ THỐNG")

    st.markdown("""
    ## ✈️ Hệ thống quản lý tour du lịch

    Ứng dụng được xây dựng bằng:

    - **Python**
    - **Streamlit**
    - **SQLite**
    - **Pandas**
    - **Plotly**

    ### Chức năng chính

    **1. Quản lý Tour**
    - Thêm tour
    - Sửa tour
    - Xóa tour
    - Tìm kiếm tour
    - Theo dõi trạng thái tour

    **2. Quản lý khách hàng**
    - Thêm khách hàng
    - Chỉnh sửa thông tin
    - Xóa khách hàng
    - Tìm kiếm khách hàng

    **3. Quản lý đặt tour**
    - Tạo đơn đặt tour
    - Tính tổng tiền tự động
    - Theo dõi trạng thái đặt tour

    **4. Thống kê**
    - Tổng số tour
    - Tổng số khách hàng
    - Tổng số đơn đặt tour
    - Doanh thu
    - Doanh thu theo tour
    - Số lượng khách theo tour

    ### Cơ sở dữ liệu

    Dữ liệu được lưu trong file:

    `quan_ly_tour.db`

    File database sẽ tự động được tạo trong thư mục
    chứa file `app.py`.
    """)


# ============================================================
# ĐÓNG DATABASE
# ============================================================

# Không cần đóng conn ở đây vì Streamlit rerun liên tục.
