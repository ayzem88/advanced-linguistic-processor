"""
نظام الإعدادات المتقدم للمعالج اللغوي العربي
Advanced Settings System for Arabic Linguistic Processor
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class LogLevel(Enum):
    """مستويات التسجيل"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheStrategy(Enum):
    """استراتيجيات التخزين المؤقت"""
    MEMORY_ONLY = "memory_only"
    DISK_ONLY = "disk_only"
    HYBRID = "hybrid"


class ProcessingMode(Enum):
    """أنماط المعالجة"""
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"


@dataclass
class ArabicProcessingSettings:
    """إعدادات معالجة النصوص العربية"""
    # إعدادات التطبيع
    normalize_alef: bool = True
    normalize_hamza: bool = True
    normalize_yaa: bool = True
    normalize_taa: bool = False  # افتراضياً غير مفعل لتجنب تغيير المعنى
    
    # إعدادات إزالة التشكيل
    remove_tashkeel: bool = True
    
    # إعدادات التقسيم
    min_word_length: int = 2
    max_word_length: int = 50
    
    # إعدادات كلمات الوقف
    remove_stop_words: bool = True
    custom_stop_words: List[str] = None
    
    # إعدادات استخراج الجذور
    enable_stemming: bool = True
    stemming_algorithm: str = "light"  # light, advanced, khalil
    
    def __post_init__(self):
        if self.custom_stop_words is None:
            self.custom_stop_words = []


@dataclass
class PerformanceSettings:
    """إعدادات الأداء"""
    # إعدادات التخزين المؤقت
    cache_enabled: bool = True
    cache_strategy: CacheStrategy = CacheStrategy.HYBRID
    cache_size: int = 2000
    cache_ttl: int = 7200  # ساعتان
    
    # إعدادات المعالجة المتوازية
    parallel_processing: bool = True
    max_workers: int = 4
    chunk_size: int = 500
    
    # إعدادات الذاكرة
    memory_limit_mb: int = 512
    gc_threshold: int = 1000  # عدد العمليات قبل تنظيف الذاكرة
    
    # إعدادات الأداء
    processing_mode: ProcessingMode = ProcessingMode.BALANCED


@dataclass
class LoggingSettings:
    """إعدادات التسجيل"""
    # إعدادات المستوى
    log_level: LogLevel = LogLevel.INFO
    console_logging: bool = True
    file_logging: bool = True
    
    # إعدادات الملفات
    log_directory: str = "logs"
    log_file_prefix: str = "linguistic_processor"
    max_log_files: int = 10
    max_log_size_mb: int = 10
    
    # إعدادات التنسيق
    log_format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # إعدادات خاصة
    log_performance: bool = True
    log_arabic_text: bool = False  # قد يكون حساساً


@dataclass
class UISettings:
    """إعدادات الواجهة الرسومية"""
    # إعدادات النافذة
    window_width: int = 1200
    window_height: int = 800
    window_maximized: bool = False
    
    # إعدادات الخط
    font_family: str = "Arial"
    font_size: int = 12
    arabic_font_family: str = "Arial Unicode MS"
    
    # إعدادات الألوان
    theme: str = "light"  # light, dark, auto
    primary_color: str = "#2E86AB"
    secondary_color: str = "#A23B72"
    
    # إعدادات اللغة
    language: str = "ar"  # ar, en
    rtl_support: bool = True
    
    # إعدادات العرض
    show_toolbar: bool = True
    show_sidebar: bool = True
    show_statusbar: bool = True


@dataclass
class AnalysisSettings:
    """إعدادات التحليل اللغوي"""
    # إعدادات تحليل التكرار
    min_frequency: int = 2
    max_frequency: int = 1000
    
    # إعدادات الكلمات المتجاورة
    collocation_window: int = 5
    min_collocation_frequency: int = 3
    
    # إعدادات KWIC
    kwic_context_size: int = 10
    
    # إعدادات الكلمات المفتاحية
    keyword_algorithm: str = "tfidf"  # tfidf, textrank, yake
    max_keywords: int = 50
    
    # إعدادات N-grams
    max_ngram_size: int = 5
    min_ngram_frequency: int = 2
    
    # إعدادات سحابة الكلمات
    wordcloud_max_words: int = 100
    wordcloud_colormap: str = "viridis"


