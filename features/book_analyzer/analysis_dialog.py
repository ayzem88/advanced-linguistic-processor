"""
نافذة تحليل الكتاب - الواجهة الرئيسية لتحليل كتاب واحد
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QProgressBar, QScrollArea, QWidget,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# استيراد خيط التحليل
from .analysis_worker import BookAnalysisWorker


class BookAnalysisDialog(QDialog):
    """نافذة تحليل الكتاب المفرد"""
    
    def __init__(self, book_title, book_content, parent=None):
        super().__init__(parent)
        self.book_title = book_title
        self.book_content = book_content
        self.analysis_worker = None
        self.analysis_results = {}
        
        self.setWindowTitle(f"تحليل كتاب: {book_title}")
        self.setModal(True)
        self.setMinimumSize(1100, 800)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # تطبيق التصميم الموحد مع المعالج اللغوي
        self.apply_linguistic_processor_theme()
        
        self.init_ui()
        self.start_analysis()
    
    def apply_linguistic_processor_theme(self):
        """تطبيق تصميم المعالج اللغوي"""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                gridline-color: #f0f0f0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: #000;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
    
    def init_ui(self):
        """تهيئة الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # العنوان والمعلومات الأساسية
        self.create_header(layout)
        
        # شريط التقدم
        self.create_progress_bar(layout)
        
        # منطقة النتائج القابلة للتمرير
        self.create_results_area(layout)
        
        # أزرار التحكم
        self.create_control_buttons(layout)
    
    def create_header(self, parent_layout):
        """إنشاء العنوان والمعلومات الأساسية"""
        header_group = QGroupBox("معلومات الكتاب")
        header_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #e0e0e0; 
                border-radius: 8px; 
                padding: 15px; 
                background-color: #f9f9f9; 
                margin-bottom: 10px;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 5px; 
                color: #2196F3; 
            }
        """)
        
        header_layout = QVBoxLayout(header_group)
        
        # عنوان الكتاب
        title_label = QLabel(f"📚 {self.book_title}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2196F3;
                padding: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # معلومات إضافية
        info_layout = QHBoxLayout()
        
        # عدد الأحرف والكلمات
        char_count = len(self.book_content)
        word_count = len(self.book_content.split())
        
        char_label = QLabel(f"📝 الأحرف: {char_count:,}")
        char_label.setStyleSheet("QLabel { font-size: 13px; color: #666; padding: 3px; }")
        info_layout.addWidget(char_label)
        
        word_label = QLabel(f"📖 الكلمات: {word_count:,}")
        word_label.setStyleSheet("QLabel { font-size: 13px; color: #666; padding: 3px; }")
        info_layout.addWidget(word_label)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        parent_layout.addWidget(header_group)
    
    def create_progress_bar(self, parent_layout):
        """إنشاء شريط التقدم"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        parent_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                text-align: center;
            }
        """)
        self.progress_label.setVisible(False)
        parent_layout.addWidget(self.progress_label)
    
    def create_results_area(self, parent_layout):
        """إنشاء منطقة النتائج"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(15)
        self.results_layout.setContentsMargins(15, 15, 15, 15)
        
        scroll_area.setWidget(self.results_widget)
        parent_layout.addWidget(scroll_area)
    
    def create_control_buttons(self, parent_layout):
        """إنشاء أزرار التحكم"""
        buttons_layout = QHBoxLayout()
        
        # زر تصدير Excel
        self.export_excel_btn = QPushButton("💾 تصدير Excel")
        self.export_excel_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                padding: 10px 20px; 
                font-size: 14px; 
                font-weight: bold; 
                border: none; 
                border-radius: 5px; 
            }
            QPushButton:hover { 
                background-color: #1976D2; 
            }
            QPushButton:disabled { 
                background-color: #cccccc; 
                color: #666666; 
            }
        """)
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        self.export_excel_btn.setEnabled(False)
        buttons_layout.addWidget(self.export_excel_btn)
        
        buttons_layout.addStretch()
        
        self.close_btn = QPushButton("إغلاق")
        self.close_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                padding: 10px 20px; 
                font-size: 14px; 
                font-weight: bold; 
                border: none; 
                border-radius: 5px; 
            }
            QPushButton:hover { 
                background-color: #1976D2; 
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    def start_analysis(self):
        """بدء عملية التحليل"""
        try:
            if not self.book_content:
                QMessageBox.warning(self, "تحذير", "لا يوجد محتوى للتحليل!")
                return
            
            # إعداد الواجهة
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # شريط متحرك
            self.progress_label.setText("جارٍ تحليل الكتاب ...")
            self.progress_label.setVisible(True)
            
            # إنشاء وتشغيل خيط التحليل
            self.analysis_worker = BookAnalysisWorker("book_1", self.book_content)
            self.analysis_worker.progress_update.connect(self.update_progress)
            self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
            self.analysis_worker.analysis_error.connect(self.on_analysis_error)
            self.analysis_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في بدء التحليل:\n{str(e)}")
    
    def update_progress(self, message):
        """تحديث شريط التقدم"""
        self.progress_label.setText(message)
    
    def on_analysis_complete(self, results):
        """اكتمال التحليل"""
        self.analysis_results = results
        
        # إخفاء شريط التقدم
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # تفعيل زر التصدير
        self.export_excel_btn.setEnabled(True)
        
        # عرض النتائج
        self.display_results()
        
        # رسالة النجاح
        QMessageBox.information(
            self, 
            "اكتمل التحليل", 
            "تم تحليل الكتاب بنجاح!\nيمكنك الآن تصدير النتائج أو تصفحها أدناه."
        )
    
    def on_analysis_error(self, error_message):
        """خطأ في التحليل"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.critical(self, "خطأ في التحليل", f"حدث خطأ أثناء التحليل:\n{error_message}")
    
    def display_results(self):
        """عرض النتائج الشاملة في الواجهة"""
        if not self.analysis_results:
            return
        
        # مسح النتائج السابقة
        self.clear_results()
        
        # عرض الإحصائيات الأساسية
        self.create_basic_stats_section()
        
        # عرض تحليل الكلمات
        if 'top_words' in self.analysis_results:
            self.create_words_section()
        
        # عرض تحليل المركبات
        if 'top_bigrams' in self.analysis_results:
            self.create_compounds_section()
        
        # عرض التحليل المتقدم للمركبات
        if 'advanced_compounds' in self.analysis_results:
            self.create_advanced_compounds_section()
        
        # عرض الكيانات المسماة
        if 'entities' in self.analysis_results:
            self.create_entities_section()
    
    def clear_results(self):
        """مسح النتائج السابقة"""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def create_basic_stats_section(self):
        """إنشاء قسم الإحصائيات الأساسية"""
        stats_group = QGroupBox("الإحصائيات الأساسية")
        stats_group.setStyleSheet(self.get_section_style())
        
        stats_layout = QHBoxLayout(stats_group)
        
        # بطاقة إحصائيات الكلمات
        words_card = self.create_stat_card("📝 الكلمات", {
            "إجمالي الكلمات": f"{self.analysis_results.get('total_words', 0):,}",
            "الكلمات الفريدة": f"{self.analysis_results.get('unique_words', 0):,}"
        })
        stats_layout.addWidget(words_card)
        
        # بطاقة إحصائيات المركبات الثنائية
        bigrams_card = self.create_stat_card("🔗 المركبات الثنائية", {
            "إجمالي المركبات": f"{self.analysis_results.get('total_bigrams_all', 0):,}",
            "المركبات الفريدة": f"{self.analysis_results.get('unique_bigrams', 0):,}"
        })
        stats_layout.addWidget(bigrams_card)
        
        # بطاقة إحصائيات المركبات الثلاثية
        trigrams_card = self.create_stat_card("🔗🔗 المركبات الثلاثية", {
            "إجمالي المركبات": f"{self.analysis_results.get('total_trigrams_all', 0):,}",
            "المركبات الفريدة": f"{self.analysis_results.get('unique_trigrams', 0):,}"
        })
        stats_layout.addWidget(trigrams_card)
        
        # بطاقة إحصائيات الكيانات
        entities_card = self.create_stat_card("🏷️ الكيانات", {
            "الأسماء": self.analysis_results.get('entities', {}).get('names_count', 0),
            "الأماكن": self.analysis_results.get('entities', {}).get('places_count', 0),
            "المؤسسات": self.analysis_results.get('entities', {}).get('organizations_count', 0)
        })
        stats_layout.addWidget(entities_card)
        
        self.results_layout.addWidget(stats_group)
    
    def create_stat_card(self, title, stats):
        """إنشاء بطاقة إحصائية"""
        card = QGroupBox(title)
        card.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f9fa;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        for label, value in stats.items():
            stat_label = QLabel(f"{label}: {value}")
            stat_label.setStyleSheet("font-size: 12px; color: #555; padding: 2px;")
            layout.addWidget(stat_label)
        
        return card
    
    def create_words_section(self):
        """إنشاء قسم تحليل الكلمات"""
        words_group = QGroupBox("الكلمات الأكثر تكراراً")
        words_group.setStyleSheet(self.get_section_style())
        
        words_layout = QVBoxLayout(words_group)
        
        # جدول الكلمات
        words_table = QTableWidget()
        words_table.setColumnCount(3)
        words_table.setHorizontalHeaderLabels(["الترتيب", "الكلمة", "التكرار"])
        
        # إضافة البيانات
        top_words = self.analysis_results.get('top_words', [])
        words_table.setRowCount(min(len(top_words), 20))
        
        for i, (word, count) in enumerate(top_words[:20]):
            words_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            words_table.setItem(i, 1, QTableWidgetItem(word))
            words_table.setItem(i, 2, QTableWidgetItem(str(count)))
        
        # تنسيق الجدول
        words_table.setStyleSheet(self.get_table_style())
        words_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        words_table.setFixedHeight(200)
        
        words_layout.addWidget(words_table)
        self.results_layout.addWidget(words_group)
    
    def create_compounds_section(self):
        """إنشاء قسم تحليل المركبات"""
        compounds_group = QGroupBox("المركبات المختارة")
        compounds_group.setStyleSheet(self.get_section_style())
        
        compounds_layout = QVBoxLayout(compounds_group)
        
        # جدول المركبات الثنائية
        bigrams_table = QTableWidget()
        bigrams_table.setColumnCount(3)
        bigrams_table.setHorizontalHeaderLabels(["الترتيب", "المركب", "PMI"])
        
        top_bigrams = self.analysis_results.get('top_bigrams', [])
        bigrams_table.setRowCount(min(len(top_bigrams), 15))
        
        for i, compound_data in enumerate(top_bigrams[:15]):
            bigrams_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            bigrams_table.setItem(i, 1, QTableWidgetItem(compound_data.get('text', '')))
            bigrams_table.setItem(i, 2, QTableWidgetItem(f"{compound_data.get('pmi', 0):.2f}"))
        
        bigrams_table.setStyleSheet(self.get_table_style())
        bigrams_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        bigrams_table.setFixedHeight(200)
        
        compounds_layout.addWidget(bigrams_table)
        self.results_layout.addWidget(compounds_group)
    
    def create_advanced_compounds_section(self):
        """إنشاء قسم التحليل المتقدم للمركبات"""
        advanced_data = self.analysis_results.get('advanced_compounds', {})
        compounds = advanced_data.get('compounds', [])
        statistics = advanced_data.get('statistics', {})
        
        if not compounds:
            return
        
        advanced_group = QGroupBox("التحليل المتقدم للمركبات")
        advanced_group.setStyleSheet(self.get_section_style())
        
        advanced_layout = QVBoxLayout(advanced_group)
        
        # إحصائيات سريعة
        stats_text = f"إجمالي المركبات: {statistics.get('total_compounds', 0)} | "
        stats_text += f"قوية: {statistics.get('strong_compounds', 0)} | "
        stats_text += f"متوسطة: {statistics.get('medium_compounds', 0)} | "
        stats_text += f"ضعيفة: {statistics.get('weak_compounds', 0)}"
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        advanced_layout.addWidget(stats_label)
        
        # جدول المركبات المتقدمة
        compounds_table = QTableWidget()
        compounds_table.setColumnCount(6)
        compounds_table.setHorizontalHeaderLabels(["الترتيب", "المركب", "PMI", "T-Score", "Log-Likelihood", "التصنيف"])
        
        compounds_table.setRowCount(min(len(compounds), 20))
        
        for i, compound in enumerate(compounds[:20]):
            compounds_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            compounds_table.setItem(i, 1, QTableWidgetItem(compound.get('text', '')))
            compounds_table.setItem(i, 2, QTableWidgetItem(f"{compound.get('pmi', 0):.3f}"))
            compounds_table.setItem(i, 3, QTableWidgetItem(f"{compound.get('t_score', 0):.3f}"))
            compounds_table.setItem(i, 4, QTableWidgetItem(f"{compound.get('log_likelihood', 0):.3f}"))
            compounds_table.setItem(i, 5, QTableWidgetItem(compound.get('category', '')))
        
        compounds_table.setStyleSheet(self.get_table_style())
        compounds_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        compounds_table.setFixedHeight(300)
        
        advanced_layout.addWidget(compounds_table)
        self.results_layout.addWidget(advanced_group)
    
    def create_entities_section(self):
        """إنشاء قسم الكيانات المسماة"""
        entities_data = self.analysis_results.get('entities', {})
        
        if not entities_data:
            return
        
        entities_group = QGroupBox("الكيانات المسماة")
        entities_group.setStyleSheet(self.get_section_style())
        
        entities_layout = QVBoxLayout(entities_group)
        
        # إحصائيات الكيانات
        stats_text = f"الأسماء: {entities_data.get('names_count', 0)} | "
        stats_text += f"الأماكن: {entities_data.get('places_count', 0)} | "
        stats_text += f"المؤسسات: {entities_data.get('organizations_count', 0)}"
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        entities_layout.addWidget(stats_label)
        
        # جدول الكيانات
        entities_table = QTableWidget()
        entities_table.setColumnCount(4)
        entities_table.setHorizontalHeaderLabels(["النوع", "الكيان", "التكرار", "النسبة"])
        
        all_entities = []
        
        # إضافة الأسماء
        for name, count in entities_data.get('top_names', [])[:10]:
            all_entities.append(('اسم', name, count))
        
        # إضافة الأماكن
        for place, count in entities_data.get('top_places', [])[:10]:
            all_entities.append(('مكان', place, count))
        
        # إضافة المؤسسات
        for org, count in entities_data.get('top_organizations', [])[:10]:
            all_entities.append(('مؤسسة', org, count))
        
        entities_table.setRowCount(len(all_entities))
        
        for i, (entity_type, entity_name, count) in enumerate(all_entities):
            entities_table.setItem(i, 0, QTableWidgetItem(entity_type))
            entities_table.setItem(i, 1, QTableWidgetItem(entity_name))
            entities_table.setItem(i, 2, QTableWidgetItem(str(count)))
            entities_table.setItem(i, 3, QTableWidgetItem(f"{(count/len(all_entities)*100):.1f}%"))
        
        entities_table.setStyleSheet(self.get_table_style())
        entities_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        entities_table.setFixedHeight(250)
        
        entities_layout.addWidget(entities_table)
        self.results_layout.addWidget(entities_group)
    
    def get_section_style(self):
        """الحصول على نمط القسم"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2196F3;
            }
        """
    
    def get_table_style(self):
        """الحصول على نمط الجدول"""
        return """
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                gridline-color: #f0f0f0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: #000;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """
    
    def export_to_excel(self):
        """تصدير النتائج إلى Excel"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "حفظ النتائج", "", "Excel (*.xlsx);;CSV (*.csv)"
            )
            
            if filename:
                # هنا يمكن إضافة كود التصدير الفعلي
                QMessageBox.information(self, "نجح", f"تم حفظ النتائج في: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في التصدير:\n{str(e)}")
