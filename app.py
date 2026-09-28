import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="Quản lý Tour Du lịch",
    page_icon="🚌",
    layout="wide"
)

# ============================================================
# MYSQL AIVEN
# ============================================================
DB_CONFIG = {
    "host": "mysql-25a34fbe-ngctruc5-4830.e.aivencloud.com",
    "port": 26716,
    "database": "defaultdb",
    "user": "avnadmin",
    "password": "AVNS_1JPNssDgmO_BqXf9Rmf",
    "ssl_disabled": False,
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def db_read(sql, params=()):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return pd.DataFrame(cur.fetchall())
    finally:
        cur.close()
        conn.close()

def db_write(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

def money(value):
    if value is None:
        return "0đ"
    try:
        if pd.isna(value):
            return "0đ"
    except Exception:
        pass
    return f"{float(value):,.0f}đ"

def init_database():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
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

        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ma_khach VARCHAR(50) NOT NULL UNIQUE,
                ho_ten VARCHAR(255) NOT NULL,
                so_dien_thoai VARCHAR(30),
                email VARCHAR(255),
                dia_chi VARCHAR(500),
                ngay_tao DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cur.execute("""
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

        # Bảng lưu các lần tính giá tour
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tour_costs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ma_tinh_gia VARCHAR(50) NOT NULL UNIQUE,
                ma_tour VARCHAR(50) NOT NULL,
                so_khach INT NOT NULL,
                chi_phi_xe DECIMAL(15,2) DEFAULT 0,
                chi_phi_khach_san DECIMAL(15,2) DEFAULT 0,
                chi_phi_an_uong DECIMAL(15,2) DEFAULT 0,
                chi_phi_ve DECIMAL(15,2) DEFAULT 0,
                chi_phi_hdv DECIMAL(15,2) DEFAULT 0,
                chi_phi_khac DECIMAL(15,2) DEFAULT 0,
                tong_chi_phi DECIMAL(15,2) DEFAULT 0,
                gia_von_khach DECIMAL(15,2) DEFAULT 0,
                ty_le_loi_nhuan DECIMAL(8,2) DEFAULT 0,
                tien_loi_nhuan DECIMAL(15,2) DEFAULT 0,
                vat DECIMAL(15,2) DEFAULT 0,
                gia_ban_khach DECIMAL(15,2) DEFAULT 0,
                ghi_chu TEXT,
                ngay_tinh DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Tự sửa database cũ nếu trước đây dùng TEXT cho trang_thai
        for table, default in [
            ("tours", "Đang hoạt động"),
            ("bookings", "Chờ xác nhận")
        ]:
            cur.execute(f"SHOW COLUMNS FROM {table} LIKE 'trang_thai'")
            col = cur.fetchone()
            if col and ("text" in str(col[1]).lower() or "blob" in str(col[1]).lower()):
                cur.execute(
                    f"ALTER TABLE {table} MODIFY COLUMN trang_thai VARCHAR(100) DEFAULT %s",
                    (default,)
                )

        conn.commit()
    finally:
        cur.close()
        conn.close()

def seed_tours():
    data = [
        (
            "DL001", "Đà Lạt 3N3Đ (Xe giường nằm)", "Đà Lạt",
            "3 ngày 3 đêm", 3, "01/10/2026", "04/10/2026", 40,
            2090000, "", "Đang hoạt động",
            "🚌 Phương tiện: Xe giường nằm\n\n"
            "🗓 Khởi hành: Tối 01/10 (Thứ 5)\n\n"
            "💰 Giá chỉ: 2.090.000đ"
        ),
        (
            "PT001", "Phan Thiết 2N1Đ (Xe ghế)", "Phan Thiết",
            "2 ngày 1 đêm", 2, "03/10/2026", "04/10/2026", 40,
            1650000, "", "Đang hoạt động",
            "🚌 Phương tiện: Xe ghế\n\n"
            "🗓 Khởi hành: Sáng 03/10 (Thứ 7)\n\n"
            "💰 Giá chỉ từ: 1.650.000đ"
        ),
        (
            "MT001", "Miền Tây 2N1Đ (Xe ghế)", "Miền Tây",
            "2 ngày 1 đêm", 2, "Hàng ngày", "Hàng ngày", 40,
            1590000, "", "Đang hoạt động",
            "🚌 Phương tiện: Xe ghế\n\n"
            "🗓 Khởi hành: Hàng ngày\n\n"
            "💰 Giá chỉ từ: 1.590.000đ"
        ),
        (
            "MT002", "Miền Tây 1N (Xe ghế)", "Miền Tây",
            "1 ngày", 1, "Hàng ngày", "Hàng ngày", 40,
            500000, "", "Đang hoạt động",
            "🚌 Phương tiện: Xe ghế\n\n"
            "🗓 Khởi hành: Hàng ngày\n\n"
            "💰 Giá chỉ từ: 500.000đ"
        ),
        (
            "TN001", "Tây Ninh - Buffet Trưa - Đỉnh Vân Sơn 1N",
            "Tây Ninh", "1 ngày", 1, "Thứ 2 - Chủ nhật",
            "Trong ngày", 40, 890000, "", "Đang hoạt động",
            "🛕 Tây Ninh - Buffet Trưa - Đỉnh Vân Sơn 1N\n\n"
            "📆 Khởi hành:\n\n"
            "• Sáng thứ 2 đến thứ 5:\n"
            "💸 Giá 890.000đ\n"
            "Chưa bao gồm Buffet\n\n"
            "• Sáng thứ 6, thứ 7, chủ nhật:\n"
            "💸 Giá 1.090.000đ"
        )
    ]

    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = """
            INSERT INTO tours (
                ma_tour, ten_tour, diem_den, thoi_gian, so_ngay,
                ngay_khoi_hanh, ngay_ket_thuc, so_cho, gia_tour,
                huong_dan_vien, trang_thai, mo_ta, ngay_tao
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        for row in data:
            cur.execute(
                "SELECT id FROM tours WHERE ma_tour=%s",
                (row[0],)
            )
            if cur.fetchone() is None:
                cur.execute(sql, row + (datetime.now(),))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ============================================================
# KHỞI TẠO
# ============================================================
try:
    init_database()
    seed_tours()
except Error as e:
    st.error("❌ Không thể kết nối hoặc khởi tạo MySQL Aiven.")
    st.code(str(e))
    st.info(
        "Hãy kiểm tra thông tin Aiven và chạy: "
        "pip install streamlit pandas mysql-connector-python"
    )
    st.stop()

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.main-title {
    font-size: 32px;
    font-weight: 700;
}
.sub-title {
    color: #666;
    margin-bottom: 20px;
}
.tour-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
    background: white;
}
.tour-name {
    font-size: 20px;
    font-weight: 700;
}
.tour-price {
    font-size: 22px;
    font-weight: 700;
}
.price-box {
    padding: 18px;
    border: 1px solid #ddd;
    border-radius: 12px;
    background: #fafafa;
}
.big-price {
    font-size: 30px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🚌 QUẢN LÝ TOUR")

menu = st.sidebar.radio(
    "CHỨC NĂNG",
    [
        "🏠 Trang chủ",
        "🧮 Tính giá Tour",
        "🗺️ Quản lý Tour",
        "💰 Chi phí Tour",
        "👥 Khách hàng",
        "📋 Đặt Tour",
        "📜 Lịch sử tính giá",
        "📊 Thống kê",
        "ℹ️ Thông tin"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Python + Streamlit + MySQL Aiven")

# ============================================================
# TRANG CHỦ
# ============================================================
if menu == "🏠 Trang chủ":
    st.markdown(
        '<div class="main-title">🚌 HỆ THỐNG QUẢN LÝ TOUR DU LỊCH</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-title">Quản lý tour - tính giá - khách hàng - đặt tour - doanh thu</div>',
        unsafe_allow_html=True
    )

    tours = db_read("SELECT * FROM tours")
    customers = db_read("SELECT * FROM customers")
    bookings = db_read("SELECT * FROM bookings")

    revenue = 0
    if not bookings.empty:
        revenue = bookings.loc[
            bookings["trang_thai"].isin(["Đã xác nhận", "Đã hoàn thành"]),
            "tong_tien"
        ].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🗺️ Tổng tour", len(tours))
    c2.metric(
        "✅ Tour hoạt động",
        int((tours["trang_thai"] == "Đang hoạt động").sum())
        if not tours.empty else 0
    )
    c3.metric("👥 Khách hàng", len(customers))
    c4.metric("💰 Doanh thu", money(revenue))

    st.markdown("---")
    st.subheader("⭐ TOUR ĐANG CÓ")

    active = (
        tours[tours["trang_thai"] == "Đang hoạt động"]
        if not tours.empty else tours
    )

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
                        <div class="tour-name">🚌 {tour['ten_tour']}</div>
                        <br>
                        📍 <b>Điểm đến:</b> {tour['diem_den']}
                        <br><br>
                        ⏱️ <b>Thời gian:</b> {tour['thoi_gian']}
                        <br><br>
                        🗓️ <b>Khởi hành:</b> {tour['ngay_khoi_hanh']}
                        <br><br>
                        <div class="tour-price">
                            💰 {money(tour['gia_tour'])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with st.expander("Xem thông tin tour"):
                    st.write(tour["mo_ta"])

# ============================================================
# TÍNH GIÁ TOUR
# ============================================================
elif menu == "🧮 Tính giá Tour":
    st.title("🧮 TÍNH GIÁ TOUR")

    tours = db_read(
        "SELECT * FROM tours WHERE trang_thai='Đang hoạt động' ORDER BY ten_tour"
    )

    if tours.empty:
        st.warning("Chưa có tour hoạt động.")
    else:
        st.subheader("1️⃣ Thông tin tour")

        tour_code = st.selectbox(
            "🚌 Chọn tour",
            tours["ma_tour"].tolist(),
            format_func=lambda x:
                f"{x} - {tours.loc[tours['ma_tour'] == x, 'ten_tour'].iloc[0]}"
        )

        selected = tours[tours["ma_tour"] == tour_code].iloc[0]

        st.info(
            f"Tour: **{selected['ten_tour']}** | "
            f"Giá đang bán: **{money(selected['gia_tour'])}/khách**"
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            so_khach = st.number_input(
                "👥 Số khách",
                min_value=1,
                max_value=1000,
                value=30
            )

        with c2:
            ty_le_loi_nhuan = st.number_input(
                "📈 Lợi nhuận (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=1.0
            )

        with c3:
            ty_le_vat = st.number_input(
                "🧾 VAT (%)",
                min_value=0.0,
                max_value=100.0,
                value=8.0,
                step=1.0
            )

        st.subheader("2️⃣ Nhập chi phí")

        st.caption(
            "Các khoản dưới đây là TỔNG CHI PHÍ cho cả đoàn, "
            "không phải chi phí của từng khách."
        )

        c1, c2 = st.columns(2)

        with c1:
            chi_phi_xe = st.number_input(
                "🚌 Chi phí xe / vận chuyển",
                min_value=0.0,
                value=0.0,
                step=100000.0
            )

            chi_phi_khach_san = st.number_input(
                "🏨 Chi phí khách sạn",
                min_value=0.0,
                value=0.0,
                step=100000.0
            )

            chi_phi_an_uong = st.number_input(
                "🍜 Chi phí ăn uống",
                min_value=0.0,
                value=0.0,
                step=100000.0
            )

        with c2:
            chi_phi_ve = st.number_input(
                "🎫 Vé tham quan",
                min_value=0.0,
                value=0.0,
                step=100000.0
            )

            chi_phi_hdv = st.number_input(
                "👨‍💼 Hướng dẫn viên",
                min_value=0.0,
                value=0.0,
                step=100000.0
            )

            chi_phi_khac = st.number_input(
                "📦 Chi phí khác",
                min_value=0.0,
                value=0.0,
                step=100000.0
            )

        ghi_chu = st.text_area(
            "📝 Ghi chú",
            placeholder="Ví dụ: Xe 45 chỗ, khách sạn 3 sao, đã bao gồm bảo hiểm..."
        )

        st.markdown("---")

        # TÍNH TOÁN
        tong_chi_phi = (
            chi_phi_xe
            + chi_phi_khach_san
            + chi_phi_an_uong
            + chi_phi_ve
            + chi_phi_hdv
            + chi_phi_khac
        )

        gia_von_khach = tong_chi_phi / so_khach

        tien_loi_nhuan = gia_von_khach * ty_le_loi_nhuan / 100

        gia_truoc_vat = gia_von_khach + tien_loi_nhuan

        tien_vat = gia_truoc_vat * ty_le_vat / 100

        gia_ban_khach = gia_truoc_vat + tien_vat

        st.subheader("3️⃣ Kết quả tính giá")

        a, b, c, d = st.columns(4)

        a.metric(
            "💰 Tổng chi phí",
            money(tong_chi_phi)
        )

        b.metric(
            "👤 Giá vốn / khách",
            money(gia_von_khach)
        )

        c.metric(
            "📈 Lợi nhuận / khách",
            money(tien_loi_nhuan)
        )

        d.metric(
            "🏷️ Giá bán / khách",
            money(gia_ban_khach)
        )

        st.markdown(
            f"""
            <div class="price-box">
                <h3>💵 GIÁ BÁN ĐỀ XUẤT</h3>
                <div class="big-price">{money(gia_ban_khach)} / khách</div>
                <br>
                <b>Số khách:</b> {so_khach} người<br>
                <b>Tổng giá bán đoàn:</b> {money(gia_ban_khach * so_khach)}<br>
                <b>Tổng chi phí:</b> {money(tong_chi_phi)}<br>
                <b>Tổng lợi nhuận:</b> {money(tien_loi_nhuan * so_khach)}<br>
                <b>Tổng VAT:</b> {money(tien_vat * so_khach)}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        with st.expander("📊 Xem chi tiết công thức"):
            st.write(
                f"**Tổng chi phí** = {money(tong_chi_phi)}"
            )
            st.write(
                f"**Giá vốn/khách** = {money(tong_chi_phi)} ÷ {so_khach} "
                f"= **{money(gia_von_khach)}**"
            )
            st.write(
                f"**Lợi nhuận/khách** = {money(gia_von_khach)} × "
                f"{ty_le_loi_nhuan}% = **{money(tien_loi_nhuan)}**"
            )
            st.write(
                f"**Giá trước VAT** = {money(gia_von_khach)} + "
                f"{money(tien_loi_nhuan)} = **{money(gia_truoc_vat)}**"
            )
            st.write(
                f"**VAT/khách** = {money(gia_truoc_vat)} × "
                f"{ty_le_vat}% = **{money(tien_vat)}**"
            )
            st.write(
                f"**Giá bán/khách** = {money(gia_truoc_vat)} + "
                f"{money(tien_vat)} = **{money(gia_ban_khach)}**"
            )

        if st.button(
            "💾 LƯU KẾT QUẢ TÍNH GIÁ",
            type="primary",
            use_container_width=True
        ):
            try:
                last = db_read(
                    "SELECT id FROM tour_costs ORDER BY id DESC LIMIT 1"
                )

                next_id = (
                    int(last.iloc[0]["id"]) + 1
                    if not last.empty else 1
                )

                ma_tinh_gia = f"TG{next_id:04d}"

                db_write(
                    """
                    INSERT INTO tour_costs (
                        ma_tinh_gia, ma_tour, so_khach,
                        chi_phi_xe, chi_phi_khach_san,
                        chi_phi_an_uong, chi_phi_ve,
                        chi_phi_hdv, chi_phi_khac,
                        tong_chi_phi, gia_von_khach,
                        ty_le_loi_nhuan, tien_loi_nhuan,
                        vat, gia_ban_khach,
                        ghi_chu, ngay_tinh
                    )
                    VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s
                    )
                    """,
                    (
                        ma_tinh_gia,
                        tour_code,
                        so_khach,
                        chi_phi_xe,
                        chi_phi_khach_san,
                        chi_phi_an_uong,
                        chi_phi_ve,
                        chi_phi_hdv,
                        chi_phi_khac,
                        tong_chi_phi,
                        gia_von_khach,
                        ty_le_loi_nhuan,
                        tien_loi_nhuan,
                        tien_vat,
                        gia_ban_khach,
                        ghi_chu,
                        datetime.now()
                    )
                )

                st.success(
                    f"✅ Đã lưu bảng tính giá {ma_tinh_gia} vào MySQL Aiven."
                )

            except Error as e:
                st.error(f"❌ Không thể lưu kết quả: {e}")

# ============================================================
# CHI PHÍ TOUR
# ============================================================
elif menu == "💰 Chi phí Tour":
    st.title("💰 CHI PHÍ TOUR")

    tours = db_read("SELECT * FROM tours ORDER BY ten_tour")

    if tours.empty:
        st.info("Chưa có tour.")
    else:
        tour_code = st.selectbox(
            "Chọn tour",
            tours["ma_tour"].tolist(),
            format_func=lambda x:
                f"{x} - {tours.loc[tours['ma_tour'] == x, 'ten_tour'].iloc[0]}"
        )

        st.subheader("Các bảng tính giá của tour")

        costs = db_read(
            """
            SELECT
                ma_tinh_gia,
                ma_tour,
                so_khach,
                chi_phi_xe,
                chi_phi_khach_san,
                chi_phi_an_uong,
                chi_phi_ve,
                chi_phi_hdv,
                chi_phi_khac,
                tong_chi_phi,
                gia_von_khach,
                ty_le_loi_nhuan,
                tien_loi_nhuan,
                vat,
                gia_ban_khach,
                ngay_tinh
            FROM tour_costs
            WHERE ma_tour=%s
            ORDER BY id DESC
            """,
            (tour_code,)
        )

        if costs.empty:
            st.info("Tour này chưa có bảng tính giá.")
        else:
            display = costs.copy()

            money_cols = [
                "chi_phi_xe",
                "chi_phi_khach_san",
                "chi_phi_an_uong",
                "chi_phi_ve",
                "chi_phi_hdv",
                "chi_phi_khac",
                "tong_chi_phi",
                "gia_von_khach",
                "tien_loi_nhuan",
                "vat",
                "gia_ban_khach"
            ]

            for col in money_cols:
                display[col] = display[col].apply(money)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

# ============================================================
# QUẢN LÝ TOUR
# ============================================================
elif menu == "🗺️ Quản lý Tour":
    st.title("🗺️ QUẢN LÝ TOUR")

    tab1, tab2, tab3 = st.tabs(
        ["📋 Danh sách", "➕ Thêm tour", "✏️ Sửa / Xóa"]
    )

    with tab1:
        tours = db_read("SELECT * FROM tours ORDER BY id DESC")

        search = st.text_input(
            "🔎 Tìm kiếm",
            placeholder="Nhập mã tour, tên tour hoặc điểm đến..."
        )

        if search and not tours.empty:
            s = search.strip()
            tours = tours[
                tours["ma_tour"].str.contains(s, case=False, na=False)
                | tours["ten_tour"].str.contains(s, case=False, na=False)
                | tours["diem_den"].str.contains(s, case=False, na=False)
            ]

        if tours.empty:
            st.info("Không tìm thấy tour.")
        else:
            display = tours[
                [
                    "ma_tour", "ten_tour", "diem_den",
                    "thoi_gian", "ngay_khoi_hanh",
                    "so_cho", "gia_tour", "trang_thai"
                ]
            ].copy()

            display["gia_tour"] = display["gia_tour"].apply(money)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

    with tab2:
        st.subheader("➕ Thêm tour mới")

        with st.form("add_tour"):
            a, b = st.columns(2)

            with a:
                ma = st.text_input("Mã tour *")
                ten = st.text_input("Tên tour *")
                diem = st.text_input("Điểm đến *")
                tg = st.text_input("Thời gian")
                so_ngay = st.number_input(
                    "Số ngày", min_value=1, max_value=100, value=1
                )
                gia = st.number_input(
                    "Giá tour",
                    min_value=0.0,
                    max_value=1000000000.0,
                    value=0.0,
                    step=100000.0
                )

            with b:
                khoi = st.text_input("Ngày khởi hành")
                ket = st.text_input("Ngày kết thúc")
                cho = st.number_input(
                    "Số chỗ", min_value=1, max_value=1000, value=40
                )
                hdv = st.text_input("Hướng dẫn viên")
                tt = st.selectbox(
                    "Trạng thái",
                    ["Đang hoạt động", "Tạm dừng", "Đã kết thúc"]
                )
                mota = st.text_area("Thông tin tour")

            submit = st.form_submit_button(
                "💾 LƯU TOUR",
                use_container_width=True
            )

        if submit:
            if not ma or not ten or not diem:
                st.error("Vui lòng nhập đầy đủ các trường bắt buộc.")
            else:
                try:
                    db_write(
                        """
                        INSERT INTO tours (
                            ma_tour, ten_tour, diem_den,
                            thoi_gian, so_ngay,
                            ngay_khoi_hanh, ngay_ket_thuc,
                            so_cho, gia_tour,
                            huong_dan_vien, trang_thai,
                            mo_ta, ngay_tao
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            ma, ten, diem, tg, so_ngay,
                            khoi, ket, cho, gia, hdv, tt,
                            mota, datetime.now()
                        )
                    )

                    st.success("✅ Thêm tour thành công!")
                    st.rerun()

                except Error as e:
                    st.error(f"❌ {e}")

    with tab3:
        tours = db_read("SELECT * FROM tours ORDER BY id")

        if tours.empty:
            st.info("Chưa có tour.")
        else:
            selected = st.selectbox(
                "Chọn tour",
                tours["id"].tolist(),
                format_func=lambda x:
                    f"{tours.loc[tours['id'] == x, 'ma_tour'].iloc[0]} - "
                    f"{tours.loc[tours['id'] == x, 'ten_tour'].iloc[0]}"
            )

            tour = tours[tours["id"] == selected].iloc[0]

            with st.form("edit_tour"):
                a, b = st.columns(2)

                with a:
                    ma = st.text_input("Mã tour", str(tour["ma_tour"]))
                    ten = st.text_input("Tên tour", str(tour["ten_tour"]))
                    diem = st.text_input("Điểm đến", str(tour["diem_den"]))
                    tg = st.text_input(
                        "Thời gian",
                        str(tour["thoi_gian"] or "")
                    )
                    so_ngay = st.number_input(
                        "Số ngày",
                        min_value=1,
                        max_value=100,
                        value=int(tour["so_ngay"] or 1)
                    )
                    gia = st.number_input(
                        "Giá tour",
                        min_value=0.0,
                        max_value=1000000000.0,
                        value=float(tour["gia_tour"] or 0),
                        step=100000.0
                    )

                with b:
                    khoi = st.text_input(
                        "Ngày khởi hành",
                        str(tour["ngay_khoi_hanh"] or "")
                    )
                    ket = st.text_input(
                        "Ngày kết thúc",
                        str(tour["ngay_ket_thuc"] or "")
                    )
                    cho = st.number_input(
                        "Số chỗ",
                        min_value=1,
                        max_value=1000,
                        value=int(tour["so_cho"] or 1)
                    )
                    hdv = st.text_input(
                        "Hướng dẫn viên",
                        str(tour["huong_dan_vien"] or "")
                    )

                    statuses = [
                        "Đang hoạt động",
                        "Tạm dừng",
                        "Đã kết thúc"
                    ]

                    tt = st.selectbox(
                        "Trạng thái",
                        statuses,
                        index=(
                            statuses.index(tour["trang_thai"])
                            if tour["trang_thai"] in statuses
                            else 0
                        )
                    )

                    mota = st.text_area(
                        "Thông tin tour",
                        str(tour["mo_ta"] or "")
                    )

                c1, c2 = st.columns(2)

                update = c1.form_submit_button(
                    "💾 CẬP NHẬT",
                    use_container_width=True
                )

                delete = c2.form_submit_button(
                    "🗑️ XÓA TOUR",
                    use_container_width=True
                )

            if update:
                try:
                    db_write(
                        """
                        UPDATE tours SET
                            ma_tour=%s,
                            ten_tour=%s,
                            diem_den=%s,
                            thoi_gian=%s,
                            so_ngay=%s,
                            ngay_khoi_hanh=%s,
                            ngay_ket_thuc=%s,
                            so_cho=%s,
                            gia_tour=%s,
                            huong_dan_vien=%s,
                            trang_thai=%s,
                            mo_ta=%s
                        WHERE id=%s
                        """,
                        (
                            ma, ten, diem, tg, so_ngay,
                            khoi, ket, cho, gia, hdv,
                            tt, mota, selected
                        )
                    )

                    st.success("✅ Cập nhật thành công!")
                    st.rerun()

                except Error as e:
                    st.error(f"❌ {e}")

            if delete:
                try:
                    db_write(
                        "DELETE FROM tours WHERE id=%s",
                        (selected,)
                    )
                    st.success("🗑️ Đã xóa tour.")
                    st.rerun()
                except Error as e:
                    st.error(f"❌ {e}")

# ============================================================
# KHÁCH HÀNG
# ============================================================
elif menu == "👥 Khách hàng":
    st.title("👥 QUẢN LÝ KHÁCH HÀNG")

    tab1, tab2 = st.tabs(
        ["📋 Danh sách", "➕ Thêm khách hàng"]
    )

    with tab1:
        customers = db_read(
            "SELECT * FROM customers ORDER BY id DESC"
        )

        if customers.empty:
            st.info("Chưa có khách hàng.")
        else:
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

    with tab2:
        with st.form("customer_form"):
            ma = st.text_input("Mã khách hàng *")
            ten = st.text_input("Họ và tên *")
            phone = st.text_input("Số điện thoại")
            email = st.text_input("Email")
            addr = st.text_area("Địa chỉ")

            submit = st.form_submit_button(
                "💾 LƯU KHÁCH HÀNG",
                use_container_width=True
            )

        if submit:
            if not ma or not ten:
                st.error("Vui lòng nhập mã khách hàng và họ tên.")
            else:
                try:
                    db_write(
                        """
                        INSERT INTO customers (
                            ma_khach, ho_ten,
                            so_dien_thoai, email,
                            dia_chi, ngay_tao
                        )
                        VALUES (%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            ma, ten, phone,
                            email, addr, datetime.now()
                        )
                    )

                    st.success("✅ Thêm khách hàng thành công!")
                    st.rerun()

                except Error as e:
                    st.error(f"❌ {e}")

# ============================================================
# ĐẶT TOUR
# ============================================================
elif menu == "📋 Đặt Tour":
    st.title("📋 QUẢN LÝ ĐẶT TOUR")

    tours = db_read(
        """
        SELECT * FROM tours
        WHERE trang_thai='Đang hoạt động'
        ORDER BY ten_tour
        """
    )

    customers = db_read(
        "SELECT * FROM customers ORDER BY ho_ten"
    )

    if tours.empty:
        st.warning("⚠️ Chưa có tour.")
    elif customers.empty:
        st.warning(
            "⚠️ Chưa có khách hàng. Hãy thêm khách hàng trước."
        )
    else:
        tour_code = st.selectbox(
            "🚌 Chọn tour",
            tours["ma_tour"].tolist(),
            format_func=lambda x:
                f"{x} - {tours.loc[tours['ma_tour'] == x, 'ten_tour'].iloc[0]}"
        )

        tour = tours[tours["ma_tour"] == tour_code].iloc[0]

        st.info(
            f"💰 Giá tour: **{money(tour['gia_tour'])} / khách**"
        )

        customer_code = st.selectbox(
            "👤 Chọn khách hàng",
            customers["ma_khach"].tolist(),
            format_func=lambda x:
                f"{x} - {customers.loc[customers['ma_khach'] == x, 'ho_ten'].iloc[0]}"
        )

        so_nguoi = st.number_input(
            "👥 Số người",
            min_value=1,
            max_value=int(tour["so_cho"] or 1000),
            value=1
        )

        tong_tien = float(tour["gia_tour"] or 0) * so_nguoi

        st.metric(
            "💰 TỔNG TIỀN",
            money(tong_tien)
        )

        ngay_dat = st.date_input(
            "📅 Ngày đặt",
            date.today()
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
                last = db_read(
                    "SELECT id FROM bookings ORDER BY id DESC LIMIT 1"
                )

                next_id = (
                    int(last.iloc[0]["id"]) + 1
                    if not last.empty else 1
                )

                ma_dat = f"DT{next_id:04d}"

                db_write(
                    """
                    INSERT INTO bookings (
                        ma_dat_tour, ma_tour,
                        ma_khach, so_nguoi,
                        tong_tien, ngay_dat,
                        trang_thai, ghi_chu
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        ma_dat, tour_code,
                        customer_code, so_nguoi,
                        tong_tien, ngay_dat,
                        trang_thai, ghi_chu
                    )
                )

                st.success(
                    f"✅ Đã tạo đơn {ma_dat} thành công!"
                )
                st.rerun()

            except Error as e:
                st.error(f"❌ Không thể tạo đơn: {e}")

        st.markdown("---")
        st.subheader("📋 DANH SÁCH ĐẶT TOUR")

        bookings = db_read(
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
            LEFT JOIN tours t ON b.ma_tour=t.ma_tour
            LEFT JOIN customers c ON b.ma_khach=c.ma_khach
            ORDER BY b.id DESC
            """
        )

        if bookings.empty:
            st.info("Chưa có đơn đặt tour.")
        else:
            display = bookings.copy()
            display["tong_tien"] = display["tong_tien"].apply(money)

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

# ============================================================
# LỊCH SỬ TÍNH GIÁ
# ============================================================
elif menu == "📜 Lịch sử tính giá":
    st.title("📜 LỊCH SỬ TÍNH GIÁ TOUR")

    costs = db_read(
        """
        SELECT
            c.ma_tinh_gia,
            c.ma_tour,
            t.ten_tour,
            c.so_khach,
            c.tong_chi_phi,
            c.gia_von_khach,
            c.ty_le_loi_nhuan,
            c.tien_loi_nhuan,
            c.vat,
            c.gia_ban_khach,
            c.ngay_tinh
        FROM tour_costs c
        LEFT JOIN tours t ON c.ma_tour=t.ma_tour
        ORDER BY c.id DESC
        """
    )

    if costs.empty:
        st.info("Chưa có lịch sử tính giá.")
    else:
        display = costs.copy()

        for col in [
            "tong_chi_phi",
            "gia_von_khach",
            "tien_loi_nhuan",
            "vat",
            "gia_ban_khach"
        ]:
            display[col] = display[col].apply(money)

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# THỐNG KÊ
# ============================================================
elif menu == "📊 Thống kê":
    st.title("📊 THỐNG KÊ KINH DOANH")

    tours = db_read("SELECT * FROM tours")
    customers = db_read("SELECT * FROM customers")
    bookings = db_read("SELECT * FROM bookings")
    costs = db_read("SELECT * FROM tour_costs")

    revenue = 0

    if not bookings.empty:
        revenue = bookings.loc[
            bookings["trang_thai"].isin(
                ["Đã xác nhận", "Đã hoàn thành"]
            ),
            "tong_tien"
        ].sum()

    a, b, c, d = st.columns(4)

    a.metric("🚌 Tổng tour", len(tours))
    b.metric("👥 Khách hàng", len(customers))
    c.metric("📋 Đơn đặt tour", len(bookings))
    d.metric("💰 Doanh thu", money(revenue))

    st.markdown("---")

    st.subheader("🚌 Thống kê trạng thái tour")

    if tours.empty:
        st.info("Chưa có tour.")
    else:
        status = tours["trang_thai"].value_counts()

        for name, value in status.items():
            st.write(f"**{name}:** {value} tour")
            st.progress(float(value / len(tours)))

    st.subheader("💰 Doanh thu theo tour")

    if bookings.empty:
        st.info("Chưa có đơn đặt tour.")
    else:
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

        if revenue_by_tour.empty:
            st.info("Chưa có doanh thu.")
        else:
            max_value = float(revenue_by_tour.max())

            for code, value in revenue_by_tour.items():
                st.write(f"**{code}** - {money(value)}")
                st.progress(
                    float(value / max_value)
                    if max_value else 0
                )

    st.subheader("🧮 Tổng quan tính giá")

    if costs.empty:
        st.info("Chưa có dữ liệu tính giá.")
    else:
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📜 Số bảng tính giá",
            len(costs)
        )

        c2.metric(
            "💵 Giá bán TB/khách",
            money(costs["gia_ban_khach"].mean())
        )

        c3.metric(
            "📈 Lợi nhuận TB/khách",
            money(costs["tien_loi_nhuan"].mean())
        )

# ============================================================
# THÔNG TIN
# ============================================================
elif menu == "ℹ️ Thông tin":
    st.title("ℹ️ THÔNG TIN HỆ THỐNG")

    st.markdown("""
## 🚌 Hệ thống quản lý tour du lịch

### Công nghệ
- Python
- Streamlit
- MySQL Aiven
- Pandas
- mysql-connector-python

### Chức năng
- Quản lý tour
- Thêm / sửa / xóa tour
- Tìm kiếm tour
- Tính giá tour
- Tính giá vốn / khách
- Tính lợi nhuận
- Tính VAT
- Lưu lịch sử tính giá
- Quản lý khách hàng
- Tạo đơn đặt tour
- Tự động tính tổng tiền
- Theo dõi trạng thái đơn đặt tour
- Thống kê doanh thu

### Công thức tính giá

**Tổng chi phí tour**

= Xe + Khách sạn + Ăn uống + Vé + HDV + Chi phí khác

**Giá vốn / khách**

= Tổng chi phí / Số khách

**Lợi nhuận / khách**

= Giá vốn × Tỷ lệ lợi nhuận

**Giá trước VAT**

= Giá vốn + Lợi nhuận

**VAT / khách**

= Giá trước VAT × Thuế VAT

**Giá bán / khách**

= Giá trước VAT + VAT

### Database

MySQL Aiven - database `defaultdb`.
""")