@dataclass
class DatabaseSettings:
    """إعدادات قاعدة البيانات الصرفية"""
    # إعدادات المسار
    db_path: str = "features/morphological_generation/db"
    
    # إعدادات التحميل
    load_prefixes: bool = True
    load_suffixes: bool = True
    load_patterns: bool = True
    load_roots: bool = True
    load_toolwords: bool = True
    
    # إعدادات الترميز
    default_encoding: str = "utf-8"
    fallback_encodings: List[str] = None
    
    def __post_init__(self):
        if self.fallback_encodings is None:
            self.fallback_encodings = ["utf-8-sig", "windows-1256", "cp1256", "iso-8859-6"]


@dataclass
class ApplicationSettings:
    """إعدادات التطبيق الرئيسية"""
    # إعدادات التطبيق
    app_name: str = "المختار اللغوي الجديد"
    app_version: str = "2.0.0"
    app_author: str = "فريق التطوير"
    
    # إعدادات الملفات
    auto_save: bool = True
    auto_save_interval: int = 300  # 5 دقائق
    backup_enabled: bool = True
    backup_count: int = 5
    
    # إعدادات التحديث
    check_updates: bool = True
    update_channel: str = "stable"  # stable, beta, dev
    
    # إعدادات الخصوصية
    collect_analytics: bool = False
    send_crash_reports: bool = True


