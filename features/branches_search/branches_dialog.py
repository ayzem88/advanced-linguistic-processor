"""
نافذة البحث بالجذع - واجهة البحث عن الكلمات التي تحتوي على جذع معين
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QTextEdit, QGroupBox, QRadioButton,
    QButtonGroup, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .branches_searcher import BranchesSearcher


class BranchesSearchDialog(QDialog):
    """نافذة البحث بالجذع"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.parent = parent
        
        self.setWindowTitle("البحث بالجذع")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(500, 300)
        
        # تطبيق تصميم المعالج اللغوي
        self.apply_linguistic_processor_theme()
        
        self.init_ui()
    
    def apply_linguistic_processor_theme(self):
        """تطبيق تصميم المعالج اللغوي"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #2196F3;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #f8f9ff;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: #333;
            }
            QRadioButton {
                font-size: 14px;
                color: #333;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::unchecked {
                border: 2px solid #ddd;
                border-radius: 9px;
                background-color: white;
            }
            QRadioButton::indicator::checked {
                border: 2px solid #2196F3;
                border-radius: 9px;
                background-color: #2196F3;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)
    
    def init_ui(self):
        """تهيئة الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # إدخال البحث
        self.create_search_input(layout)
        
        # أزرار التحكم
        self.create_control_buttons(layout)
    
    
    def create_search_input(self, parent_layout):
        """إنشاء إدخال البحث"""
        input_group = QGroupBox("إدخال البحث")
        input_layout = QVBoxLayout(input_group)
        
        # حقل إدخال الجذع
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("الجذع:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل الجذع")
        self.search_input.returnPressed.connect(self.search_branches)
        input_row.addWidget(self.search_input)
        
        input_layout.addLayout(input_row)
        
        # خيارات البحث المتقدمة
        self.create_search_options(input_layout)
        
        parent_layout.addWidget(input_group)
    
    def create_search_options(self, parent_layout):
        """إنشاء خيارات البحث المتقدمة"""
        options_group = QGroupBox("خيارات البحث")
        options_layout = QVBoxLayout(options_group)
        
        # خيار البحث في النص الحالي أو جميع الملفات
        search_scope_layout = QHBoxLayout()
        search_scope_layout.addWidget(QLabel("نطاق البحث:"))
        
        self.search_scope_group = QButtonGroup()
        self.current_text_radio = QRadioButton("النص الحالي فقط")
        self.current_text_radio.setChecked(True)
        self.all_files_radio = QRadioButton("جميع الملفات المحملة")
        
        self.search_scope_group.addButton(self.current_text_radio, 0)
        self.search_scope_group.addButton(self.all_files_radio, 1)
        
        search_scope_layout.addWidget(self.current_text_radio)
        search_scope_layout.addWidget(self.all_files_radio)
        search_scope_layout.addStretch()
        
        options_layout.addLayout(search_scope_layout)
        
        parent_layout.addWidget(options_group)
    
    def create_control_buttons(self, parent_layout):
        """إنشاء أزرار التحكم"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # زر البحث
        self.search_btn = QPushButton("🔍 بحث")
        self.search_btn.clicked.connect(self.search_branches)
        buttons_layout.addWidget(self.search_btn)
        
        # زر مسح
        clear_btn = QPushButton("🗑️ مسح")
        clear_btn.clicked.connect(self.clear_results)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        # زر إغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    
    def search_branches(self):
        """البحث عن الفروع"""
        search_input = self.search_input.text().strip()
        
        if not search_input:
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال جذع للبحث")
            return
        
        try:
            # إنشاء باحث الفروع
            searcher = BranchesSearcher()
            
            # تحليل إدخال البحث
            root_letters, excluded_letters = searcher.parse_search_input(search_input)
            
            if not root_letters:
                QMessageBox.warning(self, "خطأ", "الرجاء إدخال جذع صحيح")
                return
            
            # تحديد نطاق البحث
            if self.current_text_radio.isChecked():
                # البحث في النص الحالي فقط
                if not self.text.strip():
                    QMessageBox.warning(self, "تحذير", "لا يوجد نص للبحث فيه")
                    return
                
                branches = searcher.search_branches_in_text(self.text, root_letters, excluded_letters)
                source_info = "النص الحالي"
                formatted_results = searcher.format_branches_results(branches, source_info)
                
            else:
                # البحث في جميع الملفات المحملة
                all_texts, source_info = self.get_all_loaded_texts_with_sources()
                if not all_texts:
                    QMessageBox.warning(self, "تحذير", "لا توجد ملفات محملة للبحث فيها")
                    return
                
                # البحث في جميع النصوص
                branches = searcher.search_branches_in_text(all_texts, root_letters, excluded_letters)
                formatted_results = searcher.format_branches_results(branches, source_info)
            
            # عرض النتائج في المربع الرئيسي دائماً
            if hasattr(self.parent, 'results_area'):
                self.parent.results_area.setPlainText(formatted_results)
                self.parent.status_bar.showMessage(f"تم عرض نتائج البحث بالجذع '{''.join(root_letters)}'")
            else:
                QMessageBox.information(self, "النتائج", formatted_results)
            
            # رسالة النجاح
            if branches:
                QMessageBox.information(
                    self, 
                    "نجح البحث", 
                    f"تم العثور على {len(branches)} كلمة تحتوي على الجذع '{''.join(root_letters)}'"
                )
            else:
                QMessageBox.information(
                    self, 
                    "لا توجد نتائج", 
                    f"لم يتم العثور على أي كلمة تحتوي على الجذع '{''.join(root_letters)}'"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء البحث:\n{str(e)}")
    
    def get_all_loaded_texts(self):
        """الحصول على جميع النصوص المحملة"""
        all_texts = []
        
        # إضافة النص الحالي
        if self.text.strip():
            all_texts.append(self.text)
        
        # إضافة النص المحلل
        if hasattr(self.parent, 'analyzer') and self.parent.analyzer.text:
            all_texts.append(self.parent.analyzer.text)
        
        # إضافة نصوص المجموعات المحملة
        if hasattr(self.parent, 'corpus_manager'):
            for corpus_name in self.parent.corpus_manager.list_corpora():
                corpus_text = self.parent.corpus_manager.get_corpus_text(corpus_name)
                if corpus_text.strip():
                    all_texts.append(corpus_text)
        
        # دمج جميع النصوص
        return "\n\n".join(all_texts)
    
    def get_all_loaded_texts_with_sources(self):
        """الحصول على جميع النصوص المحملة مع معلومات المصدر"""
        all_texts = []
        sources = []
        
        # إضافة النص الحالي
        if self.text.strip():
            all_texts.append(self.text)
            sources.append("النص الحالي")
        
        # إضافة النص المحلل
        if hasattr(self.parent, 'analyzer') and self.parent.analyzer.text:
            all_texts.append(self.parent.analyzer.text)
            sources.append("النص المحلل")
        
        # إضافة نصوص المجموعات المحملة
        if hasattr(self.parent, 'corpus_manager'):
            for corpus_name in self.parent.corpus_manager.list_corpora():
                corpus_text = self.parent.corpus_manager.get_corpus_text(corpus_name)
                if corpus_text.strip():
                    all_texts.append(corpus_text)
                    sources.append(f"مجموعة: {corpus_name}")
        
        # دمج جميع النصوص
        combined_text = "\n\n".join(all_texts)
        source_info = "، ".join(sources) if sources else "غير محدد"
        
        return combined_text, source_info
    
    def clear_results(self):
        """مسح النتائج"""
        self.search_input.clear()
        # مسح مربع النتائج الرئيسي
        if hasattr(self.parent, 'results_area'):
            self.parent.results_area.clear()
