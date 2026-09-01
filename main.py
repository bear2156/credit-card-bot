"""
تطبيق أتمتة إدخال بيانات البطاقات الائتمانية - واجهة بسيطة وسهلة الفهم
"""

import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QLabel, QMessageBox,
    QDialog, QFormLayout, QListWidget, QListWidgetItem, QDialogButtonBox,
    QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

CUSTOM_SITES_FILE = 'custom_sites.json'

class AddWebsiteDialog(QDialog):
    """نافذة بسيطة لإضافة موقع جديد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة موقع جديد")
        self.setGeometry(150, 150, 400, 300)
        self.setStyleSheet(DIALOG_STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(12)
        
        # اسم الموقع
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: أمازون أو eBay")
        layout.addRow(self.create_label("📝 اسم الموقع:"), self.name_input)
        
        # رابط الموقع
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("مثال: https://www.amazon.com")
        layout.addRow(self.create_label("🔗 رابط الموقع:"), self.url_input)
        
        # معلومات مساعدة
        info_label = QLabel(
            "⚠️ اترك الحقول التالية فارغة إذا لم تكن متأكداً\nسيتم ملء البيانات يدويّاً"
        )
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addRow(info_label)
        
        # Selectors (اختياري)
        self.card_selector = QLineEdit()
        self.card_selector.setPlaceholderText("مثال: #card-input")
        layout.addRow(self.create_label("💳 حقل رقم البطاقة:"), self.card_selector)
        
        self.name_selector = QLineEdit()
        self.name_selector.setPlaceholderText("مثال: #name-input")
        layout.addRow(self.create_label("👤 حقل الاسم:"), self.name_selector)
        
        self.month_selector = QLineEdit()
        self.month_selector.setPlaceholderText("مثال: #month")
        layout.addRow(self.create_label("📅 حقل الشهر:"), self.month_selector)
        
        self.year_selector = QLineEdit()
        self.year_selector.setPlaceholderText("مثال: #year")
        layout.addRow(self.create_label("📅 حقل السنة:"), self.year_selector)
        
        self.cvv_selector = QLineEdit()
        self.cvv_selector.setPlaceholderText("مثال: #cvv")
        layout.addRow(self.create_label("🔐 حقل CVV:"), self.cvv_selector)
        
        self.submit_selector = QLineEdit()
        self.submit_selector.setPlaceholderText("مثال: #submit-btn")
        layout.addRow(self.create_label("✅ زر الإرسال:"), self.submit_selector)
        
        # أزرار
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; color: #333;")
        return label
    
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip(),
            'selectors': {
                'card_number': self.card_selector.text().strip(),
                'cardholder': self.name_selector.text().strip(),
                'month': self.month_selector.text().strip(),
                'year': self.year_selector.text().strip(),
                'cvv': self.cvv_selector.text().strip(),
                'submit': self.submit_selector.text().strip()
            }
        }


class CreditCardApp(QMainWindow):
    """تطبيق بسيط وسهل الفهم للمبتدئين"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 أتمتة إدخال البطاقات الائتمانية")
        self.setGeometry(100, 100, 600, 750)
        self.setStyleSheet(MAIN_STYLE)
        
        self.websites = self.load_websites()
        self.init_ui()
    
    def load_websites(self):
        """تحميل المواقع المحفوظة"""
        if Path(CUSTOM_SITES_FILE).exists():
            try:
                with open(CUSTOM_SITES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_websites(self):
        """حفظ المواقع"""
        with open(CUSTOM_SITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.websites, f, ensure_ascii=False, indent=2)
    
    def init_ui(self):
        """إنشاء الواجهة"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # الرأس
        title = QLabel("🔐 نظام أتمتة البطاقات الائتمانية")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2196F3; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # ===== قسم بيانات البطاقة =====
        card_section = QLabel("📌 الخطوة 1️⃣: أدخل بيانات البطاقة")
        card_section.setStyleSheet("font-weight: bold; color: #333; font-size: 12px; margin-top: 10px;")
        main_layout.addWidget(card_section)
        
        # رقم البطاقة
        card_row = QHBoxLayout()
        card_row.setSpacing(10)
        card_row.addWidget(QLabel("💳 رقم البطاقة:"), 1)
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("مثال: 4532123456789012 (16 رقم)")
        card_row.addWidget(self.card_input, 3)
        main_layout.addLayout(card_row)
        
        # اسم صاحب البطاقة
        name_row = QHBoxLayout()
        name_row.setSpacing(10)
        name_row.addWidget(QLabel("👤 الاسم:"), 1)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: Ahmed Ali")
        name_row.addWidget(self.name_input, 3)
        main_layout.addLayout(name_row)
        
        # الشهر والسنة
        date_row = QHBoxLayout()
        date_row.setSpacing(10)
        date_row.addWidget(QLabel("📅 الشهر:"), 1)
        self.month_input = QSpinBox()
        self.month_input.setRange(1, 12)
        self.month_input.setValue(1)
        date_row.addWidget(self.month_input, 1)
        date_row.addWidget(QLabel("السنة:"), 1)
        self.year_input = QSpinBox()
        self.year_input.setRange(2024, 2035)
        self.year_input.setValue(2024)
        date_row.addWidget(self.year_input, 1)
        main_layout.addLayout(date_row)
        
        # CVV
        cvv_row = QHBoxLayout()
        cvv_row.setSpacing(10)
        cvv_row.addWidget(QLabel("🔐 CVV:"), 1)
        self.cvv_input = QLineEdit()
        self.cvv_input.setPlaceholderText("مثال: 123 (3 أرقام خلف البطاقة)")
        self.cvv_input.setMaxLength(4)
        cvv_row.addWidget(self.cvv_input, 3)
        main_layout.addLayout(cvv_row)
        
        main_layout.addSpacing(15)
        
        # ===== قسم اختيار الموقع =====
        site_section = QLabel("🌐 الخطوة 2️⃣: اختر الموقع")
        site_section.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        main_layout.addWidget(site_section)
        
        site_row = QHBoxLayout()
        site_row.setSpacing(10)
        self.site_combo = QComboBox()
        self.site_combo.addItem("-- اختر موقعاً --", "")
        self.site_combo.addItem("📦 أمازون", "https://www.amazon.com")
        self.site_combo.addItem("🛒 eBay", "https://www.ebay.com")
        self.site_combo.addItem("💳 PayPal", "https://www.paypal.com")
        
        # إضافة المواقع المخصصة
        if self.websites:
            self.site_combo.addItem("", "")  # فاصل
            for name in self.websites.keys():
                self.site_combo.addItem(f"⭐ {name}", self.websites[name]['url'])
        
        site_row.addWidget(self.site_combo, 3)
        
        add_site_btn = QPushButton("➕ إضافة موقع")
        add_site_btn.setMaximumWidth(120)
        add_site_btn.clicked.connect(self.add_website)
        site_row.addWidget(add_site_btn)
        
        manage_btn = QPushButton("⚙️ إدارة")
        manage_btn.setMaximumWidth(80)
        manage_btn.clicked.connect(self.manage_websites)
        site_row.addWidget(manage_btn)
        
        main_layout.addLayout(site_row)
        
        main_layout.addSpacing(20)
        
        # ===== أزرار العمل =====
        action_section = QLabel("✅ الخطوة 3️⃣: بدء العملية")
        action_section.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        main_layout.addWidget(action_section)
        
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        
        start_btn = QPushButton("▶️ بدء الآن")
        start_btn.setMinimumHeight(45)
        start_btn.setStyleSheet(START_BUTTON_STYLE)
        start_btn.clicked.connect(self.start_automation)
        action_row.addWidget(start_btn)
        
        test_btn = QPushButton("🧪 اختبار")
        test_btn.setMinimumHeight(45)
        test_btn.clicked.connect(self.test_website)
        action_row.addWidget(test_btn)
        
        main_layout.addLayout(action_row)
        
        # معلومات وتعليمات
        info = QLabel(
            "ℹ️ تعليمات:\n"
            "• أدخل بيانات البطاقة في الأعلى\n"
            "• اختر الموقع من القائمة\n"
            "• اضغط 'بدء الآن' وانتظر\n"
            "• لا تغلق المتصفح حتى ينتهي"
        )
        info.setStyleSheet(
            "color: #666; font-size: 11px; "
            "background-color: #f5f5f5; padding: 12px; border-radius: 4px; "
            "border-left: 4px solid #2196F3;"
        )
        main_layout.addWidget(info)
        
        main_layout.addSpacing(10)
        
        # رسالة الحالة
        self.status = QLabel("✅ جاهز! أدخل البيانات وابدأ 😊")
        self.status.setStyleSheet(
            "color: #4CAF50; font-weight: bold; "
            "background-color: #f1f8f6; padding: 12px; border-radius: 4px;"
        )
        main_layout.addWidget(self.status)
        
        main_layout.addStretch()
        
        central.setLayout(main_layout)
    
    def add_website(self):
        """إضافة موقع جديد"""
        dialog = AddWebsiteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not data['name'] or not data['url']:
                QMessageBox.warning(
                    self, "⚠️ خطأ",
                    "الرجاء إدخال اسم الموقع والرابط!"
                )
                return
            
            self.websites[data['name']] = data
            self.save_websites()
            self.refresh_combo()
            
            self.status.setText(
                f"✅ تم إضافة '{data['name']}' بنجاح! 🎉"
            )
            self.status.setStyleSheet(
                "color: #4CAF50; font-weight: bold; "
                "background-color: #f1f8f6; padding: 12px; border-radius: 4px;"
            )
            
            QMessageBox.information(
                self, "✅ نجاح",
                f"تم إضافة '{data['name']}' بنجاح!\n"
                "يمكنك الآن اختياره من القائمة."
            )
    
    def manage_websites(self):
        """إدارة المواقع"""
        if not self.websites:
            QMessageBox.information(
                self, "ℹ️ معلومة",
                "لا توجد مواقع مخصصة حالياً!\n"
                "أنقر على '➕ إضافة موقع' لإضافة واحد."
            )
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("⚙️ إدارة المواقع")
        dialog.setGeometry(150, 150, 400, 400)
        dialog.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout()
        
        label = QLabel("🌐 المواقع المحفوظة:")
        label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(label)
        
        website_list = QListWidget()
        website_list.setStyleSheet(
            "QListWidget { background-color: white; border: 1px solid #ddd; border-radius: 4px; }\n"
            "QListWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }\n"
            "QListWidget::item:selected { background-color: #e3f2fd; color: #1976D2; }"
        )
        for name in self.websites.keys():
            item = QListWidgetItem(f"⭐ {name}")
            website_list.addItem(item)
        layout.addWidget(website_list)
        
        btn_row = QHBoxLayout()
        
        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; padding: 10px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #d32f2f; }"
        )
        delete_btn.clicked.connect(
            lambda: self.delete_website(
                website_list.currentItem(), dialog
            )
        )
        btn_row.addWidget(delete_btn)
        
        close_btn = QPushButton("✅ إغلاق")
        close_btn.clicked.connect(dialog.close)
        btn_row.addWidget(close_btn)
        
        layout.addLayout(btn_row)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def delete_website(self, item, dialog):
        """حذف موقع"""
        if not item:
            QMessageBox.warning(self, "⚠️ خطأ", "اختر موقعاً لحذفه!")
            return
        
        name = item.text().replace("⭐ ", "")
        
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف '{name}'؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.websites[name]
            self.save_websites()
            self.refresh_combo()
            dialog.close()
            
            self.status.setText(f"✅ تم حذف '{name}'!")
            QMessageBox.information(self, "✅ نجاح", f"تم حذف '{name}' بنجاح!")
    
    def refresh_combo(self):
        """تحديث قائمة المواقع"""
        current = self.site_combo.currentData()
        self.site_combo.clear()
        self.site_combo.addItem("-- اختر موقعاً --", "")
        self.site_combo.addItem("📦 أمازون", "https://www.amazon.com")
        self.site_combo.addItem("🛒 eBay", "https://www.ebay.com")
        self.site_combo.addItem("💳 PayPal", "https://www.paypal.com")
        
        if self.websites:
            self.site_combo.addItem("", "")
            for name in self.websites.keys():
                self.site_combo.addItem(
                    f"⭐ {name}",
                    self.websites[name]['url']
                )
        
        if current:
            index = self.site_combo.findData(current)
            if index >= 0:
                self.site_combo.setCurrentIndex(index)
    
    def start_automation(self):
        """بدء العملية"""
        # التحقق من البيانات
        if not self.card_input.text():
            QMessageBox.warning(
                self, "⚠️ خطأ",
                "الرجاء إدخال رقم البطاقة أولاً!"
            )
            return
        
        if not self.name_input.text():
            QMessageBox.warning(
                self, "⚠️ خطأ",
                "الرجاء إدخال الاسم أولاً!"
            )
            return
        
        if self.site_combo.currentData() == "":
            QMessageBox.warning(
                self, "⚠️ خطأ",
                "الرجاء اختيار موقعاً من القائمة!"
            )
            return
        
        # رسالة التأكيد
        QMessageBox.information(
            self, "🚀 بدء العملية",
            f"سيتم فتح المتصفح الآن\n"
            f"الموقع: {self.site_combo.currentText()}\n\n"
            f"⚠️ لا تغلق المتصفح حتى ينتهي!"
        )
        
        self.status.setText(
            "🔄 جاري تنفيذ العملية... يرجى الانتظار"
        )
        self.status.setStyleSheet(
            "color: #FF9800; font-weight: bold; "
            "background-color: #fff3e0; padding: 12px; border-radius: 4px;"
        )
    
    def test_website(self):
        """اختبار الموقع"""
        if self.site_combo.currentData() == "":
            QMessageBox.warning(
                self, "⚠️ خطأ",
                "الرجاء اختيار موقعاً من القائمة!"
            )
            return
        
        url = self.site_combo.currentData()
        QMessageBox.information(
            self, "🧪 اختبار",
            f"سيتم فتح الموقع:\n{url}\n\n"
            f"تحقق من وجود حقول البطاقة."
        )


# الأنماط (Styles)
MAIN_STYLE = """
QMainWindow {
    background-color: #f8f9fa;
}

QLineEdit, QSpinBox, QComboBox {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 6px;
    background-color: white;
    font-size: 12px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 2px solid #2196F3;
    background-color: #f0f8ff;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #1565C0;
}

QLabel {
    color: #333;
}
"""

START_BUTTON_STYLE = """
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 15px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}
"""

DIALOG_STYLE = """
QDialog {
    background-color: #f8f9fa;
}

QLineEdit {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 6px;
    background-color: white;
    font-size: 11px;
}

QLineEdit:focus {
    border: 2px solid #2196F3;
    background-color: #f0f8ff;
}

QLabel {
    color: #333;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #1976D2;
}
"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CreditCardApp()
    window.show()
    sys.exit(app.exec_())