class SettingsManager:
    """مدير الإعدادات المتقدم"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        تهيئة مدير الإعدادات
        
        Args:
            config_file: مسار ملف الإعدادات
        """
        self.config_file = Path(config_file)
        self.settings = self._create_default_settings()
        self._load_settings()
    
    def _create_default_settings(self) -> Dict[str, Any]:
        """إنشاء الإعدادات الافتراضية"""
        return {
            'arabic_processing': asdict(ArabicProcessingSettings()),
            'performance': asdict(PerformanceSettings()),
            'logging': asdict(LoggingSettings()),
            'ui': asdict(UISettings()),
            'analysis': asdict(AnalysisSettings()),
            'database': asdict(DatabaseSettings()),
            'application': asdict(ApplicationSettings())
        }
    
    def _load_settings(self):
        """تحميل الإعدادات من الملف"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # دمج الإعدادات المحملة مع الافتراضية
                self._merge_settings(loaded_settings)
                
            except Exception as e:
                print(f"خطأ في تحميل الإعدادات: {e}")
                print("سيتم استخدام الإعدادات الافتراضية")
        else:
            # إنشاء ملف الإعدادات الافتراضي
            self.save_settings()
    
    def _merge_settings(self, loaded_settings: Dict[str, Any]):
        """دمج الإعدادات المحملة مع الافتراضية"""
        for category, settings in loaded_settings.items():
            if category in self.settings:
                if isinstance(settings, dict):
                    self.settings[category].update(settings)
                else:
                    self.settings[category] = settings
    
    def save_settings(self):
        """حفظ الإعدادات في الملف"""
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # تحويل Enum إلى قيم نصية قبل الحفظ
            serializable_settings = self._make_serializable(self.settings)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"خطأ في حفظ الإعدادات: {e}")
    
    def _make_serializable(self, obj):
        """تحويل الكائنات غير القابلة للتسلسل إلى قيم نصية"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return obj
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """
        الحصول على إعداد محدد
        
        Args:
            category: فئة الإعداد
            key: مفتاح الإعداد
            default: القيمة الافتراضية
            
        Returns:
            قيمة الإعداد
        """
        try:
            return self.settings.get(category, {}).get(key, default)
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, category: str, key: str, value: Any):
        """
        تعيين إعداد محدد
        
        Args:
            category: فئة الإعداد
            key: مفتاح الإعداد
            value: القيمة الجديدة
        """
        if category not in self.settings:
            self.settings[category] = {}
        
        self.settings[category][key] = value
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """
        الحصول على فئة إعدادات كاملة
        
        Args:
            category: فئة الإعدادات
            
        Returns:
            قاموس الإعدادات
        """
        return self.settings.get(category, {})
    
    def set_category(self, category: str, settings: Dict[str, Any]):
        """
        تعيين فئة إعدادات كاملة
        
        Args:
            category: فئة الإعدادات
            settings: الإعدادات الجديدة
        """
        self.settings[category] = settings
    
    def reset_to_defaults(self):
        """إعادة تعيين جميع الإعدادات للقيم الافتراضية"""
        self.settings = self._create_default_settings()
        self.save_settings()
    
    def export_settings(self, file_path: str):
        """
        تصدير الإعدادات إلى ملف
        
        Args:
            file_path: مسار الملف المستهدف
        """
        try:
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"خطأ في تصدير الإعدادات: {e}")
    
    def import_settings(self, file_path: str):
        """
        استيراد الإعدادات من ملف
        
        Args:
            file_path: مسار الملف المصدر
        """
        try:
            import_path = Path(file_path)
            
            if not import_path.exists():
                raise FileNotFoundError(f"الملف غير موجود: {file_path}")
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            self._merge_settings(imported_settings)
            self.save_settings()
            
        except Exception as e:
            print(f"خطأ في استيراد الإعدادات: {e}")
    
    def validate_settings(self) -> List[str]:
        """
        التحقق من صحة الإعدادات
        
        Returns:
            قائمة بالأخطاء إن وجدت
        """
        errors = []
        
        # التحقق من إعدادات الأداء
        perf_settings = self.get_category('performance')
        if perf_settings.get('cache_size', 0) < 0:
            errors.append("حجم التخزين المؤقت يجب أن يكون موجباً")
        
        if perf_settings.get('max_workers', 0) < 1:
            errors.append("عدد العمال يجب أن يكون أكبر من صفر")
        
        # التحقق من إعدادات التحليل
        analysis_settings = self.get_category('analysis')
        if analysis_settings.get('min_frequency', 0) < 0:
            errors.append("الحد الأدنى للتكرار يجب أن يكون موجباً")
        
        if analysis_settings.get('max_frequency', 0) < analysis_settings.get('min_frequency', 0):
            errors.append("الحد الأقصى للتكرار يجب أن يكون أكبر من الحد الأدنى")
        
        # التحقق من إعدادات الواجهة
        ui_settings = self.get_category('ui')
        if ui_settings.get('window_width', 0) < 400:
            errors.append("عرض النافذة يجب أن يكون أكبر من 400 بكسل")
        
        if ui_settings.get('window_height', 0) < 300:
            errors.append("ارتفاع النافذة يجب أن يكون أكبر من 300 بكسل")
        
        return errors
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """
        الحصول على ملخص الإعدادات
        
        Returns:
            ملخص الإعدادات
        """
        return {
            'total_categories': len(self.settings),
            'categories': list(self.settings.keys()),
            'validation_errors': len(self.validate_settings()),
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists()
        }


# إنشاء مثيل عام لمدير الإعدادات
settings_manager = SettingsManager()


def get_setting(category: str, key: str, default: Any = None) -> Any:
    """دالة مساعدة للحصول على إعداد"""
    return settings_manager.get_setting(category, key, default)


def set_setting(category: str, key: str, value: Any):
    """دالة مساعدة لتعيين إعداد"""
    settings_manager.set_setting(category, key, value)


def save_settings():
    """دالة مساعدة لحفظ الإعدادات"""
    settings_manager.save_settings()


def load_settings():
    """دالة مساعدة لتحميل الإعدادات"""
    settings_manager._load_settings()


# إعدادات سريعة للوصول
ARABIC_SETTINGS = settings_manager.get_category('arabic_processing')
PERFORMANCE_SETTINGS = settings_manager.get_category('performance')
LOGGING_SETTINGS = settings_manager.get_category('logging')
UI_SETTINGS = settings_manager.get_category('ui')
ANALYSIS_SETTINGS = settings_manager.get_category('analysis')
DATABASE_SETTINGS = settings_manager.get_category('database')
APPLICATION_SETTINGS = settings_manager.get_category('application')
