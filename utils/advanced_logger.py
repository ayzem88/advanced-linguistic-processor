"""
نظام تسجيل الأخطاء المتقدم للمعالج اللغوي
Advanced Logging System for Linguistic Processor
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import traceback
import functools


class AdvancedLogger:
    """نظام تسجيل متقدم مع دعم متعدد المستويات"""
    
    def __init__(self, name: str = "linguistic_processor", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # إعداد المسجلات
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # منع تكرار المسجلات
        if self.logger.handlers:
            return
            
        self._setup_handlers()
        self._setup_formatters()
    
    def _setup_handlers(self):
        """إعداد معالجات التسجيل المختلفة"""
        
        # معالج الملف الرئيسي
        main_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # معالج الأخطاء
        error_file = self.log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # معالج وحدة التحكم
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # إضافة المعالجات
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        
        # حفظ المراجع للمعالجات
        self.handlers = {
            'file': file_handler,
            'error': error_handler,
            'console': console_handler
        }
    
    def _setup_formatters(self):
        """إعداد تنسيقات التسجيل"""
        
        # تنسيق مفصل للملفات
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # تنسيق مبسط للوحدة
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # تطبيق التنسيقات
        self.handlers['file'].setFormatter(detailed_formatter)
        self.handlers['error'].setFormatter(detailed_formatter)
        self.handlers['console'].setFormatter(simple_formatter)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """تسجيل رسالة تشخيصية"""
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """تسجيل رسالة معلوماتية"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """تسجيل تحذير"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exception: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None):
        """تسجيل خطأ مع تفاصيل إضافية"""
        if exception:
            message = f"{message} | Exception: {str(exception)}"
            self.logger.error(message, extra=extra, exc_info=True)
        else:
            self.logger.error(message, extra=extra)
    
    def critical(self, message: str, exception: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None):
        """تسجيل خطأ حرج"""
        if exception:
            message = f"{message} | Exception: {str(exception)}"
            self.logger.critical(message, extra=extra, exc_info=True)
        else:
            self.logger.critical(message, extra=extra)
    
    def performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """تسجيل معلومات الأداء"""
        message = f"Performance | {operation} took {duration:.3f}s"
        if details:
            message += f" | Details: {details}"
        self.logger.info(message, extra={'type': 'performance'})
    
    def arabic_text(self, operation: str, text: str, result: Optional[str] = None):
        """تسجيل عمليات النصوص العربية"""
        message = f"Arabic Text | {operation} | Input: {text[:50]}..."
        if result:
            message += f" | Output: {result[:50]}..."
        self.logger.debug(message, extra={'type': 'arabic_text'})


def log_function_call(logger: AdvancedLogger):
    """ديكوراتور لتسجيل استدعاءات الدوال"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.debug(f"Calling {func.__name__} with args: {len(args)}, kwargs: {list(kwargs.keys())}")
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.performance(f"{func.__name__}", duration)
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"Error in {func.__name__} after {duration:.3f}s", exception=e)
                raise
        return wrapper
    return decorator


def log_arabic_processing(logger: AdvancedLogger):
    """ديكوراتور لتسجيل معالجة النصوص العربية"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # البحث عن النص العربي في المعاملات
            text_arg = None
            for arg in args:
                if isinstance(arg, str) and any('\u0600' <= char <= '\u06FF' for char in arg):
                    text_arg = arg
                    break
            
            if text_arg:
                logger.arabic_text(func.__name__, text_arg)
            
            try:
                result = func(*args, **kwargs)
                if text_arg and result:
                    logger.arabic_text(func.__name__, text_arg, str(result))
                return result
            except Exception as e:
                logger.error(f"Arabic processing error in {func.__name__}", exception=e)
                raise
        return wrapper
    return decorator


class ErrorHandler:
    """معالج أخطاء متقدم مع استراتيجيات مختلفة"""
    
    def __init__(self, logger: AdvancedLogger):
        self.logger = logger
        self.error_counts: Dict[str, int] = {}
        self.max_retries = 3
    
    def handle_file_error(self, operation: str, file_path: str, exception: Exception) -> bool:
        """معالجة أخطاء الملفات"""
        error_key = f"file_{operation}_{type(exception).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        if self.error_counts[error_key] > self.max_retries:
            self.logger.critical(f"Max retries exceeded for {operation} on {file_path}", exception=exception)
            return False
        
        self.logger.error(f"File operation failed: {operation} on {file_path}", exception=exception)
        return True
    
    def handle_encoding_error(self, file_path: str, exception: Exception) -> bool:
        """معالجة أخطاء الترميز"""
        self.logger.error(f"Encoding error in {file_path}", exception=exception)
        return True
    
    def handle_xml_error(self, file_path: str, exception: Exception) -> bool:
        """معالجة أخطاء XML"""
        self.logger.error(f"XML parsing error in {file_path}", exception=exception)
        return True
    
    def handle_arabic_processing_error(self, operation: str, text: str, exception: Exception) -> bool:
        """معالجة أخطاء معالجة العربية"""
        self.logger.error(f"Arabic processing error in {operation}", exception=exception)
        self.logger.arabic_text(f"Failed {operation}", text[:100])
        return True


# إنشاء مثيل عام للمسجل
main_logger = AdvancedLogger("linguistic_processor")
error_handler = ErrorHandler(main_logger)
