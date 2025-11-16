"""
نافذة الإعدادات المتقدمة للمعالج اللغوي
Advanced Settings Dialog for Linguistic Processor
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
        QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox, QPushButton,
        QGroupBox, QFormLayout, QTextEdit, QFileDialog, QMessageBox,
        QSlider, QProgressBar, QListWidget, QListWidgetItem, QSplitter
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
    from PyQt6.QtGui import QFont, QIcon, QPixmap
    
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.settings_manager import settings_manager, SettingsManager
    from utils.advanced_logger import AdvancedLogger
except ImportError:
    settings_manager = None
    AdvancedLogger = None


# @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
class SettingsDialog(QDialog):
    """نافذة الإعدادات المتقدمة"""
    
    settings_changed = pyqtSignal(dict)  # إشارة عند تغيير الإعدادات
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager or SettingsManager()
        self.logger = AdvancedLogger("settings_dialog") if AdvancedLogger else None
        
        self.setWindowTitle("الإعدادات المتقدمة - المختار اللغوي الجديد")
        self.setModal(True)
        self.resize(800, 600)
        
        # إعداد الواجهة
        self.setup_ui()
        self.load_current_settings()
        self.apply_styles()
        
        # إعداد المؤقتات
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_settings)
        self.auto_save_timer.start(30000)  # حفظ تلقائي كل 30 ثانية
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        
        # إنشاء تبويبات الإعدادات
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # تبويب معالجة العربية
        self.setup_arabic_processing_tab()
        
        # تبويب الأداء
        self.setup_performance_tab()
        
        # تبويب التسجيل
        self.setup_logging_tab()
        
        # تبويب الواجهة
        self.setup_ui_tab()
        
        # تبويب التحليل
        self.setup_analysis_tab()
        
        # تبويب قاعدة البيانات
        self.setup_database_tab()
        
        # تبويب التطبيق
        self.setup_application_tab()
        
        # أزرار التحكم
        self.setup_control_buttons(layout)
    
    def setup_arabic_processing_tab(self):
        """إعداد تبويب معالجة العربية"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة التطبيع
        normalization_group = QGroupBox("إعدادات التطبيع")
        normalization_layout = QFormLayout(normalization_group)
        
        self.normalize_alef_cb = QCheckBox("توحيد أشكال الألف")
        self.normalize_hamza_cb = QCheckBox("توحيد أشكال الهمزة")
        self.normalize_yaa_cb = QCheckBox("توحيد الياء والألف المقصورة")
        self.normalize_taa_cb = QCheckBox("توحيد التاء المربوطة والهاء")
        self.remove_tashkeel_cb = QCheckBox("إزالة التشكيل")
        
        normalization_layout.addRow(self.normalize_alef_cb)
        normalization_layout.addRow(self.normalize_hamza_cb)
        normalization_layout.addRow(self.normalize_yaa_cb)
        normalization_layout.addRow(self.normalize_taa_cb)
        normalization_layout.addRow(self.remove_tashkeel_cb)
        
        # مجموعة التقسيم
        tokenization_group = QGroupBox("إعدادات التقسيم")
        tokenization_layout = QFormLayout(tokenization_group)
        
        self.min_word_length_spin = QSpinBox()
        self.min_word_length_spin.setRange(1, 20)
        self.min_word_length_spin.setValue(2)
        
        self.max_word_length_spin = QSpinBox()
        self.max_word_length_spin.setRange(10, 100)
        self.max_word_length_spin.setValue(50)
        
        tokenization_layout.addRow("الحد الأدنى لطول الكلمة:", self.min_word_length_spin)
        tokenization_layout.addRow("الحد الأقصى لطول الكلمة:", self.max_word_length_spin)
        
        # مجموعة كلمات الوقف
        stopwords_group = QGroupBox("إعدادات كلمات الوقف")
        stopwords_layout = QVBoxLayout(stopwords_group)
        
        self.remove_stop_words_cb = QCheckBox("إزالة كلمات الوقف")
        stopwords_layout.addWidget(self.remove_stop_words_cb)
        
        # كلمات وقف مخصصة
        custom_stopwords_label = QLabel("كلمات وقف مخصصة (مفصولة بفواصل):")
        stopwords_layout.addWidget(custom_stopwords_label)
        
        self.custom_stopwords_text = QTextEdit()
        self.custom_stopwords_text.setMaximumHeight(100)
        stopwords_layout.addWidget(self.custom_stopwords_text)
        
        # مجموعة استخراج الجذور
        stemming_group = QGroupBox("إعدادات استخراج الجذور")
        stemming_layout = QFormLayout(stemming_group)
        
        self.enable_stemming_cb = QCheckBox("تفعيل استخراج الجذور")
        self.stemming_algorithm_combo = QComboBox()
        self.stemming_algorithm_combo.addItems(["light", "advanced", "khalil"])
        
        stemming_layout.addRow(self.enable_stemming_cb)
        stemming_layout.addRow("خوارزمية استخراج الجذور:", self.stemming_algorithm_combo)
        
        # إضافة المجموعات إلى التخطيط
        layout.addWidget(normalization_group)
        layout.addWidget(tokenization_group)
        layout.addWidget(stopwords_group)
        layout.addWidget(stemming_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "معالجة العربية")
    
    def setup_performance_tab(self):
        """إعداد تبويب الأداء"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة التخزين المؤقت
        cache_group = QGroupBox("إعدادات التخزين المؤقت")
        cache_layout = QFormLayout(cache_group)
        
        self.cache_enabled_cb = QCheckBox("تفعيل التخزين المؤقت")
        self.cache_strategy_combo = QComboBox()
        self.cache_strategy_combo.addItems(["memory_only", "disk_only", "hybrid"])
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 10000)
        self.cache_size_spin.setValue(2000)
        
        self.cache_ttl_spin = QSpinBox()
        self.cache_ttl_spin.setRange(60, 86400)  # من دقيقة إلى يوم
        self.cache_ttl_spin.setValue(7200)
        
        cache_layout.addRow(self.cache_enabled_cb)
        cache_layout.addRow("استراتيجية التخزين المؤقت:", self.cache_strategy_combo)
        cache_layout.addRow("حجم التخزين المؤقت:", self.cache_size_spin)
        cache_layout.addRow("وقت انتهاء الصلاحية (ثانية):", self.cache_ttl_spin)
        
        # مجموعة المعالجة المتوازية
        parallel_group = QGroupBox("إعدادات المعالجة المتوازية")
        parallel_layout = QFormLayout(parallel_group)
        
        self.parallel_processing_cb = QCheckBox("تفعيل المعالجة المتوازية")
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 16)
        self.max_workers_spin.setValue(4)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 2000)
        self.chunk_size_spin.setValue(500)
        
        parallel_layout.addRow(self.parallel_processing_cb)
        parallel_layout.addRow("الحد الأقصى للعمال:", self.max_workers_spin)
        parallel_layout.addRow("حجم الجزء:", self.chunk_size_spin)
        
        # مجموعة الذاكرة
        memory_group = QGroupBox("إعدادات الذاكرة")
        memory_layout = QFormLayout(memory_group)
        
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(64, 2048)
        self.memory_limit_spin.setValue(512)
        
        self.gc_threshold_spin = QSpinBox()
        self.gc_threshold_spin.setRange(100, 10000)
        self.gc_threshold_spin.setValue(1000)
        
        memory_layout.addRow("حد الذاكرة (ميجابايت):", self.memory_limit_spin)
        memory_layout.addRow("عتبة تنظيف الذاكرة:", self.gc_threshold_spin)
        
        # مجموعة نمط المعالجة
        processing_group = QGroupBox("نمط المعالجة")
        processing_layout = QFormLayout(processing_group)
        
        self.processing_mode_combo = QComboBox()
        self.processing_mode_combo.addItems(["fast", "balanced", "accurate"])
        
        processing_layout.addRow("نمط المعالجة:", self.processing_mode_combo)
        
        # إضافة المجموعات
        layout.addWidget(cache_group)
        layout.addWidget(parallel_group)
        layout.addWidget(memory_group)
        layout.addWidget(processing_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "الأداء")
    
    def setup_logging_tab(self):
        """إعداد تبويب التسجيل"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة مستوى التسجيل
        level_group = QGroupBox("مستوى التسجيل")
        level_layout = QFormLayout(level_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
        self.console_logging_cb = QCheckBox("تسجيل في وحدة التحكم")
        self.file_logging_cb = QCheckBox("تسجيل في الملفات")
        
        level_layout.addRow("مستوى التسجيل:", self.log_level_combo)
        level_layout.addRow(self.console_logging_cb)
        level_layout.addRow(self.file_logging_cb)
        
        # مجموعة ملفات التسجيل
        files_group = QGroupBox("إعدادات ملفات التسجيل")
        files_layout = QFormLayout(files_group)
        
        self.log_directory_edit = QLineEdit()
        self.log_directory_edit.setText("logs")
        
        self.log_file_prefix_edit = QLineEdit()
        self.log_file_prefix_edit.setText("linguistic_processor")
        
        self.max_log_files_spin = QSpinBox()
        self.max_log_files_spin.setRange(1, 50)
        self.max_log_files_spin.setValue(10)
        
        self.max_log_size_spin = QSpinBox()
        self.max_log_size_spin.setRange(1, 100)
        self.max_log_size_spin.setValue(10)
        
        files_layout.addRow("مجلد التسجيل:", self.log_directory_edit)
        files_layout.addRow("بادئة ملف التسجيل:", self.log_file_prefix_edit)
        files_layout.addRow("الحد الأقصى لملفات التسجيل:", self.max_log_files_spin)
        files_layout.addRow("الحد الأقصى لحجم الملف (ميجابايت):", self.max_log_size_spin)
        
        # مجموعة التسجيل الخاص
        special_group = QGroupBox("إعدادات التسجيل الخاصة")
        special_layout = QFormLayout(special_group)
        
        self.log_performance_cb = QCheckBox("تسجيل معلومات الأداء")
        self.log_arabic_text_cb = QCheckBox("تسجيل النصوص العربية")
        
        special_layout.addRow(self.log_performance_cb)
        special_layout.addRow(self.log_arabic_text_cb)
        
        # إضافة المجموعات
        layout.addWidget(level_group)
        layout.addWidget(files_group)
        layout.addWidget(special_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "التسجيل")
    
    def setup_ui_tab(self):
        """إعداد تبويب الواجهة"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة النافذة
        window_group = QGroupBox("إعدادات النافذة")
        window_layout = QFormLayout(window_group)
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(400, 2000)
        self.window_width_spin.setValue(1200)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(300, 1500)
        self.window_height_spin.setValue(800)
        
        self.window_maximized_cb = QCheckBox("فتح النافذة مكبرة")
        
        window_layout.addRow("عرض النافذة:", self.window_width_spin)
        window_layout.addRow("ارتفاع النافذة:", self.window_height_spin)
        window_layout.addRow(self.window_maximized_cb)
        
        # مجموعة الخط
        font_group = QGroupBox("إعدادات الخط")
        font_layout = QFormLayout(font_group)
        
        self.font_family_edit = QLineEdit()
        self.font_family_edit.setText("Arial")
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        
        self.arabic_font_family_edit = QLineEdit()
        self.arabic_font_family_edit.setText("Arial Unicode MS")
        
        font_layout.addRow("عائلة الخط:", self.font_family_edit)
        font_layout.addRow("حجم الخط:", self.font_size_spin)
        font_layout.addRow("عائلة الخط العربي:", self.arabic_font_family_edit)
        
        # مجموعة الألوان
        colors_group = QGroupBox("إعدادات الألوان")
        colors_layout = QFormLayout(colors_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "auto"])
        
        self.primary_color_edit = QLineEdit()
        self.primary_color_edit.setText("#2E86AB")
        
        self.secondary_color_edit = QLineEdit()
        self.secondary_color_edit.setText("#A23B72")
        
        colors_layout.addRow("المظهر:", self.theme_combo)
        colors_layout.addRow("اللون الأساسي:", self.primary_color_edit)
        colors_layout.addRow("اللون الثانوي:", self.secondary_color_edit)
        
        # مجموعة اللغة
        language_group = QGroupBox("إعدادات اللغة")
        language_layout = QFormLayout(language_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["ar", "en"])
        
        self.rtl_support_cb = QCheckBox("دعم الكتابة من اليمين إلى اليسار")
        
        language_layout.addRow("اللغة:", self.language_combo)
        language_layout.addRow(self.rtl_support_cb)
        
        # مجموعة العرض
        display_group = QGroupBox("إعدادات العرض")
        display_layout = QFormLayout(display_group)
        
        self.show_toolbar_cb = QCheckBox("إظهار شريط الأدوات")
        self.show_sidebar_cb = QCheckBox("إظهار الشريط الجانبي")
        self.show_statusbar_cb = QCheckBox("إظهار شريط الحالة")
        
        display_layout.addRow(self.show_toolbar_cb)
        display_layout.addRow(self.show_sidebar_cb)
        display_layout.addRow(self.show_statusbar_cb)
        
        # إضافة المجموعات
        layout.addWidget(window_group)
        layout.addWidget(font_group)
        layout.addWidget(colors_group)
        layout.addWidget(language_group)
        layout.addWidget(display_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "الواجهة")
    
    def setup_analysis_tab(self):
        """إعداد تبويب التحليل"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة تحليل التكرار
        frequency_group = QGroupBox("إعدادات تحليل التكرار")
        frequency_layout = QFormLayout(frequency_group)
        
        self.min_frequency_spin = QSpinBox()
        self.min_frequency_spin.setRange(1, 100)
        self.min_frequency_spin.setValue(2)
        
        self.max_frequency_spin = QSpinBox()
        self.max_frequency_spin.setRange(10, 10000)
        self.max_frequency_spin.setValue(1000)
        
        frequency_layout.addRow("الحد الأدنى للتكرار:", self.min_frequency_spin)
        frequency_layout.addRow("الحد الأقصى للتكرار:", self.max_frequency_spin)
        
        # مجموعة الكلمات المتجاورة
        collocations_group = QGroupBox("إعدادات الكلمات المتجاورة")
        collocations_layout = QFormLayout(collocations_group)
        
        self.collocation_window_spin = QSpinBox()
        self.collocation_window_spin.setRange(2, 20)
        self.collocation_window_spin.setValue(5)
        
        self.min_collocation_frequency_spin = QSpinBox()
        self.min_collocation_frequency_spin.setRange(1, 100)
        self.min_collocation_frequency_spin.setValue(3)
        
        collocations_layout.addRow("حجم النافذة:", self.collocation_window_spin)
        collocations_layout.addRow("الحد الأدنى لتكرار التجاوز:", self.min_collocation_frequency_spin)
        
        # مجموعة KWIC
        kwic_group = QGroupBox("إعدادات KWIC")
        kwic_layout = QFormLayout(kwic_group)
        
        self.kwic_context_size_spin = QSpinBox()
        self.kwic_context_size_spin.setRange(5, 50)
        self.kwic_context_size_spin.setValue(10)
        
        kwic_layout.addRow("حجم السياق:", self.kwic_context_size_spin)
        
        # مجموعة الكلمات المفتاحية
        keywords_group = QGroupBox("إعدادات الكلمات المفتاحية")
        keywords_layout = QFormLayout(keywords_group)
        
        self.keyword_algorithm_combo = QComboBox()
        self.keyword_algorithm_combo.addItems(["tfidf", "textrank", "yake"])
        
        self.max_keywords_spin = QSpinBox()
        self.max_keywords_spin.setRange(10, 500)
        self.max_keywords_spin.setValue(50)
        
        keywords_layout.addRow("خوارزمية الكلمات المفتاحية:", self.keyword_algorithm_combo)
        keywords_layout.addRow("الحد الأقصى للكلمات المفتاحية:", self.max_keywords_spin)
        
        # مجموعة N-grams
        ngrams_group = QGroupBox("إعدادات N-grams")
        ngrams_layout = QFormLayout(ngrams_group)
        
        self.max_ngram_size_spin = QSpinBox()
        self.max_ngram_size_spin.setRange(2, 10)
        self.max_ngram_size_spin.setValue(5)
        
        self.min_ngram_frequency_spin = QSpinBox()
        self.min_ngram_frequency_spin.setRange(1, 100)
        self.min_ngram_frequency_spin.setValue(2)
        
        ngrams_layout.addRow("الحد الأقصى لحجم N-gram:", self.max_ngram_size_spin)
        ngrams_layout.addRow("الحد الأدنى لتكرار N-gram:", self.min_ngram_frequency_spin)
        
        # مجموعة سحابة الكلمات
        wordcloud_group = QGroupBox("إعدادات سحابة الكلمات")
        wordcloud_layout = QFormLayout(wordcloud_group)
        
        self.wordcloud_max_words_spin = QSpinBox()
        self.wordcloud_max_words_spin.setRange(10, 1000)
        self.wordcloud_max_words_spin.setValue(100)
        
        self.wordcloud_colormap_combo = QComboBox()
        self.wordcloud_colormap_combo.addItems(["viridis", "plasma", "inferno", "magma", "cividis"])
        
        wordcloud_layout.addRow("الحد الأقصى للكلمات:", self.wordcloud_max_words_spin)
        wordcloud_layout.addRow("خريطة الألوان:", self.wordcloud_colormap_combo)
        
        # إضافة المجموعات
        layout.addWidget(frequency_group)
        layout.addWidget(collocations_group)
        layout.addWidget(kwic_group)
        layout.addWidget(keywords_group)
        layout.addWidget(ngrams_group)
        layout.addWidget(wordcloud_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "التحليل")
    
    def setup_database_tab(self):
        """إعداد تبويب قاعدة البيانات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة المسار
        path_group = QGroupBox("إعدادات المسار")
        path_layout = QFormLayout(path_group)
        
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setText("features/morphological_generation/db")
        
        browse_btn = QPushButton("تصفح...")
        browse_btn.clicked.connect(self.browse_db_path)
        
        path_layout.addRow("مسار قاعدة البيانات:", self.db_path_edit)
        path_layout.addRow("", browse_btn)
        
        # مجموعة التحميل
        loading_group = QGroupBox("إعدادات التحميل")
        loading_layout = QFormLayout(loading_group)
        
        self.load_prefixes_cb = QCheckBox("تحميل البادئات")
        self.load_suffixes_cb = QCheckBox("تحميل اللواحق")
        self.load_patterns_cb = QCheckBox("تحميل الأنماط")
        self.load_roots_cb = QCheckBox("تحميل الجذور")
        self.load_toolwords_cb = QCheckBox("تحميل الكلمات المساعدة")
        
        loading_layout.addRow(self.load_prefixes_cb)
        loading_layout.addRow(self.load_suffixes_cb)
        loading_layout.addRow(self.load_patterns_cb)
        loading_layout.addRow(self.load_roots_cb)
        loading_layout.addRow(self.load_toolwords_cb)
        
        # مجموعة الترميز
        encoding_group = QGroupBox("إعدادات الترميز")
        encoding_layout = QFormLayout(encoding_group)
        
        self.default_encoding_edit = QLineEdit()
        self.default_encoding_edit.setText("utf-8")
        
        self.fallback_encodings_text = QTextEdit()
        self.fallback_encodings_text.setMaximumHeight(80)
        self.fallback_encodings_text.setPlainText("utf-8-sig\nwindows-1256\ncp1256\niso-8859-6")
        
        encoding_layout.addRow("الترميز الافتراضي:", self.default_encoding_edit)
        encoding_layout.addRow("ترميزات احتياطية:", self.fallback_encodings_text)
        
        # إضافة المجموعات
        layout.addWidget(path_group)
        layout.addWidget(loading_group)
        layout.addWidget(encoding_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "قاعدة البيانات")
    
    def setup_application_tab(self):
        """إعداد تبويب التطبيق"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مجموعة التطبيق
        app_group = QGroupBox("معلومات التطبيق")
        app_layout = QFormLayout(app_group)
        
        self.app_name_edit = QLineEdit()
        self.app_name_edit.setText("المختار اللغوي الجديد")
        
        self.app_version_edit = QLineEdit()
        self.app_version_edit.setText("2.0.0")
        
        self.app_author_edit = QLineEdit()
        self.app_author_edit.setText("فريق التطوير")
        
        app_layout.addRow("اسم التطبيق:", self.app_name_edit)
        app_layout.addRow("إصدار التطبيق:", self.app_version_edit)
        app_layout.addRow("مطور التطبيق:", self.app_author_edit)
        
        # مجموعة الملفات
        files_group = QGroupBox("إعدادات الملفات")
        files_layout = QFormLayout(files_group)
        
        self.auto_save_cb = QCheckBox("حفظ تلقائي")
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(60, 3600)
        self.auto_save_interval_spin.setValue(300)
        
        self.backup_enabled_cb = QCheckBox("تفعيل النسخ الاحتياطي")
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 20)
        self.backup_count_spin.setValue(5)
        
        files_layout.addRow(self.auto_save_cb)
        files_layout.addRow("فترة الحفظ التلقائي (ثانية):", self.auto_save_interval_spin)
        files_layout.addRow(self.backup_enabled_cb)
        files_layout.addRow("عدد النسخ الاحتياطية:", self.backup_count_spin)
        
        # مجموعة التحديث
        update_group = QGroupBox("إعدادات التحديث")
        update_layout = QFormLayout(update_group)
        
        self.check_updates_cb = QCheckBox("التحقق من التحديثات")
        self.update_channel_combo = QComboBox()
        self.update_channel_combo.addItems(["stable", "beta", "dev"])
        
        update_layout.addRow(self.check_updates_cb)
        update_layout.addRow("قناة التحديث:", self.update_channel_combo)
        
        # مجموعة الخصوصية
        privacy_group = QGroupBox("إعدادات الخصوصية")
        privacy_layout = QFormLayout(privacy_group)
        
        self.collect_analytics_cb = QCheckBox("جمع البيانات التحليلية")
        self.send_crash_reports_cb = QCheckBox("إرسال تقارير الأخطاء")
        
        privacy_layout.addRow(self.collect_analytics_cb)
        privacy_layout.addRow(self.send_crash_reports_cb)
        
        # إضافة المجموعات
        layout.addWidget(app_group)
        layout.addWidget(files_group)
        layout.addWidget(update_group)
        layout.addWidget(privacy_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "التطبيق")
    
    def setup_control_buttons(self, layout):
        """إعداد أزرار التحكم"""
        button_layout = QHBoxLayout()
        
        # أزرار الإعدادات
        self.reset_btn = QPushButton("إعادة تعيين")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        self.import_btn = QPushButton("استيراد")
        self.import_btn.clicked.connect(self.import_settings)
        
        self.export_btn = QPushButton("تصدير")
        self.export_btn.clicked.connect(self.export_settings)
        
        # أزرار التحكم الرئيسية
        self.apply_btn = QPushButton("تطبيق")
        self.apply_btn.clicked.connect(self.apply_settings)
        
        self.save_btn = QPushButton("حفظ")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("موافق")
        self.ok_btn.clicked.connect(self.accept_and_save)
        
        # إضافة الأزرار
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def load_current_settings(self):
        """تحميل الإعدادات الحالية"""
        if not self.settings_manager:
            return
        
        # تحميل إعدادات معالجة العربية
        arabic_settings = self.settings_manager.get_category('arabic_processing')
        self.normalize_alef_cb.setChecked(arabic_settings.get('normalize_alef', True))
        self.normalize_hamza_cb.setChecked(arabic_settings.get('normalize_hamza', True))
        self.normalize_yaa_cb.setChecked(arabic_settings.get('normalize_yaa', True))
        self.normalize_taa_cb.setChecked(arabic_settings.get('normalize_taa', False))
        self.remove_tashkeel_cb.setChecked(arabic_settings.get('remove_tashkeel', True))
        
        self.min_word_length_spin.setValue(arabic_settings.get('min_word_length', 2))
        self.max_word_length_spin.setValue(arabic_settings.get('max_word_length', 50))
        
        self.remove_stop_words_cb.setChecked(arabic_settings.get('remove_stop_words', True))
        custom_stop_words = arabic_settings.get('custom_stop_words', [])
        self.custom_stopwords_text.setPlainText(', '.join(custom_stop_words))
        
        self.enable_stemming_cb.setChecked(arabic_settings.get('enable_stemming', True))
        stemming_algorithm = arabic_settings.get('stemming_algorithm', 'light')
        self.stemming_algorithm_combo.setCurrentText(stemming_algorithm)
        
        # تحميل إعدادات الأداء
        performance_settings = self.settings_manager.get_category('performance')
        self.cache_enabled_cb.setChecked(performance_settings.get('cache_enabled', True))
        cache_strategy = performance_settings.get('cache_strategy', 'hybrid')
        self.cache_strategy_combo.setCurrentText(cache_strategy)
        self.cache_size_spin.setValue(performance_settings.get('cache_size', 2000))
        self.cache_ttl_spin.setValue(performance_settings.get('cache_ttl', 7200))
        
        self.parallel_processing_cb.setChecked(performance_settings.get('parallel_processing', True))
        self.max_workers_spin.setValue(performance_settings.get('max_workers', 4))
        self.chunk_size_spin.setValue(performance_settings.get('chunk_size', 500))
        
        self.memory_limit_spin.setValue(performance_settings.get('memory_limit_mb', 512))
        self.gc_threshold_spin.setValue(performance_settings.get('gc_threshold', 1000))
        
        processing_mode = performance_settings.get('processing_mode', 'balanced')
        self.processing_mode_combo.setCurrentText(processing_mode)
        
        # تحميل باقي الإعدادات...
        # (يمكن إضافة المزيد حسب الحاجة)
    
    def apply_settings(self):
        """تطبيق الإعدادات"""
        try:
            # جمع الإعدادات من الواجهة
            settings = self.collect_settings()
            
            # التحقق من صحة الإعدادات
            errors = self.settings_manager.validate_settings()
            if errors:
                QMessageBox.warning(self, "تحذير", f"أخطاء في الإعدادات:\n" + "\n".join(errors))
                return
            
            # تطبيق الإعدادات
            for category, category_settings in settings.items():
                self.settings_manager.set_category(category, category_settings)
            
            # إرسال إشارة التغيير
            self.settings_changed.emit(settings)
            
            QMessageBox.information(self, "نجح", "تم تطبيق الإعدادات بنجاح")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تطبيق الإعدادات: {e}")
    
    def save_settings(self):
        """حفظ الإعدادات"""
        try:
            # جمع الإعدادات من الواجهة
            settings = self.collect_settings()
            
            # تطبيق الإعدادات
            for category, category_settings in settings.items():
                self.settings_manager.set_category(category, category_settings)
            
            # حفظ الإعدادات
            self.settings_manager.save_settings()
            
            QMessageBox.information(self, "نجح", "تم حفظ الإعدادات بنجاح")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الإعدادات: {e}")
    
    def accept_and_save(self):
        """قبول الإعدادات وحفظها"""
        self.save_settings()
        self.accept()
    
    def reset_settings(self):
        """إعادة تعيين الإعدادات للقيم الافتراضية"""
        reply = QMessageBox.question(
            self, "تأكيد", 
            "هل أنت متأكد من إعادة تعيين جميع الإعدادات للقيم الافتراضية؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.reset_to_defaults()
            self.load_current_settings()
            QMessageBox.information(self, "نجح", "تم إعادة تعيين الإعدادات")
    
    def import_settings(self):
        """استيراد الإعدادات من ملف"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "استيراد الإعدادات", "", "ملفات JSON (*.json)"
        )
        
        if file_path:
            try:
                self.settings_manager.import_settings(file_path)
                self.load_current_settings()
                QMessageBox.information(self, "نجح", "تم استيراد الإعدادات بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في استيراد الإعدادات: {e}")
    
    def export_settings(self):
        """تصدير الإعدادات إلى ملف"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "تصدير الإعدادات", "settings_backup.json", "ملفات JSON (*.json)"
        )
        
        if file_path:
            try:
                self.settings_manager.export_settings(file_path)
                QMessageBox.information(self, "نجح", "تم تصدير الإعدادات بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في تصدير الإعدادات: {e}")
    
    def browse_db_path(self):
        """تصفح مسار قاعدة البيانات"""
        directory = QFileDialog.getExistingDirectory(
            self, "اختيار مجلد قاعدة البيانات"
        )
        
        if directory:
            self.db_path_edit.setText(directory)
    
    def collect_settings(self) -> Dict[str, Dict[str, Any]]:
        """جمع الإعدادات من الواجهة"""
        settings = {}
        
        # إعدادات معالجة العربية
        settings['arabic_processing'] = {
            'normalize_alef': self.normalize_alef_cb.isChecked(),
            'normalize_hamza': self.normalize_hamza_cb.isChecked(),
            'normalize_yaa': self.normalize_yaa_cb.isChecked(),
            'normalize_taa': self.normalize_taa_cb.isChecked(),
            'remove_tashkeel': self.remove_tashkeel_cb.isChecked(),
            'min_word_length': self.min_word_length_spin.value(),
            'max_word_length': self.max_word_length_spin.value(),
            'remove_stop_words': self.remove_stop_words_cb.isChecked(),
            'custom_stop_words': [w.strip() for w in self.custom_stopwords_text.toPlainText().split(',') if w.strip()],
            'enable_stemming': self.enable_stemming_cb.isChecked(),
            'stemming_algorithm': self.stemming_algorithm_combo.currentText()
        }
        
        # إعدادات الأداء
        settings['performance'] = {
            'cache_enabled': self.cache_enabled_cb.isChecked(),
            'cache_strategy': self.cache_strategy_combo.currentText(),
            'cache_size': self.cache_size_spin.value(),
            'cache_ttl': self.cache_ttl_spin.value(),
            'parallel_processing': self.parallel_processing_cb.isChecked(),
            'max_workers': self.max_workers_spin.value(),
            'chunk_size': self.chunk_size_spin.value(),
            'memory_limit_mb': self.memory_limit_spin.value(),
            'gc_threshold': self.gc_threshold_spin.value(),
            'processing_mode': self.processing_mode_combo.currentText()
        }
        
        # إعدادات التسجيل
        settings['logging'] = {
            'log_level': self.log_level_combo.currentText(),
            'console_logging': self.console_logging_cb.isChecked(),
            'file_logging': self.file_logging_cb.isChecked(),
            'log_directory': self.log_directory_edit.text(),
            'log_file_prefix': self.log_file_prefix_edit.text(),
            'max_log_files': self.max_log_files_spin.value(),
            'max_log_size_mb': self.max_log_size_spin.value(),
            'log_performance': self.log_performance_cb.isChecked(),
            'log_arabic_text': self.log_arabic_text_cb.isChecked()
        }
        
        # إعدادات الواجهة
        settings['ui'] = {
            'window_width': self.window_width_spin.value(),
            'window_height': self.window_height_spin.value(),
            'window_maximized': self.window_maximized_cb.isChecked(),
            'font_family': self.font_family_edit.text(),
            'font_size': self.font_size_spin.value(),
            'arabic_font_family': self.arabic_font_family_edit.text(),
            'theme': self.theme_combo.currentText(),
            'primary_color': self.primary_color_edit.text(),
            'secondary_color': self.secondary_color_edit.text(),
            'language': self.language_combo.currentText(),
            'rtl_support': self.rtl_support_cb.isChecked(),
            'show_toolbar': self.show_toolbar_cb.isChecked(),
            'show_sidebar': self.show_sidebar_cb.isChecked(),
            'show_statusbar': self.show_statusbar_cb.isChecked()
        }
        
        # إعدادات التحليل
        settings['analysis'] = {
            'min_frequency': self.min_frequency_spin.value(),
            'max_frequency': self.max_frequency_spin.value(),
            'collocation_window': self.collocation_window_spin.value(),
            'min_collocation_frequency': self.min_collocation_frequency_spin.value(),
            'kwic_context_size': self.kwic_context_size_spin.value(),
            'keyword_algorithm': self.keyword_algorithm_combo.currentText(),
            'max_keywords': self.max_keywords_spin.value(),
            'max_ngram_size': self.max_ngram_size_spin.value(),
            'min_ngram_frequency': self.min_ngram_frequency_spin.value(),
            'wordcloud_max_words': self.wordcloud_max_words_spin.value(),
            'wordcloud_colormap': self.wordcloud_colormap_combo.currentText()
        }
        
        # إعدادات قاعدة البيانات
        settings['database'] = {
            'db_path': self.db_path_edit.text(),
            'load_prefixes': self.load_prefixes_cb.isChecked(),
            'load_suffixes': self.load_suffixes_cb.isChecked(),
            'load_patterns': self.load_patterns_cb.isChecked(),
            'load_roots': self.load_roots_cb.isChecked(),
            'load_toolwords': self.load_toolwords_cb.isChecked(),
            'default_encoding': self.default_encoding_edit.text(),
            'fallback_encodings': [e.strip() for e in self.fallback_encodings_text.toPlainText().split('\n') if e.strip()]
        }
        
        # إعدادات التطبيق
        settings['application'] = {
            'app_name': self.app_name_edit.text(),
            'app_version': self.app_version_edit.text(),
            'app_author': self.app_author_edit.text(),
            'auto_save': self.auto_save_cb.isChecked(),
            'auto_save_interval': self.auto_save_interval_spin.value(),
            'backup_enabled': self.backup_enabled_cb.isChecked(),
            'backup_count': self.backup_count_spin.value(),
            'check_updates': self.check_updates_cb.isChecked(),
            'update_channel': self.update_channel_combo.currentText(),
            'collect_analytics': self.collect_analytics_cb.isChecked(),
            'send_crash_reports': self.send_crash_reports_cb.isChecked()
        }
        
        return settings
    
    def auto_save_settings(self):
        """حفظ تلقائي للإعدادات"""
        try:
            settings = self.collect_settings()
            for category, category_settings in settings.items():
                self.settings_manager.set_category(category, category_settings)
            self.settings_manager.save_settings()
        except Exception as e:
            if self.logger:
                self.logger.error(f"فشل في الحفظ التلقائي: {e}")
    
    def apply_styles(self):
        """تطبيق الأنماط على الواجهة"""
        style = """
        QDialog {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        
        QTabWidget::tab-bar {
            alignment: center;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #2E86AB;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #2E86AB;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1e5a7a;
        }
        
        QPushButton:pressed {
            background-color: #0d3a4a;
        }
        
        QLineEdit, QSpinBox, QComboBox, QTextEdit {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 4px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
            border: 2px solid #2E86AB;
        }
        """
        
        self.setStyleSheet(style)


if __name__ == '__main__':
    if not PYQT_AVAILABLE:
        print("PyQt6 غير متاح - لا يمكن تشغيل نافذة الإعدادات")
        sys.exit(1)
    
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = SettingsDialog()
    dialog.show()
    
    sys.exit(app.exec())
