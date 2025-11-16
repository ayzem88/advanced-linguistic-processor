"""
نافذة التوليد الصرفي - التصميم المطابق للمعالج اللغوي
Morphological Generation Dialog - Linguistic Processor Design
"""

import sys
import os
from pathlib import Path

# إضافة المسار المحلي للمحلل الصرفي
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QWidget, QMessageBox, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

try:
    from khalil_analyzer import KhalilAnalyzer
except ImportError:
    KhalilAnalyzer = None


class AnalysisWorker(QThread):
    """عامل التحليل في الخلفية"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, analyzer, text):
        super().__init__()
        self.analyzer = analyzer
        self.text = text
    
    def run(self):
        try:
            self.progress.emit("جارٍ التحليل...")
            
            # تقسيم النص إلى كلمات
            words = self.text.strip().split()
            all_results = []
            
            for word in words:
                if not word:
                    continue
                    
                self.progress.emit(f"تحليل: {word}")
                results = self.analyzer.analyze_word(word)
                
                if results:
                    # أخذ أفضل نتيجة لكل كلمة
                    for result in results[:1]:  # فقط النتيجة الأولى (الأفضل)
                        all_results.append({
                            'word': word,
                            'result': result
                        })
                else:
                    # لا توجد نتائج
                    all_results.append({
                        'word': word,
                        'result': None
                    })
            
            self.finished.emit(all_results)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class MorphologicalDialog(QDialog):
    """نافذة التوليد الصرفي"""
    
    def __init__(self, initial_text="", parent=None):
        super().__init__(parent)
        self.initial_text = initial_text
        self.analyzer = None
        self.worker = None
        
        self.setWindowTitle("التوليد الصرفي")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(600, 400)
        
        # تطبيق تصميم المعالج اللغوي
        self.apply_linguistic_processor_theme()
        
        self.init_ui()
        self.init_analyzer()
        
        # إذا كان هناك نص مبدئي، قم بالتحليل
        if initial_text:
            self.input_text.setPlainText(initial_text)
            # رسالة توضيحية
            self.status_label.setText(f"📝 تم نقل النص المظلل ({len(initial_text)} حرف)")
            # تأخير التحليل قليلاً للسماح بعرض النافذة
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, self.start_analysis)  # زيادة التأخير لضمان تحميل المحلل
    
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
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e0e0e0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
    
    def init_ui(self):
        """إنشاء الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # العنوان البسيط
        title_label = QLabel("🔤 التوليد الصرفي")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2196F3;
                padding: 10px;
                background-color: #f8f9ff;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # منطقة الإدخال البسيطة
        input_group = self.create_input_area()
        layout.addWidget(input_group)
        
        # منطقة النتائج
        results_group = self.create_results_area()
        layout.addWidget(results_group)
        
        # الشريط السفلي
        footer = self.create_footer()
        layout.addWidget(footer)
    
    
    def create_input_area(self):
        """إنشاء منطقة الإدخال"""
        group = QGroupBox("📝 النص للتحليل")
        
        layout = QVBoxLayout()
        
        # مربع الإدخال
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("أدخل كلمة أو جملة للتحليل الصرفي...")
        self.input_text.setMaximumHeight(100)  # تقليل الارتفاع
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Arial';
                font-size: 12pt;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #2196F3;
            }
        """)
        layout.addWidget(self.input_text)
        
        group.setLayout(layout)
        return group
    
    def create_results_area(self):
        """إنشاء منطقة النتائج"""
        group = QGroupBox("📊 نتائج التحليل")
        
        layout = QVBoxLayout()
        
        # جدول النتائج المبسط
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)  # تقليل الأعمدة
        self.results_table.setHorizontalHeaderLabels([
            "الكلمة", "السوابق", "الجذع", "اللواحق", "النوع"
        ])
        
        # تعيين سلوك الجدول
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # تعديل عرض الأعمدة
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # الكلمة
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # السوابق
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # الجذع
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # اللواحق
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # النوع
        
        layout.addWidget(self.results_table)
        
        group.setLayout(layout)
        return group
    
    def create_footer(self):
        """إنشاء الشريط السفلي"""
        footer = QWidget()
        footer.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(8)
        
        # رسالة الحالة
        self.status_label = QLabel("جاهز للتحليل")
        self.status_label.setStyleSheet("color: #333; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # الأزرار الأساسية فقط
        self.analyze_btn = QPushButton("🔍 تحليل")
        self.analyze_btn.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_btn)
        
        self.clear_btn = QPushButton("🗑️ مسح")
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)
        
        close_btn = QPushButton("❌ إغلاق")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return footer
    
    def init_analyzer(self):
        """تهيئة المحلل الصرفي"""
        try:
            if KhalilAnalyzer is None:
                raise ImportError("لم يتم العثور على KhalilAnalyzer")
            
            self.status_label.setText("⏳ جارٍ تحميل المحلل الصرفي...")
            self.analyzer = KhalilAnalyzer()
            self.status_label.setText("✅ المحلل الصرفي جاهز")
            
        except Exception as e:
            error_msg = f"فشل تحميل المحلل الصرفي:\n{str(e)}"
            self.status_label.setText("❌ خطأ في تحميل المحلل")
            QMessageBox.critical(self, "خطأ", error_msg)
            self.analyze_btn.setEnabled(False)
    
    def start_analysis(self):
        """بدء التحليل"""
        text = self.input_text.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال نص للتحليل")
            return
        
        if not self.analyzer:
            QMessageBox.critical(self, "خطأ", "المحلل الصرفي غير جاهز")
            return
        
        # تعطيل الأزرار
        self.analyze_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        
        # مسح النتائج السابقة
        self.results_table.setRowCount(0)
        
        # بدء التحليل في الخلفية
        self.worker = AnalysisWorker(self.analyzer, text)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.start()
    
    def on_progress_update(self, message: str):
        """تحديث رسالة التقدم"""
        self.status_label.setText(message)
    
    def on_analysis_finished(self, results: list):
        """عند انتهاء التحليل"""
        self.status_label.setText(f"✅ تم التحليل - عدد الكلمات: {len(results)}")
        
        # عرض النتائج في الجدول
        self.display_results(results)
        
        # تفعيل الأزرار
        self.analyze_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
    
    def on_analysis_error(self, error: str):
        """عند حدوث خطأ"""
        self.status_label.setText("❌ فشل التحليل")
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التحليل:\n{error}")
        
        # تفعيل الأزرار
        self.analyze_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
    
    def display_results(self, results: list):
        """عرض النتائج في الجدول"""
        self.results_table.setRowCount(len(results))
        
        for row, item in enumerate(results):
            word = item['word']
            result = item['result']
            
            # الكلمة
            word_item = QTableWidgetItem(word)
            word_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.results_table.setItem(row, 0, word_item)
            
            if result:
                result_type = result.get('type', '')
                
                if result_type == 'morphological':
                    # تحليل صرفي عادي
                    prefixes = result.get('prefixes', [])
                    stem = result.get('stem', '')
                    suffixes = result.get('suffixes', [])
                    
                    # السوابق
                    prefixes_text = ' + '.join(prefixes) if prefixes else '-'
                    self.results_table.setItem(row, 1, QTableWidgetItem(prefixes_text))
                    
                    # الجذع
                    self.results_table.setItem(row, 2, QTableWidgetItem(stem or '-'))
                    
                    # اللواحق
                    suffixes_text = ' + '.join(suffixes) if suffixes else '-'
                    self.results_table.setItem(row, 3, QTableWidgetItem(suffixes_text))
                    
                    # النوع
                    self.results_table.setItem(row, 4, QTableWidgetItem('صرفي'))
                
                elif result_type == 'toolword':
                    # كلمة أداة
                    self.results_table.setItem(row, 1, QTableWidgetItem('-'))
                    self.results_table.setItem(row, 2, QTableWidgetItem(word))
                    self.results_table.setItem(row, 3, QTableWidgetItem('-'))
                    
                    tool_type = result.get('toolword_type', 'أداة')
                    self.results_table.setItem(row, 4, QTableWidgetItem(tool_type))
                
                elif result_type == 'root_direct':
                    # جذر مباشر
                    self.results_table.setItem(row, 1, QTableWidgetItem('-'))
                    self.results_table.setItem(row, 2, QTableWidgetItem('-'))
                    self.results_table.setItem(row, 3, QTableWidgetItem('-'))
                    self.results_table.setItem(row, 4, QTableWidgetItem('جذر'))
                
                else:
                    # نوع غير معروف
                    for col in range(1, 5):
                        self.results_table.setItem(row, col, QTableWidgetItem('-'))
            else:
                # لا توجد نتائج
                self.results_table.setItem(row, 1, QTableWidgetItem('-'))
                self.results_table.setItem(row, 2, QTableWidgetItem('-'))
                self.results_table.setItem(row, 3, QTableWidgetItem('-'))
                
                no_result_item = QTableWidgetItem('لا يوجد')
                no_result_item.setForeground(QColor("#999999"))
                self.results_table.setItem(row, 4, no_result_item)
        
        # تعديل ارتفاع الصفوف
        self.results_table.resizeRowsToContents()
    
    def clear_all(self):
        """مسح كل شيء"""
        self.input_text.clear()
        self.results_table.setRowCount(0)
        self.status_label.setText("جاهز للتحليل")
    


def main():
    """اختبار النافذة"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # نص تجريبي
    test_text = "المسلمون يقرأون الكتب المفيدة"
    
    dialog = MorphologicalDialog(test_text)
    dialog.exec()
    
    sys.exit(0)


if __name__ == "__main__":
    main()
