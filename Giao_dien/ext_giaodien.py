import os
import json
import datetime
import qrcode
import pandas as pd
from PyQt6.QtGui import QIcon, QPixmap, QColor, QImage, QAction, QBrush, QPainter, QPen
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QApplication, QStackedWidget, QMainWindow, QDialog, QFrame,
                             QLabel, QWidget, QPushButton, QHBoxLayout, QTableWidget,
                             QLineEdit, QHeaderView, QTableWidgetItem, QVBoxLayout, QMessageBox, QFileDialog, QStyle, QInputDialog)
from PyQt6.uic import loadUi

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

# -- HÀM HỖ TRỢ ĐƯỜNG DẪN --
def get_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# ================= CLASS LOGIN & REGISTER =================
class Login(QDialog):
    def __init__(self, widget):
        super().__init__()
        loadUi(get_path("login.ui"), self)
        self.widget = widget
        self.btn_log.clicked.connect(self.log)
        self.btn_log.setEnabled(False)
        self.log_name.textChanged.connect(self.check_inputs_log)
        self.log_pass.textChanged.connect(self.check_inputs_log)
        self.lbl_reg.linkActivated.connect(self.goto_reg)
        
        self.log_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        eye_icon_path = get_path("icon/eye.png")
        if os.path.exists(eye_icon_path):
            self.action_log = self.log_pass.addAction(QIcon(eye_icon_path), QLineEdit.ActionPosition.TrailingPosition)
            self.action_log.triggered.connect(self.toggle_pass)
            
        self.warn_log.hide()

    def toggle_pass(self):
        if self.log_pass.echoMode() == QLineEdit.EchoMode.Password:
            self.log_pass.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.log_pass.setEchoMode(QLineEdit.EchoMode.Password)

    def log(self):
        name = self.log_name.text()
        password = self.log_pass.text()
        users = load_json(get_path("data/users.json"))
        
        # Tìm user xem có khớp không
        user_info = next((u for u in users if u.get("name") == name and u.get("password") == password), None)
        
        if user_info:
            self.warn_log.hide()
            # Mặc định tài khoản cũ không có trường role sẽ là admin
            role = user_info.get("role", "admin") 
            
            if role == "admin":
                main_screen = self.widget.widget(2)
                main_screen.profile(name)
                main_screen.refresh_all_data()
                self.widget.setCurrentIndex(2)
            else:
                # Nếu là khách hàng mới tạo, hiển thị màn hình riêng
                self.show_customer_view(name)
        else:
            self.warn_log.setText("Sai tài khoản hoặc mật khẩu!")
            self.warn_log.show()

    def show_customer_view(self, name):
        # Tự động tạo một màn hình trắng cơ bản cho khách nếu chưa có
        if not hasattr(self, "cust_view"):
            self.cust_view = QWidget()
            self.cust_view.setStyleSheet("background-color: #EBF5FF;")
            layout = QVBoxLayout()
            
            self.cust_lbl = QLabel()
            self.cust_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cust_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E40AF;")
            
            btn_logout = QPushButton(" Đăng xuất")
            btn_logout.setIcon(QIcon(get_path("icon/logout.png")))
            btn_logout.setFixedSize(150, 45)
            btn_logout.setStyleSheet("""
                QPushButton {
                    background-color: white; color: #EF4444; font-weight: bold;
                    border: 2px solid #FECACA; border-radius: 8px; font-size: 15px;
                }
                QPushButton:hover { background-color: #FEF2F2; border: 2px solid #EF4444; }
            """)
            btn_logout.clicked.connect(lambda: self.widget.setCurrentIndex(0))
            
            layout.addStretch()
            layout.addWidget(self.cust_lbl)
            layout.addSpacing(30)
            layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addStretch()
            
            self.cust_view.setLayout(layout)
            self.widget.addWidget(self.cust_view)
        
        self.cust_lbl.setText(f"Xin chào {name}!\n\nĐây là tài khoản Khách.\nGiao diện mua sắm đang được phát triển nhé!")
        self.widget.setCurrentWidget(self.cust_view)

    def check_inputs_log(self):
        self.btn_log.setEnabled(bool(self.log_name.text().strip() and self.log_pass.text().strip()))

    def goto_reg(self):
        self.widget.setCurrentIndex(1)


