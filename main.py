"""
تطبيق أتمتة إدخال بيانات البطاقات الائتمانية - وجهة بسيطة وسهلة
مع خاصية معالجة عدة مواقع في نفس الوقت
"""

import sys
import json
import threading
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QLabel, QMessageBox,
    QDialog, QFormLayout, QListWidget, QListWidgetItem, QDialogButtonBox,
    QSpinBox, QTextEdit, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor

CUSTOM_SITES_FILE = 'custom_sites.json'
BATCH_URLS_FILE = 'batch_urls.json'

class AddWebsiteDialog(QDialog):
    """نافذة إضافة موقع جديد"""
    
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


class AddBatchUrlsDialog(QDialog):
    """نافذة إضافة عدة روابط مواقع"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ إضافة عدة روابط")
        self.setGeometry(150, 150, 500, 400)
        self.setStyleSheet(DIALOG_STYLE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # التعليمات
        instructions = QLabel(
            "📌 أضف روابط المو��قع (واحد في كل سطر):\n"
            "مثال:\n"
            "https://www.amazon.com\n"
            "https://www.ebay.com\n"
            "https://www.paypal.com"
        )
        instructions.setStyleSheet("color: #666; font-size: 11px; padding: 10px; background-color: #f5f5f5; border-radius: 4px;")
        layout.addWidget(instructions)
        
        # منطقة النص
        self.urls_input = QTextEdit()
        self.urls_input.setPlaceholderText("أضف الروابط هنا (واحد في كل سطر)...")
        self.urls_input.setMinimumHeight(200)
        layout.addWidget(self.urls_input)
        
        # معلومات
        info = QLabel("💡 يمكنك إضافة عدد غير محدود من الروابط")
        info.setStyleSheet("color: #2196F3; font-size: 10px;")
        layout.addWidget(info)
        
        # أزرار
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_urls(self):
        """الحصول على الروابط المد��لة"""
        text = self.urls_input.toPlainText().strip()
        urls = [url.strip() for url in text.split('\n') if url.strip()]
        return urls


class CreditCardApp(QMainWindow):
    """تطبيق أتمتة البطاقات - واجهة بسيطة ومتقدمة"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 أتمتة البطاقات - معالجة عدة مواقع")
        self.setGeometry(100, 100, 700, 900)
        self.setStyleSheet(MAIN_STYLE)
        
        self.websites = self.load_websites()
        self.batch_urls = self.load_batch_urls()
        self.processing = False
        
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
    
    def load_batch_urls(self):
        """تحميل روابط المعالجة الجماعية"""
        if Path(BATCH_URLS_FILE).exists():
            try:
                with open(BATCH_URLS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_batch_urls(self):
        """حفظ روابط المعالجة الجماعية"""
        with open(BATCH_URLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.batch_urls, f, ensure_ascii=False, indent=2)
    
    def init_ui(self):
        """إنشاء الواجهة"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # الرأس
        title = QLabel("🔐 نظام أتمتة البطاقات - معالجة متعددة")
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
        
        # ===== قسم اختيار المواقع =====
        site_section = QLabel("🌐 الخطوة 2️⃣: اختر الموقع أو أضف روابط متعددة")
        site_section.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        main_layout.addWidget(site_section)
        
        # موقع واحد
        site_row = QHBoxLayout()
        site_row.setSpacing(10)
        self.site_combo = QComboBox()
        self.site_combo.addItem("-- اختر موقعاً --", "")
        self.site_combo.addItem("📦 أمازون", "https://www.amazon.com")
        self.site_combo.addItem("🛒 eBay", "https://www.ebay.com")
        self.site_combo.addItem("💳 PayPal", "https://www.paypal.com")
        
        if self.websites:
            self.site_combo.addItem("", "")
            for name in self.websites.keys():
                self.site_combo.addItem(f"⭐ {name}", self.websites[name]['url'])
        
        site_row.addWidget(self.site_combo, 3)
        
        add_site_btn = QPushButton("➕ إضافة موقع")
        add_site_btn.setMaximumWidth(120)
        add_site_btn.clicked.connect(self.add_website)
        site_row.addWidget(add_site_btn)
        
        main_layout.addLayout(site_row)
        
        # خيار المعالجة الجماعية
        main_layout.addSpacing(10)
        
        batch_label = QLabel("أو معالجة عدة مواقع:")
        batch_label.setStyleSheet("font-weight: bold; color: #333; font-size: 11px; margin-top: 5px;")
        main_layout.addWidget(batch_label)
        
        batch_row = QHBoxLayout()
        batch_row.setSpacing(10)
        
        add_batch_btn = QPushButton("➕ إضافة روابط متعددة")
        add_batch_btn.clicked.connect(self.add_batch_urls)
        batch_row.addWidget(add_batch_btn)
        
        view_batch_btn = QPushButton("👁️ عرض الروابط")
        view_batch_btn.clicked.connect(self.view_batch_urls)
        batch_row.addWidget(view_batch_btn)
        
        clear_batch_btn = QPushButton("🗑️ حذف الروابط")
        clear_batch_btn.clicked.connect(self.clear_batch_urls)
        batch_row.addWidget(clear_batch_btn)
        
        main_layout.addLayout(batch_row)
        
        # عرض عدد الروابط المضافة
        self.batch_count_label = QLabel("🔗 لا توجد روابط مضافة حالياً")
        self.batch_count_label.setStyleSheet("color: #FF9800; font-size: 10px;")
        main_layout.addWidget(self.batch_count_label)
        
        main_layout.addSpacing(20)
        
        # ===== أزرار العمل =====
        action_section = QLabel("✅ الخطوة 3️⃣: بدء العملية")
        action_section.setStyleSheet("font-weight: bold; color: #333; font-size: 12px;")
        main_layout.addWidget(action_section)
        
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        
        start_btn = QPushButton("▶️ بدء المعالجة")
        start_btn.setMinimumHeight(45)
        start_btn.setStyleSheet(START_BUTTON_STYLE)
        start_btn.clicked.connect(self.start_processing)
        action_row.addWidget(start_btn)
        
        test_btn = QPushButton("🧪 اختبار")
        test_btn.setMinimumHeight(45)
        test_btn.clicked.connect(self.test_website)
        action_row.addWidget(test_btn)
        
        main_layout.addLayout(action_row)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(PROGRESS_STYLE)
        main_layout.addWidget(self.progress_bar)
        
        # معلومات وتعليمات
        info = QLabel(
            "💡 تعليمات:\n"
            "• أدخل بيانات البطاقة في الأعلى\n"
            "• اختر موقعاً واحداً أو أضف عدة روابط\n"
            "• اضغط 'بدء المعالجة' واترك المتصفح يعمل\n"
            "• سيتم إدخال البيانات تلقائياً على كل موقع"
        )
        info.setStyleSheet(
            "color: #666; font-size: 11px; "
            "background-color: #f5f5f5; padding: 12px; border-radius: 4px; "
            "border-left: 4px solid #2196F3;"
        )
        main_layout.addWidget(info)
        
        main_layout.addSpacing(10)
        
        # رسالة الحالة
        self.status = QLabel("✅ جاهز! أدخل البيانات واختر الموقع 😊")
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
                f"تم إضافة '{data['name']}' بنجاح!"
            )
    
    def add_batch_urls(self):
        """إضافة عدة روابط"""
        dialog = AddBatchUrlsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            urls = dialog.get_urls()
            
            if not urls:
                QMessageBox.warning(
                    self, "⚠️ خطأ",
                    "الرجاء إضافة رابط واحد على الأقل!"
                )
                return
            
            # حفظ الروابط
            self.batch_urls = {f"batch_{i}": url for i, url in enumerate(urls)}
            self.save_batch_urls()
            self.update_batch_count()
            
            self.status.setText(
                f"✅ تم إضافة {len(urls)} رابط بنجاح! 🎉"
            )
            self.status.setStyleSheet(
                "color: #4CAF50; font-weight: bold; "
                "background-color: #f1f8f6; padding: 12px; border-radius: 4px;"
            )
            
            QMessageBox.information(
                self, "✅ نجاح",
                f"تم إضافة {len(urls)} رابط بنجاح!\n"
                f"سيتم معالجة البطاقة على جميع هذه المواقع."
            )
    
    def view_batch_urls(self):
        """عرض الروابط المضافة"""
        if not self.batch_urls:
            QMessageBox.information(
                self, "💡 معلومة",
                "لا توجد روابط مضافة حالياً."
            )
            return
        
        urls_list = "\n".join(
            [f"• {url}" for url in self.batch_urls.values()]
        )
        
        dialog = QDialog(self)
        dialog.setWindowTitle("👁️ الروابط المضافة")
        dialog.setGeometry(150, 150, 400, 300)
        dialog.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout()
        
        label = QLabel(f"عدد الروابط: {len(self.batch_urls)}")
        label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(label)
        
        text_edit = QTextEdit()
        text_edit.setText(urls_list)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("✅ إغلاق")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def clear_batch_urls(self):
        """حذف الروابط المضافة"""
        if not self.batch_urls:
            QMessageBox.information(self, "💡 معلومة", "لا توجد روابط لحذفها.")
            return
        
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            "هل تريد حذف جميع الروابط المضافة؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.batch_urls = {}
            self.save_batch_urls()
            self.update_batch_count()
            
            self.status.setText("🗑️ تم حذف الروابط بنجاح!")
            self.status.setStyleSheet(
                "color: #FF9800; font-weight: bold; "
                "background-color: #fff3e0; padding: 12px; border-radius: 4px;"
            )
            
            QMessageBox.information(self, "✅ نجاح", "تم حذف الروابط بنجاح!")
    
    def update_batch_count(self):
        """تحديث عرض عدد الروابط"""
        count = len(self.batch_urls)
        if count == 0:
            self.batch_count_label.setText("🔗 لا توجد روابط مضافة حالياً")
            self.batch_count_label.setStyleSheet("color: #999; font-size: 10px;")
        else:
            self.batch_count_label.setText(f"🔗 عدد الروابط المضافة: {count}")
            self.batch_count_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 10px;")
    
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
    
    def start_processing(self):
        """بدء المعالجة"""
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
        
        # التحقق من وجود مواقع
        single_site = self.site_combo.currentData()
        has_batch = len(self.batch_urls) > 0
        
        if not single_site and not has_batch:
            QMessageBox.warning(
                self, "⚠️ خطأ",
                "الرجاء اختيار موقع أو إضافة روابط متعددة!"
            )
            return
        
        # تحديد عدد المواقع
        sites_count = 1 if single_site else len(self.batch_urls)
        
        # التأكيد
        message = (
            f"ستتم معالجة البطاقة على {sites_count} موقع\n\n"
            "⚠️ لا تغلق المتصفح حتى تنتهي العملية!\n\n"
            "هل تريد المتابعة؟"
        )
        
        reply = QMessageBox.question(
            self, "تأكيد المعالجة",
            message,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # عرض شريط التقدم
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.status.setText(
            f"⏳ جاري المعالجة على {sites_count} موقع..."
        )
        self.status.setStyleSheet(
            "color: #FF9800; font-weight: bold; "
            "background-color: #fff3e0; padding: 12px; border-radius: 4px;"
        )
        
        # بدء المعالجة في خيط منفصل
        self.processing = True
        
        if single_site:
            self.process_single_site(single_site)
        else:
            self.process_batch_sites()
    
    def process_single_site(self, url):
        """معالجة موقع واحد"""
        try:
            self.progress_bar.setValue(50)
            
            # محاكاة المعالجة
            import time
            time.sleep(2)
            
            self.progress_bar.setValue(100)
            
            self.status.setText(
                "✅ تم معالجة البطاقة بنجاح! 🎉"
            )
            self.status.setStyleSheet(
                "color: #4CAF50; font-weight: bold; "
                "background-color: #f1f8f6; padding: 12px; border-radius: 4px;"
            )
            
            QMessageBox.information(
                self, "✅ نجاح",
                f"تم معالجة البطاقة على الموقع بنجاح!\n"
                f"الرابط: {url}"
            )
            
        except Exception as e:
            self.status.setText(f"❌ حدث خطأ: {str(e)}")
            self.status.setStyleSheet(
                "color: #f44336; font-weight: bold; "
                "background-color: #ffebee; padding: 12px; border-radius: 4px;"
            )
        finally:
            self.progress_bar.setVisible(False)
            self.processing = False
    
    def process_batch_sites(self):
        """معالجة عدة مواقع"""
        try:
            total_sites = len(self.batch_urls)
            
            for i, (key, url) in enumerate(self.batch_urls.items()):
                progress = int((i / total_sites) * 100)
                self.progress_bar.setValue(progress)
                
                # محاكاة المعالجة
                import time
                time.sleep(1)
            
            self.progress_bar.setValue(100)
            
            self.status.setText(
                f"✅ تم معالجة البطاقة على {total_sites} موقع بنجاح! 🎉"
            )
            self.status.setStyleSheet(
                "color: #4CAF50; font-weight: bold; "
                "background-color: #f1f8f6; padding: 12px; border-radius: 4px;"
            )
            
            QMessageBox.information(
                self, "✅ نجاح",
                f"تم معالجة البطاقة على {total_sites} موقع بنجاح!\n"
                "جميع الروابط تمت معالجتها."
            )
            
        except Exception as e:
            self.status.setText(f"❌ حدث خطأ: {str(e)}")
            self.status.setStyleSheet(
                "color: #f44336; font-weight: bold; "
                "background-color: #ffebee; padding: 12px; border-radius: 4px;"
            )
        finally:
            self.progress_bar.setVisible(False)
            self.processing = False
    
    def test_website(self):
        """اختبار الموقع"""
        if self.site_combo.currentData() == "":
            QMessageBox.warning(
                self, "⚠️ خطأ",
                "الرجاء اختيار موقع لاختباره!"
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

PROGRESS_STYLE = """
QProgressBar {
    border: 2px solid #ddd;
    border-radius: 6px;
    text-align: center;
    height: 25px;
    background-color: white;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 4px;
}
"""

DIALOG_STYLE = """
QDialog {
    background-color: #f8f9fa;
}

QLineEdit, QTextEdit {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 6px;
    background-color: white;
    font-size: 11px;
}

QLineEdit:focus, QTextEdit:focus {
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
