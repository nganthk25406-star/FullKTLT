import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore, QtWidgets
from ext_giaodien import Login, Register, Main
# os.environ["QT_FONT_DPI"] = "96"

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()

login = Login(widget)
reg = Register(widget)
main = Main(widget)

widget.addWidget(login)
widget.addWidget(reg)
widget.addWidget(main)

# widget.setCurrentIndex(2)

# def center_widget(w, width, height):
#     w.setFixedWidth(width)
#     w.setFixedHeight(height)
#
#     screen = QApplication.primaryScreen().availableGeometry()
#     screen_width = screen.width()
#     screen_height = screen.height()
#
#     # Tính toán tọa độ x, y để nằm giữa
#     x = (screen_width - width) // 2
#     y = (screen_height - height) // 2
#
#     w.setGeometry(x, y, width, height)
#
# center_widget(widget, 480, 500)

widget.show()
sys.exit(app.exec())