class Register(QDialog):
    def __init__(self, widget):
        super().__init__()
        loadUi(get_path("register.ui"), self)
        self.widget = widget
        self.btn_reg.clicked.connect(self.reg)
        self.btn_reg.setEnabled(False)
        self.reg_name.textChanged.connect(self.check_inputs_reg)
        self.reg_pass.textChanged.connect(self.check_inputs_reg)
        self.conf_pass.textChanged.connect(self.check_inputs_reg)
        self.lbl_log.linkActivated.connect(self.goto_log)
        
        self.reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.conf_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        eye_icon_path = get_path("icon/eye.png")
        if os.path.exists(eye_icon_path):
            self.action_reg = self.reg_pass.addAction(QIcon(eye_icon_path), QLineEdit.ActionPosition.TrailingPosition)
            self.action_conf = self.conf_pass.addAction(QIcon(eye_icon_path), QLineEdit.ActionPosition.TrailingPosition)
            self.action_reg.triggered.connect(lambda: self.toggle_pass(self.reg_pass))
            self.action_conf.triggered.connect(lambda: self.toggle_pass(self.conf_pass))

        self.warn_reg.hide()

    def toggle_pass(self, line_edit):
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def reg(self):
        name = self.reg_name.text().strip()
        password = self.reg_pass.text().strip()
        if password != self.conf_pass.text().strip():
            self.warn_reg.setText("Mật khẩu không khớp!")
            self.warn_reg.show()
            return
            
        users = load_json(get_path("data/users.json"))
        if any(u.get("name") == name for u in users):
            self.warn_reg.setText("Tên đăng nhập đã tồn tại!")
            self.warn_reg.show()
            return
            
        # Tài khoản đăng ký mới tự động nhận role "customer"
        users.append({"name": name, "password": password, "role": "customer"})
        save_json(get_path("data/users.json"), users)
        self.goto_log()

    def check_inputs_reg(self):
        self.btn_reg.setEnabled(bool(self.reg_name.text() and self.reg_pass.text() and self.conf_pass.text()))

    def goto_log(self):
        self.widget.setCurrentIndex(0)


# ================= CLASS LỊCH SỬ KHÁCH HÀNG =================
class CustomerHistory(QDialog):
    def __init__(self, parent, cust_name, cust_phone):
        super().__init__(parent)
        loadUi(get_path("customer_history.ui"), self)
        
        self.label.setText(f"Lịch sử mua hàng - {cust_name}")
        
        # Load thông tin điểm
        customers = load_json(get_path("data/customers.json"))
        cust = next((c for c in customers if c.get("phone") == cust_phone), None)
        if cust:
            pts = cust.get("points", 0)
            self.lbl_points.setText(f"{pts} Điểm")
            rank = "Kim Cương" if pts >= 100 else "Vàng" if pts >= 50 else "Bạc" if pts >= 25 else "Đồng" if pts >= 10 else "Thường"
            self.lbl_rank.setText(rank)
            
        # Load danh sách đơn
        orders = load_json(get_path("data/orders.json"))
        cust_orders = [o for o in orders if o.get("customer") == cust_name]
        
        self.tableWidget.setRowCount(len(cust_orders))
        for row, o in enumerate(cust_orders):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(o.get("id", "")))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(o.get("date", "")))
            items_str = ", ".join([f"{i['name']} (x{i['qty']})" for i in o.get("items", [])])
            self.tableWidget.setItem(row, 2, QTableWidgetItem(items_str))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(f"{o.get('total', 0):,} đ"))
            
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_cancel.clicked.connect(self.close)


