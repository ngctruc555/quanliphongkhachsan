import streamlit as st
import sqlite3
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
# DATABASE
# ============================================================

DB_NAME = "quan_ly_tour.db"


def get_connection():
    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


conn = get_connection()


# ============================================================
# TẠO DATABASE
# ============================================================

def init_database():

    cursor = conn.cursor()

    # --------------------------------------------------------
    # BẢNG TOUR
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BẢNG KHÁCH HÀNG
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BẢNG ĐẶT TOUR
    # --------------------------------------------------------

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

    # ========================================================
    # DỮ LIỆU TOUR CÓ SẴN
    # ========================================================

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

    # --------------------------------------------------------
    # THÊM TOUR NẾU CHƯA CÓ
    # --------------------------------------------------------

    for tour in tours_data:

        cursor.execute(
            """
            SELECT id
            FROM tours
            WHERE ma_tour = ?
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

    conn.commit()


init_database()


# ============================================================
# HÀM HỖ TRỢ
# ============================================================

def get_data(query, params=()):
    return pd.read_sql_query(
        query,
        conn,
        params=params
    )


def execute_query(query, params=()):

    cursor = conn.cursor()

    cursor.execute(
        query,
        params
    )

    conn.commit()

    return cursor


def format_money(value):

    if value is None:
        return "0đ"

    return f"{value:,.0f}đ"


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

st.sidebar.caption(
    "Hệ thống quản lý tour du lịch"
)

st.sidebar.caption(
    "Python + Streamlit + SQLite"
)


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

    tours = get_data(
        "SELECT * FROM tours"
    )

    customers = get_data(
        "SELECT * FROM customers"
    )

    bookings = get_data(
        "SELECT * FROM bookings"
    )

    total_tours = len(tours)

    active_tours = len(
        tours[
            tours["trang_thai"] == "Đang hoạt động"
        ]
    )

    total_customers = len(customers)

    total_bookings = len(bookings)

    revenue = 0

    if not bookings.empty:

        revenue = bookings[
            bookings["trang_thai"].isin(
                [
                    "Đã xác nhận",
                    "Đã hoàn thành"
                ]
            )
        ]["tong_tien"].sum()

    # --------------------------------------------------------
    # THỐNG KÊ NHANH
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🗺️ Tổng tour",
        total_tours
    )

    c2.metric(
        "✅ Tour hoạt động",
        active_tours
    )

    c3.metric(
        "👥 Khách hàng",
        total_customers
    )

    c4.metric(
        "💰 Doanh thu",
        format_money(revenue)
    )

    st.markdown("---")

    # --------------------------------------------------------
    # DANH SÁCH TOUR
    # --------------------------------------------------------

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
                    🚌 {tour['ten_tour']}
                    </div>

                    <br>

                    📍 <b>Điểm đến:</b>
                    {tour['diem_den']}

                    <br><br>

                    ⏱️ <b>Thời gian:</b>
                    {tour['thoi_gian']}

                    <br><br>

                    🗓️ <b>Khởi hành:</b>
                    {tour['ngay_khoi_hanh']}

                    <br><br>

                    <div class="tour-price">
                    💰 {format_money(tour['gia_tour'])}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander(
                    "Xem thông tin tour"
                ):

                    st.write(
                        tour["mo_ta"]
                    )


# ============================================================
# QUẢN LÝ TOUR
# ============================================================

elif menu == "🗺️ Quản lý Tour":

    st.title("🗺️ QUẢN LÝ TOUR")

    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Danh sách",
            "➕ Thêm tour",
            "✏️ Sửa / Xóa"
        ]
    )

    # ========================================================
    # DANH SÁCH TOUR
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
                tours["ma_tour"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                tours["ten_tour"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                tours["diem_den"].str.contains(
                    search,
                    case=False,
                    na=False
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

            display["gia_tour"] = display[
                "gia_tour"
            ].apply(format_money)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Không tìm thấy tour."
            )

    # ========================================================
    # THÊM TOUR
    # ========================================================

    with tab2:

        st.subheader("➕ Thêm tour mới")

        with st.form("add_tour"):

            col1, col2 = st.columns(2)

            with col1:

                ma_tour = st.text_input(
                    "Mã tour *"
                )

                ten_tour = st.text_input(
                    "Tên tour *"
                )

                diem_den = st.text_input(
                    "Điểm đến *"
                )

                thoi_gian = st.text_input(
                    "Thời gian"
                )

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

                mo_ta = st.text_area(
                    "Thông tin tour"
                )

            submit = st.form_submit_button(
                "💾 LƯU TOUR",
                use_container_width=True
            )

            if submit:

                if (
                    not ma_tour
                    or not ten_tour
                    or not diem_den
                ):

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
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    # ========================================================
    # SỬA / XÓA
    # ========================================================

    with tab3:

        tours = get_data(
            "SELECT * FROM tours ORDER BY id"
        )

        if tours.empty:

            st.info(
                "Chưa có tour."
            )

        else:

            selected_id = st.selectbox(
                "Chọn tour",
                tours["id"].tolist(),
                format_func=lambda x:
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

            tour = tours[
                tours["id"] == selected_id
            ].iloc[0]

            with st.form("edit_tour"):

                ma = st.text_input(
                    "Mã tour",
                    value=tour["ma_tour"]
                )

                ten = st.text_input(
                    "Tên tour",
                    value=tour["ten_tour"]
                )

                diem = st.text_input(
                    "Điểm đến",
                    value=tour["diem_den"]
                )

                thoi_gian_edit = st.text_input(
                    "Thời gian",
                    value=tour["thoi_gian"] or ""
                )

                gia = st.number_input(
                    "Giá tour",
                    min_value=0,
                    value=float(
                        tour["gia_tour"] or 0
                    ),
                    step=100000.0
                )

                so_cho_edit = st.number_input(
                    "Số chỗ",
                    min_value=1,
                    value=int(
                        tour["so_cho"] or 1
                    )
                )

                khoi_hanh = st.text_input(
                    "Ngày khởi hành",
                    value=tour["ngay_khoi_hanh"] or ""
                )

                ket_thuc = st.text_input(
                    "Ngày kết thúc",
                    value=tour["ngay_ket_thuc"] or ""
                )

                hdv = st.text_input(
                    "Hướng dẫn viên",
                    value=tour["huong_dan_vien"] or ""
                )

                status = st.selectbox(
                    "Trạng thái",
                    [
                        "Đang hoạt động",
                        "Tạm dừng",
                        "Đã kết thúc"
                    ],
                    index=[
                        "Đang hoạt động",
                        "Tạm dừng",
                        "Đã kết thúc"
                    ].index(
                        tour["trang_thai"]
                    )
                    if tour["trang_thai"]
                    in [
                        "Đang hoạt động",
                        "Tạm dừng",
                        "Đã kết thúc"
                    ]
                    else 0
                )

                mota = st.text_area(
                    "Thông tin tour",
                    value=tour["mo_ta"] or ""
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

                    execute_query(
                        """
                        UPDATE tours
                        SET
                            ma_tour = ?,
                            ten_tour = ?,
                            diem_den = ?,
                            thoi_gian = ?,
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

                    st.success(
                        "✅ Cập nhật tour thành công!"
                    )

                if delete:

                    execute_query(
                        """
                        DELETE FROM tours
                        WHERE id = ?
                        """,
                        (selected_id,)
                    )

                    st.success(
                        "🗑️ Đã xóa tour."
                    )


# ============================================================
# KHÁCH HÀNG
# ============================================================

elif menu == "👥 Khách hàng":

    st.title("👥 QUẢN LÝ KHÁCH HÀNG")

    tab1, tab2 = st.tabs(
        [
            "📋 Danh sách",
            "➕ Thêm khách hàng"
        ]
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

            st.info(
                "Chưa có khách hàng."
            )

    # --------------------------------------------------------
    # THÊM
    # --------------------------------------------------------

    with tab2:

        with st.form("customer_form"):

            ma_khach = st.text_input(
                "Mã khách hàng *"
            )

            ho_ten = st.text_input(
                "Họ và tên *"
            )

            so_dien_thoai = st.text_input(
                "Số điện thoại"
            )

            email = st.text_input(
                "Email"
            )

            dia_chi = st.text_area(
                "Địa chỉ"
            )

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

        st.warning(
            "⚠️ Chưa có tour."
        )

    elif customers.empty:

        st.warning(
            "⚠️ Chưa có khách hàng. "
            "Hãy thêm khách hàng trước."
        )

    else:

        # ----------------------------------------------------
        # CHỌN TOUR
        # ----------------------------------------------------

        tour_code = st.selectbox(
            "🚌 Chọn tour",
            tours["ma_tour"].tolist(),
            format_func=lambda x:
            x
            + " - "
            + tours.loc[
                tours["ma_tour"] == x,
                "ten_tour"
            ].iloc[0]
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
            format_func=lambda x:
            x
            + " - "
            + customers.loc[
                customers["ma_khach"] == x,
                "ho_ten"
            ].iloc[0]
        )

        # ----------------------------------------------------
        # SỐ NGƯỜI
        # ----------------------------------------------------

        so_nguoi = st.number_input(
            "👥 Số người",
            min_value=1,
            value=1
        )

        # ----------------------------------------------------
        # TỔNG TIỀN
        # ----------------------------------------------------

        tong_tien = (
            selected_tour["gia_tour"]
            * so_nguoi
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

        ghi_chu = st.text_area(
            "Ghi chú"
        )

        if st.button(
            "💾 TẠO ĐƠN ĐẶT TOUR",
            use_container_width=True
        ):

            cursor = conn.cursor()

            # Tạo mã tự động
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM bookings
                """
            )

            count = cursor.fetchone()[0] + 1

            ma_dat = (
                f"DT{count:04d}"
            )

            try:

                cursor.execute(
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
                        tour_code,
                        customer_code,
                        so_nguoi,
                        tong_tien,
                        str(ngay_dat),
                        trang_thai,
                        ghi_chu
                    )
                )

                conn.commit()

                st.success(
                    f"✅ Đã tạo đơn {ma_dat} thành công!"
                )

            except Exception as e:

                st.error(
                    f"Không thể tạo đơn: {e}"
                )

        st.markdown("---")

        # ----------------------------------------------------
        # DANH SÁCH ĐẶT TOUR
        # ----------------------------------------------------

        st.subheader(
            "📋 DANH SÁCH ĐẶT TOUR"
        )

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

            st.info(
                "Chưa có đơn đặt tour."
            )


# ============================================================
# THỐNG KÊ
# ============================================================

elif menu == "📊 Thống kê":

    st.title("📊 THỐNG KÊ KINH DOANH")

    tours = get_data(
        "SELECT * FROM tours"
    )

    customers = get_data(
        "SELECT * FROM customers"
    )

    bookings = get_data(
        "SELECT * FROM bookings"
    )

    # --------------------------------------------------------
    # CHỈ SỐ
    # --------------------------------------------------------

    revenue = 0

    if not bookings.empty:

        revenue = bookings[
            bookings["trang_thai"].isin(
                [
                    "Đã xác nhận",
                    "Đã hoàn thành"
                ]
            )
        ]["tong_tien"].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🚌 Tổng tour",
        len(tours)
    )

    c2.metric(
        "👥 Khách hàng",
        len(customers)
    )

    c3.metric(
        "📋 Đơn đặt tour",
        len(bookings)
    )

    c4.metric(
        "💰 Doanh thu",
        format_money(revenue)
    )

    st.markdown("---")

    # --------------------------------------------------------
    # THỐNG KÊ TOUR
    # --------------------------------------------------------

    st.subheader(
        "🚌 Thống kê số lượng tour"
    )

    if not tours.empty:

        status = (
            tours["trang_thai"]
            .value_counts()
        )

        for name, value in status.items():

            st.write(
                f"**{name}:** {value} tour"
            )

            st.progress(
                value / len(tours)
            )

    # --------------------------------------------------------
    # DOANH THU
    # --------------------------------------------------------

    st.subheader(
        "💰 Doanh thu theo tour"
    )

    if not bookings.empty:

        revenue_by_tour = (
            bookings[
                bookings["trang_thai"].isin(
                    [
                        "Đã xác nhận",
                        "Đã hoàn thành"
                    ]
                )
            ]
            .groupby("ma_tour")[
                "tong_tien"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
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

            st.info(
                "Chưa có doanh thu."
            )

    else:

        st.info(
            "Chưa có đơn đặt tour."
        )


# ============================================================
# THÔNG TIN
# ============================================================

elif menu == "ℹ️ Thông tin":

    st.title(
        "ℹ️ THÔNG TIN HỆ THỐNG"
    )

    st.markdown("""
    ## 🚌 Hệ thống quản lý tour du lịch

    ### Công nghệ sử dụng

    - Python
    - Streamlit
    - SQLite
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

    ---

    ### Database

    Dữ liệu được lưu tự động trong:

    `quan_ly_tour.db`
    """)


# ============================================================
# KẾT THÚC
# ============================================================