# ================= CLASS MAIN =================
class Main(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        loadUi(get_path("manage.ui"), self)
        self.widget = widget
        
        self.setStyleSheet("QMessageBox { color: black; background-color: white; }")
        
        self.widget.resize(1152, 616)
        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        self.listWidget.setCurrentRow(0)

        self.btn_logo.setText(" 8386 Shop")
        self.btn_logo.setIcon(QIcon(get_path("icon/shop.png")))
        self.btn_logo.setIconSize(QSize(40, 40))

        self.btn_logout.setText(" Đăng xuất")
        self.btn_logout.setIcon(QIcon(get_path("icon/logout.png")))

        item_rep = self.listWidget.item(0)
        item_pro = self.listWidget.item(1)
        item_orders = self.listWidget.item(2)
        item_cus = self.listWidget.item(3)

        if item_rep: item_rep.setIcon(self.change_color("reports_blue.png", "reports_white.png"))
        if item_pro: item_pro.setIcon(self.change_color("products_blue.png", "products_white.png"))
        if item_orders: item_orders.setIcon(self.change_color("orders_blue.png", "orders_white.png"))
        if item_cus: item_cus.setIcon(self.change_color("customer_blue.png", "customer_white.png"))
        self.listWidget.setIconSize(QSize(24, 24))

        for table in [self.table_products, self.table_orders, self.table_customers]:
            if hasattr(self, table.objectName()):
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        black_title_style = "color: #000000; font-weight: bold; font-size: 25pt;"
        if hasattr(self, 'label_5'): self.label_5.setStyleSheet(black_title_style)   
        if hasattr(self, 'label_22'): self.label_22.setStyleSheet(black_title_style) 
        if hasattr(self, 'label_24'): self.label_24.setStyleSheet(black_title_style) 
        if hasattr(self, 'label_25'): self.label_25.setStyleSheet(black_title_style) 

        self.btn_logout.clicked.connect(self.logout)
        self.btn_add.clicked.connect(self.open_add_product)
        self.btn_edit.clicked.connect(self.open_edit_product) 
        self.btn_del.clicked.connect(self.delete_product)
        self.add_order.clicked.connect(self.open_add_order)
        self.btn_excel.clicked.connect(self.export_excel)
        
        # Kết nối nút lịch sử mua hàng
        if hasattr(self, 'btn_history'):
            self.btn_history.clicked.connect(self.show_customer_history)

        if hasattr(self, 'customer_search'):
            self.customer_search.setStyleSheet("color: #1E40AF; background-color: white; border: 1px solid #CBD5E1; border-radius: 4px;")
            self.customer_search.setPlaceholderText(" Tìm kiếm khách hàng...")
            self.customer_search.textChanged.connect(self.filter_customers)

        if hasattr(self, 'date_picker'):
            self.date_picker.dateChanged.connect(self.load_reports)

        self.table_products.itemSelectionChanged.connect(self.toggle_edit_delete)
        self.btn_del.setEnabled(False)
        self.btn_edit.setEnabled(False)

        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self.frame_bieudo)
        layout.addWidget(self.canvas)

        if hasattr(self, 'cbo_report_type'):
            self.cbo_report_type.currentIndexChanged.connect(self.load_reports)
            
        if hasattr(self, 'date_picker'):
            self.date_picker.setDate(datetime.date.today())
            self.date_picker.dateChanged.connect(self.load_reports)

    def filter_customers(self):
        search_text = self.customer_search.text().lower()
        for row in range(self.table_customers.rowCount()):
            item_name = self.table_customers.item(row, 0).text().lower()
            item_phone = self.table_customers.item(row, 1).text().lower()
            is_match = search_text in item_name or search_text in item_phone
            self.table_customers.setRowHidden(row, not is_match)

    def refresh_all_data(self):
        self.load_products()
        self.load_customers()
        self.load_reports()
        self.load_orders()

    def profile(self, username):
        self.btn_name.setText(f"   {username}")
        icon_avatar = get_path("icon/user.png")
        self.btn_name.setIcon(QIcon(icon_avatar))
        self.btn_name.setIconSize(QSize(30, 30))

    def change_color(self, original, selected):
        icon = QIcon()
        goc = get_path(f"icon/{original}")
        chon = get_path(f"icon/{selected}")
        if os.path.exists(goc):
            icon.addPixmap(QPixmap(goc), QIcon.Mode.Normal, QIcon.State.Off)
        if os.path.exists(chon):
            icon.addPixmap(QPixmap(chon), QIcon.Mode.Selected, QIcon.State.Off)
        return icon

    def logout(self):
        self.widget.setCurrentIndex(0)
        
    def show_customer_history(self):
        row = self.table_customers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chưa chọn khách hàng", "Vui lòng bấm chọn một khách hàng trong bảng trước!")
            return
        cust_name = self.table_customers.item(row, 0).text()
        cust_phone = self.table_customers.item(row, 1).text()
        dialog = CustomerHistory(self, cust_name, cust_phone)
        dialog.exec()

    # --- QUẢN LÝ SẢN PHẨM ---
    def load_products(self):
        products = load_json(get_path("data/products.json"))
        
        self.table_products.setColumnCount(7)
        self.table_products.setHorizontalHeaderLabels(["Tên sản phẩm", "Size", "Màu", "Số lượng", "Giá bán", "Giá gốc", "Trạng thái"])

        header = self.table_products.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        self.table_products.setRowCount(len(products))
        for row, p in enumerate(products):
            item_name = QTableWidgetItem(p["name"])
            item_size = QTableWidgetItem(p["size"])
            item_color = QTableWidgetItem(p["color"])
            
            qty = int(p.get("qty", 0))
            item_qty = QTableWidgetItem(str(qty))
            item_price = QTableWidgetItem(f"{p['price']:,} đ")
            
            cost = p.get("cost", p["price"] * 0.7)
            item_cost = QTableWidgetItem(f"{int(cost):,} đ")
            
            status = "Còn hàng" if qty > 0 else "Hết hàng"
            item_status = QTableWidgetItem(status)
            
            if qty <= 5:
                red_brush = QBrush(QColor("red"))
                bg_brush = QBrush(QColor("#fee2e2")) 
                for item in [item_name, item_size, item_color, item_qty, item_price, item_cost, item_status]:
                    item.setForeground(red_brush)
                    item.setBackground(bg_brush)
            else:
                black_brush = QBrush(QColor("black"))
                for item in [item_name, item_size, item_color, item_qty, item_price, item_cost, item_status]:
                    item.setForeground(black_brush)
            
            self.table_products.setItem(row, 0, item_name)
            self.table_products.setItem(row, 1, item_size)
            self.table_products.setItem(row, 2, item_color)
            self.table_products.setItem(row, 3, item_qty)
            self.table_products.setItem(row, 4, item_price)
            self.table_products.setItem(row, 5, item_cost)
            self.table_products.setItem(row, 6, item_status)

    def toggle_edit_delete(self):
        has_selection = len(self.table_products.selectedItems()) > 0
        self.btn_del.setEnabled(has_selection)
        self.btn_edit.setEnabled(has_selection)

    def open_add_product(self):
        dialog = AddProduct(self)
        dialog.exec()
        self.load_products()

    def open_edit_product(self):
        row = self.table_products.currentRow()
        if row < 0: return
        products = load_json(get_path("data/products.json"))
        product_data = products[row]
        
        dialog = EditProduct(self, product_data, row)
        dialog.exec()
        self.load_products()

    def delete_product(self):
        row = self.table_products.currentRow()
        if row < 0: return
        products = load_json(get_path("data/products.json"))
        products.pop(row)
        save_json(get_path("data/products.json"), products)
        self.load_products()

    # --- QUẢN LÝ KHÁCH HÀNG ---
    def load_customers(self):
        customers = load_json(get_path("data/customers.json"))
        self.table_customers.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.table_customers.setItem(row, 0, QTableWidgetItem(c["name"]))
            self.table_customers.setItem(row, 1, QTableWidgetItem(c.get("phone", "")))
            self.table_customers.setItem(row, 2, QTableWidgetItem(c.get("email", "")))
            self.table_customers.setItem(row, 3, QTableWidgetItem(str(c["points"])))
            
            pts = c["points"]
            rank = "Kim Cương" if pts >= 100 else "Vàng" if pts >= 50 else "Bạc" if pts >= 25 else "Đồng" if pts >= 10 else "Thường"
            self.table_customers.setItem(row, 4, QTableWidgetItem(rank))

    # --- ĐƠN HÀNG & BÁO CÁO ---
    def open_add_order(self):
        dialog = AddOrder(self)
        dialog.exec()
        self.refresh_all_data()
        self.listWidget.setCurrentRow(2)

    def load_orders(self):
        orders = load_json(get_path("data/orders.json"))
        self.table_orders.setRowCount(len(orders))
        for row, o in enumerate(orders):
            self.table_orders.setItem(row, 0, QTableWidgetItem(o["id"]))
            self.table_orders.setItem(row, 1, QTableWidgetItem(o["customer"]))
            self.table_orders.setItem(row, 2, QTableWidgetItem(str(len(o["items"])) + " món"))
            self.table_orders.setItem(row, 3, QTableWidgetItem(f"{o['total']:,} đ"))
            self.table_orders.setItem(row, 4, QTableWidgetItem(o["method"]))

    def load_reports(self):
        if hasattr(self, 'frame_3'): self.frame_3.setMinimumHeight(120)
        if hasattr(self, 'frame_8'): self.frame_8.setMinimumHeight(120)
        if hasattr(self, 'frame_9'): self.frame_9.setMinimumHeight(120)
        
        orders = load_json(get_path("data/orders.json"))
        
        # --- LOGIC LỌC MỚI BỔ SUNG ---
        filter_type = self.cbo_report_type.currentText() if hasattr(self, 'cbo_report_type') else "Tất cả"
        # Lấy ngày được chọn từ widget date_picker
        selected_date = self.date_picker.date().toPyDate().strftime("%Y-%m-%d") if hasattr(self, 'date_picker') else ""
        selected_month = selected_date[:7] # Định dạng YYYY-MM
        # -----------------------------

        total_rev = 0
        total_profit = 0
        monthly_stats = {}
        product_sales = {}

        for o in orders:
            order_date = o.get("date", "2026-01-01")
            month_key = order_date[:7]

            # --- KIỂM TRA ĐIỀU KIỆN LỌC ---
            if filter_type == "Theo ngày" and order_date != selected_date:
                continue
            elif filter_type == "Theo tháng" and month_key != selected_month:
                continue
            # ------------------------------

            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'rev': 0, 'prof': 0}

            order_rev = 0
            order_prof = 0
            for item in o.get("items", []):
                qty = item.get("qty", 0)
                price = item.get("price", 0)
                cost = item.get("cost", price * 0.7 * qty)

                rev = price * qty
                prof = rev - cost

                order_rev += rev
                order_prof += prof

                name = item.get("name", "")
                product_sales[name] = product_sales.get(name, 0) + qty

            total_rev += order_rev
            total_profit += order_prof
            monthly_stats[month_key]['rev'] += order_rev
            monthly_stats[month_key]['prof'] += order_prof

        if hasattr(self, 'lbl_income'):
            self.lbl_income.setStyleSheet("color: black; font-weight: bold;")
            self.lbl_income.setText(f"{int(total_rev):,} đ")
        if hasattr(self, 'lbl_profit'):
            self.lbl_profit.setStyleSheet("color: black; font-weight: bold;")
            self.lbl_profit.setText(f"{int(total_profit):,} đ")

        best_month_str = "..."
        if monthly_stats:
            best_month = max(monthly_stats, key=lambda k: monthly_stats[k]['rev'])
            best_month_str = f"{best_month[5:]}/{best_month[:4]}" 
            
            if hasattr(self, 'label_27'):
                self.label_27.setText(f"Doanh thu: {int(monthly_stats[best_month]['rev']):,} đ")
            
        if hasattr(self, 'lbl_best'): 
            self.lbl_best.setStyleSheet("color: black; font-weight: bold;")
            self.lbl_best.setText(best_month_str)

        if hasattr(self, 'tableWidget'):
            self.tableWidget.setRowCount(len(monthly_stats))
            self.tableWidget.setHorizontalHeaderLabels(["Tháng", "Doanh thu", "Lợi nhuận"])
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            sorted_months = sorted(monthly_stats.items(), reverse=True)
            
            for row, (month, stats) in enumerate(sorted_months):
                display_month = f"{month[5:]}/{month[:4]}"
                self.tableWidget.setItem(row, 0, QTableWidgetItem(display_month))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(f"{int(stats['rev']):,} đ"))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(f"{int(stats['prof']):,} đ"))

        if hasattr(self, 'frame_bieudo_2'):
            if not self.frame_bieudo_2.layout():
                layout_top5 = QVBoxLayout(self.frame_bieudo_2)
                layout_top5.setContentsMargins(15, 45, 15, 15)
                self.top5_table = QTableWidget()
                self.top5_table.setColumnCount(2)
                self.top5_table.setHorizontalHeaderLabels(["Sản phẩm", "Đã bán"])
                self.top5_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                self.top5_table.verticalHeader().setVisible(False)
                self.top5_table.setStyleSheet("QTableWidget { background-color: white; border: none; } QHeaderView::section { background-color: #EFF6FF; color: #1E40AF; font-weight: bold; border: none; padding: 5px; }")
                layout_top5.addWidget(self.top5_table)
            
            top5 = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
            self.top5_table.setRowCount(len(top5))
            for row, (name, qty) in enumerate(top5):
                it_name = QTableWidgetItem(name)
                it_qty = QTableWidgetItem(str(qty))
                it_name.setForeground(QBrush(QColor("black")))
                it_qty.setForeground(QBrush(QColor("black")))
                self.top5_table.setItem(row, 0, it_name)
                self.top5_table.setItem(row, 1, it_qty)

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Chỉnh lề biểu đồ để tận dụng không gian rộng hơn
        self.fig.subplots_adjust(left=0.15, bottom=0.25, right=0.95, top=0.9)
        
        if monthly_stats:
            sorted_months = sorted(monthly_stats.keys())
            dates = [f"{m[5:]}/{m[:4]}" for m in sorted_months]
            revs = [monthly_stats[m]['rev'] for m in sorted_months]
            
            ax.plot(dates, revs, marker='o', color='#2563EB', linestyle='-', linewidth=2, markersize=6)
            ax.set_title("Biểu đồ doanh thu")
            
            # --- CHỈNH CHỮ TRỤC HOÀNH NHỎ HƠN 50% ---
            # Sử dụng fontsize nhỏ (ví dụ: 6 hoặc 7) để chữ không bị đè lên nhau
            ax.tick_params(axis='x', labelsize=7, rotation=45) 
            ax.tick_params(axis='y', labelsize=8)
            
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
            
        self.canvas.draw()

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo Excel", "", "Excel Files (*.xlsx)")
        if path:
            orders = load_json(get_path("data/orders.json"))
            df = pd.DataFrame(orders)
            df.to_excel(path, index=False)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Thành công")
            msg_box.setText("Đã xuất file Excel!")
            msg_box.setStyleSheet("""
                QMessageBox { background-color: white; }
                QLabel { color: black; font-size: 13px; }
                QPushButton { color: black; background-color: #E2E8F0; padding: 6px 15px; border: 1px solid #94A3B8; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #CBD5E1; }
                """)
            msg_box.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
            
        if hasattr(self, 'add_order') and hasattr(self, 'table_orders'):
            y_buttons = 45 
            right_margin = self.table_orders.x() + self.table_orders.width()
                
            if hasattr(self, 'btn_excel'):
                x_excel = right_margin - self.btn_excel.width()
                x_add = x_excel - self.add_order.width() - 15 
                    
                self.btn_excel.move(int(x_excel), int(y_buttons))
                self.add_order.move(int(x_add), int(y_buttons))
            else:
                x_add = right_margin - self.add_order.width()
                self.add_order.move(int(x_add), int(y_buttons))
            
        if hasattr(self, 'layoutWidget') and hasattr(self, 'table_products'):
            x = self.table_products.x() + self.table_products.width() - self.layoutWidget.width()
            y = self.table_products.y() - self.layoutWidget.height() - 10
            self.layoutWidget.move(int(x), int(y))


# ================= CÁC DIALOG CHỨC NĂNG =================
class AddProduct(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        loadUi(get_path("add_products.ui"), self)
        
        self.resize(500, self.height())
        
        for lbl in self.findChildren(QLabel):
            font = lbl.font()
            if font.pointSize() > 14 or font.pixelSize() > 18:
                lbl.setMinimumWidth(480)
                lbl.resize(480, lbl.height())
                # Dịch sang trái khoảng 1cm (~40 pixel so với vị trí cũ)
                lbl.move(-30, lbl.y())  
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #1E40AF; font-weight: bold;")

        self.btn_cancel.clicked.connect(self.close)
        self.btn_them.clicked.connect(self.save_product)

    def save_product(self):
        products = load_json(get_path("data/products.json"))
        cost_val = int(self.line_price.text() or 0)
        new_prod = {
            "id": f"P0{len(products)+1}",
            "name": self.line_name.text(),
            "size": self.line_size.text(),
            "color": self.line_color.text(),
            "qty": int(self.line_quan.text() or 0),
            "cost": cost_val,
            "price": int(cost_val * 1.25)
        }
        products.append(new_prod)
        save_json(get_path("data/products.json"), products)
        self.close()


class EditProduct(QDialog):
    def __init__(self, parent, product_data, row_index):
        super().__init__(parent)
        loadUi(get_path("edit.ui"), self)
        self.row_index = row_index
        
        self.resize(500, self.height())
        
        for lbl in self.findChildren(QLabel):
            font = lbl.font()
            if font.pointSize() > 14 or font.pixelSize() > 18:
                lbl.setMinimumWidth(480)
                lbl.resize(480, lbl.height())
                # Dịch sang trái khoảng 1cm (~40 pixel so với vị trí cũ)
                lbl.move(-30, lbl.y())  
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #1E40AF; font-weight: bold;")
        
        self.edt_name.setText(product_data["name"])
        self.edt_size.setText(product_data["size"])
        self.edt_color.setText(product_data["color"])
        self.edt_quan.setText(str(product_data["qty"]))
        
        cost_val = product_data.get("cost", product_data["price"] * 0.7)
        self.edt_price.setText(str(int(cost_val)))

        self.edt_cancel.clicked.connect(self.close)
        self.btn_save.clicked.connect(self.save_edit)

    def save_edit(self):
        products = load_json(get_path("data/products.json"))
        products[self.row_index]["name"] = self.edt_name.text()
        products[self.row_index]["size"] = self.edt_size.text()
        products[self.row_index]["color"] = self.edt_color.text()
        products[self.row_index]["qty"] = int(self.edt_quan.text() or 0)
        
        cost_val = int(self.edt_price.text() or 0)
        products[self.row_index]["cost"] = cost_val
        products[self.row_index]["price"] = int(cost_val * 1.25) 
        
        save_json(get_path("data/products.json"), products)
        self.close()

class AddOrder(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        loadUi(get_path("add_order.ui"), self)
        
        self.setStyleSheet("""
            QDialog { background-color: #F8FAFC; }
            QLabel, QLineEdit, QComboBox { color: black; }
            QLineEdit, QComboBox, QTableWidget { background-color: white; }
            QComboBox QAbstractItemView { color: black; background-color: white; }
            QHeaderView::section { color: black; background-color: #E2E8F0; }
            QMessageBox { color: black; background-color: white; }
            QTableWidget { color: black; font-weight: bold; background-color: white; }
        """)
        
        self.table_cart.setColumnCount(4)
        self.table_cart.setHorizontalHeaderLabels(["Sản phẩm", "Giá", "Số lượng", "Thành tiền"])
        self.table_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cart.setRowCount(0)
        
        self.order_cancel.clicked.connect(self.close)
        self.btn_pay.clicked.connect(self.process_payment)
        
        self.products = load_json(get_path("data/products.json"))
        self.cbo_product.addItems([p["name"] for p in self.products])
        self.btn_cart.clicked.connect(self.add_to_cart)
        
        self.cart = []
        self.total = 0
        self.profit = 0
        self.btn_pay.setEnabled(False)

    def add_to_cart(self):
        prod_name = self.cbo_product.currentText()
        qty = int(self.line_qty.text() or 1)
        prod = next((p for p in self.products if p["name"] == prod_name), None)
        
        if prod and prod["qty"] >= qty:
            price = prod["price"]
            subtotal = price * qty
            self.cart.append({"name": prod_name, "qty": qty, "price": price, "subtotal": subtotal, "cost": prod.get("cost", price*0.7)*qty})
            self.update_cart_table()
        else:
            msg_err = QMessageBox(self)
            msg_err.setIcon(QMessageBox.Icon.Warning)
            msg_err.setWindowTitle("Lỗi")
            msg_err.setText("Sản phẩm đã hết hoặc không đủ số lượng!")
            msg_err.setStyleSheet("""
                QMessageBox { background-color: white; }
                QLabel { color: black; font-size: 13px; }
                QPushButton { color: black; background-color: #E2E8F0; padding: 6px 15px; border: 1px solid #94A3B8; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #CBD5E1; }
            """)
            msg_err.exec()

    def update_cart_table(self):
        self.table_cart.setRowCount(len(self.cart))
        subtotal_sum = 0
        cost_sum = 0
        
        black_brush = QBrush(QColor("black"))
        
        for row, item in enumerate(self.cart):
            item_n = QTableWidgetItem(item["name"])
            item_p = QTableWidgetItem(str(item["price"]))
            item_q = QTableWidgetItem(str(item["qty"]))
            item_s = QTableWidgetItem(str(item["subtotal"]))
            
            item_n.setForeground(black_brush)
            item_p.setForeground(black_brush)
            item_q.setForeground(black_brush)
            item_s.setForeground(black_brush)
            
            self.table_cart.setItem(row, 0, item_n)
            self.table_cart.setItem(row, 1, item_p)
            self.table_cart.setItem(row, 2, item_q)
            self.table_cart.setItem(row, 3, item_s)
            
            subtotal_sum += item["subtotal"]
            cost_sum += item["cost"]

        cust_name = self.line_customer.text().strip().lower()
        customers = load_json(get_path("data/customers.json"))
        cust = next((c for c in customers if c["name"].strip().lower() == cust_name), None)
        
        discount = 0
        if cust:
            pts = cust.get("points", 0)
            if pts >= 100: discount = 0.07 
            elif pts >= 50: discount = 0.05 
            elif pts >= 25: discount = 0.03 

        self.total = (subtotal_sum * 1.08) * (1 - discount)
        self.profit = self.total - cost_sum
        
        self.lbl_total.setText(f"{int(self.total):,} đ (Thuế 8%, Giảm {int(discount*100)}%)")
        self.btn_pay.setEnabled(len(self.cart) > 0)

    def process_payment(self):
        dialog = PayMethod(self, self.total)
        if dialog.exec():
            cust_input = self.line_customer.text().strip()
            final_customer_name = cust_input if cust_input else "Khách lẻ"
            
            customers = load_json(get_path("data/customers.json"))
            earned_points = int(self.total) // 10000 
            
            if cust_input:
                # Tách riêng form yêu cầu sđt và ép màu nút bấm để không bị chìm
                input_dialog = QInputDialog(self)
                input_dialog.setWindowTitle("Xác nhận số điện thoại")
                input_dialog.setLabelText(f"Nhập số điện thoại của '{cust_input}' để tích điểm\n(Bỏ trống nếu không muốn tích điểm):")
                input_dialog.setStyleSheet("""
                    QDialog { background-color: white; }
                    QLabel { color: black; font-size: 13px; }
                    QLineEdit { color: black; background-color: white; border: 1px solid #94A3B8; padding: 4px; }
                    QPushButton { color: black; background-color: #E2E8F0; padding: 6px 15px; border: 1px solid #94A3B8; border-radius: 4px; font-weight: bold; }
                    QPushButton:hover { background-color: #CBD5E1; }
                """)
                ok = input_dialog.exec()
                phone = input_dialog.textValue()
                
                if ok and phone.strip():
                    phone_str = phone.strip()
                    found_cust = next((c for c in customers if c.get("phone") == phone_str), None)
                    if found_cust:
                        found_cust["points"] += earned_points
                        final_customer_name = found_cust["name"]
                    else:
                        customers.append({
                            "name": cust_input,
                            "phone": phone_str,
                            "email": "",
                            "points": earned_points
                        })
            
            save_json(get_path("data/customers.json"), customers)
            if self.parent() and hasattr(self.parent(), 'load_customers'):
                self.parent().load_customers()

            orders = load_json(get_path("data/orders.json"))
            order_id = f"ORD{len(orders)+1:03d}"
            today_date = datetime.date.today().strftime("%Y-%m-%d")
            
            orders.append({
                "id": order_id,
                "customer": final_customer_name,
                "items": self.cart,
                "total": int(self.total),
                "profit": int(self.profit),
                "date": today_date,
                "method": dialog.method
            })
            save_json(get_path("data/orders.json"), orders)
            
            for item in self.cart:
                for p in self.products:
                    if p["name"] == item["name"]: p["qty"] -= item["qty"]
            save_json(get_path("data/products.json"), self.products)

            if self.parent() and hasattr(self.parent(), 'load_reports'):
                self.parent().load_reports()

            # Tách riêng khung thông báo thành công và ép màu cho nút bấm
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Thành công")
            msg_box.setText("Đã thanh toán thành công!")
            msg_box.setStyleSheet("""
                QMessageBox { background-color: white; }
                QLabel { color: black; font-size: 13px; }
                QPushButton { color: black; background-color: #E2E8F0; padding: 6px 15px; border: 1px solid #94A3B8; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #CBD5E1; }
            """)
            msg_box.exec()
            
            self.cart.clear()
            self.update_cart_table()
            self.line_qty.clear()
            self.line_customer.clear()
            self.btn_pay.setEnabled(False)
            self.lbl_total.setText("...")


class PayMethod(QDialog):
    def __init__(self, parent, total_amount):
        super().__init__(parent)
        loadUi(get_path("pay_method.ui"), self)
        
        self.total_amount = total_amount 
        self.method = ""
        self.btn_back.clicked.connect(self.reject)
        self.pay_qr.clicked.connect(self.open_qr)
        self.pay_cash.clicked.connect(self.pay_by_cash)

        for lbl in self.findChildren(QLabel):
            text = lbl.text().lower()
            if "phương thức" in text:
                lbl.setStyleSheet("font-size: 10pt; font-weight: bold; color: black;")
            elif "trong 2" in text or "hình thức" in text:
                lbl.setStyleSheet("font-size: 7pt; color: #555555;")

        if hasattr(self, 'lbl_amount'):
            self.lbl_amount.setText(f"{int(self.total_amount):,} đ")
            self.lbl_amount.setStyleSheet("color: #2563EB; font-weight: bold; font-size: 16pt;")

    def pay_by_cash(self):
        self.method = "Tiền mặt"
        self.accept()

    def open_qr(self):
        self.method = "QR Code"
        dialog = PayQR(self, self.total_amount)
        if dialog.exec():
            self.accept()


class PayQR(QDialog):
    def __init__(self, parent, total_amount):
        super().__init__(parent)
        loadUi(get_path("qr_pay.ui"), self)
        self.pay_cancel.clicked.connect(self.reject)
        self.pay_conf.clicked.connect(self.accept)
        
        qr_data = f"Thanh toan don hang: {int(total_amount)} VND"
        qr = qrcode.make(qr_data)
        qr_path = get_path("temp_qr.png")
        qr.save(qr_path)
        
        if os.path.exists(qr_path):
            # Tự động tạo một label nhét vừa vặn vào trong khung frame_qr
            self.lbl_qr = QLabel(self.frame_qr)
            self.lbl_qr.resize(self.frame_qr.width(), self.frame_qr.height())
            self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_qr.setPixmap(QPixmap(qr_path).scaled(self.frame_qr.width() - 10, self.frame_qr.height() - 10, Qt.AspectRatioMode.KeepAspectRatio))
            self.lbl_qr.show()
