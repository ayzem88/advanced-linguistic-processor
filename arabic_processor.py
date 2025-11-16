"""
معالج اللغة العربية المتقدم - النسخة المحسنة
Advanced Arabic Language Processor - Enhanced Version
"""
import re
import logging
from collections import Counter
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import sys

# إضافة مسار utils للاستيراد
utils_path = Path(__file__).parent / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

try:
    from advanced_logger import AdvancedLogger, log_arabic_processing, log_function_call, error_handler
    from performance_optimizer import (
        main_cache, performance_optimizer, cached_arabic_processing, parallel_processing
    )
    from settings_manager import settings_manager, get_setting
    
    # إنشاء المسجل الرئيسي
    main_logger = AdvancedLogger("arabic_processor")
    
except ImportError:
    # إنشاء مسجل بسيط كبديل
    logging.basicConfig(level=logging.INFO)
    AdvancedLogger = logging.getLogger
    def log_arabic_processing(logger): return lambda func: func
    def log_function_call(logger): return lambda func: func
    def cached_arabic_processing(func): return func
    def parallel_processing(chunk_size=1000): return lambda func: func
    def get_setting(category, key, default=None): return default
    error_handler = None
    main_cache = None
    performance_optimizer = None
    settings_manager = None
    main_logger = logging.getLogger("arabic_processor")


class ArabicProcessor:
    """
    معالج متخصص للغة العربية مع دعم متقدم
    
    يوفر معالجة شاملة للنصوص العربية تشمل:
    - إزالة التشكيل وتوحيد الحروف
    - استخراج الجذور والتحليل الصرفي
    - إزالة كلمات الوقف
    - تحليل النصوص المتقدمة
    
    أمثلة:
        >>> processor = ArabicProcessor()
        >>> text = "اللّغة العربيّة جميلة"
        >>> normalized = processor.normalize_text(text)
        >>> print(normalized)
        اللغة العربية جميلة
        
        >>> words = processor.tokenize_advanced(text, remove_stop=True, stem=True)
        >>> print(words)
        ['لغة', 'عربي', 'جميل']
    """
    
    # أحرف التشكيل العربية
    TASHKEEL = re.compile(r'[\u064B-\u065F\u0670]')
    
    # حروف العلة
    HARAKAT = ['ً', 'ٌ', 'ٍ', 'َ', 'ُ', 'ِ', 'ّ', 'ْ', 'ـ']
    
    # أدوات التعريف والضمائر
    PREFIXES = ['ال', 'وال', 'فال', 'بال', 'كال', 'لل']
    SUFFIXES = ['ها', 'هم', 'هن', 'كم', 'كن', 'نا', 'ني', 'ك', 'ه', 'ي']
    
    # حروف الجر والعطف
    PARTICLES = ['في', 'من', 'إلى', 'على', 'عن', 'الى', 'و', 'ف', 'ب', 'ك', 'ل']
    
    # الضمائر
    PRONOUNS = ['هو', 'هي', 'هم', 'هن', 'أنا', 'أنت', 'أنتم', 'أنتن', 'نحن', 'أنتِ']
    
    # كلمات وقف شائعة
    STOP_WORDS = [
        'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
        'التي', 'الذي', 'التى', 'الذى', 'هو', 'هي', 'هم', 'هن', 'أن', 'إن',
        'كان', 'كانت', 'يكون', 'تكون', 'ليس', 'ليست', 'قد', 'لقد', 'قال',
        'كل', 'بعض', 'غير', 'سوى', 'بين', 'عند', 'لدى', 'أو', 'أم', 'لكن',
        'لكن', 'بل', 'حتى', 'كي', 'لكي', 'ما', 'ماذا', 'متى', 'أين', 'كيف'
    ]
    
    def __init__(self, logger: Optional[AdvancedLogger] = None):
        """
        تهيئة المعالج العربي
        
        Args:
            logger: مسجل مخصص، إذا لم يتم توفيره سيتم إنشاء مسجل افتراضي
        """
        self.logger = logger or AdvancedLogger("arabic_processor")
        self.logger.info("تم تهيئة المعالج العربي")
        
        # إحصائيات الأداء
        self.stats = {
            'texts_processed': 0,
            'words_tokenized': 0,
            'errors_handled': 0
        }
    
    @cached_arabic_processing
    @log_arabic_processing(main_logger)
    def remove_tashkeel(self, text: str) -> str:
        """
        إزالة التشكيل من النص العربي
        
        Args:
            text: النص العربي المراد إزالة التشكيل منه
            
        Returns:
            النص بدون تشكيل
        """
        if not text or not isinstance(text, str):
            return text  # إرجاع النص كما هو إذا كان فارغاً
        
        try:
            result = self.TASHKEEL.sub('', text)
            self.logger.debug(f"تم إزالة التشكيل من نص طوله {len(text)} حرف")
            return result
        except Exception as e:
            self.logger.error(f"خطأ في إزالة التشكيل", exception=e)
            return text  # إرجاع النص الأصلي في حالة الخطأ
    
    @log_arabic_processing(main_logger)
    def normalize_alef(self, text: str) -> str:
        """
        توحيد أشكال الألف في النص العربي
        
        Args:
            text: النص المراد توحيد أشكال الألف فيه
            
        Returns:
            النص مع توحيد أشكال الألف
        """
        if not text:
            return text
        
        try:
            result = re.sub('[إأآا]', 'ا', text)
            self.logger.debug(f"تم توحيد أشكال الألف في نص طوله {len(text)} حرف")
            return result
        except Exception as e:
            self.logger.error(f"خطأ في توحيد أشكال الألف", exception=e)
            raise
    
    @log_arabic_processing(main_logger)
    def normalize_hamza(self, text: str) -> str:
        """
        توحيد أشكال الهمزة في النص العربي
        
        Args:
            text: النص المراد توحيد أشكال الهمزة فيه
            
        Returns:
            النص مع توحيد أشكال الهمزة
        """
        if not text:
            return text
        
        try:
            result = re.sub('[ؤئ]', 'ء', text)
            self.logger.debug(f"تم توحيد أشكال الهمزة في نص طوله {len(text)} حرف")
            return result
        except Exception as e:
            self.logger.error(f"خطأ في توحيد أشكال الهمزة", exception=e)
            raise
    
    @log_arabic_processing(main_logger)
    def normalize_yaa(self, text: str) -> str:
        """
        توحيد الياء والألف المقصورة في النص العربي
        
        Args:
            text: النص المراد توحيد الياء والألف المقصورة فيه
            
        Returns:
            النص مع توحيد الياء والألف المقصورة
        """
        if not text:
            return text
        
        try:
            result = re.sub('[ىي]', 'ي', text)
            self.logger.debug(f"تم توحيد الياء والألف المقصورة في نص طوله {len(text)} حرف")
            return result
        except Exception as e:
            self.logger.error(f"خطأ في توحيد الياء والألف المقصورة", exception=e)
            raise
    
    @log_arabic_processing(main_logger)
    def normalize_taa(self, text: str) -> str:
        """
        توحيد التاء المربوطة والهاء في النص العربي
        
        Args:
            text: النص المراد توحيد التاء المربوطة والهاء فيه
            
        Returns:
            النص مع توحيد التاء المربوطة والهاء
        """
        if not text:
            return text
        
        try:
            result = re.sub('ة', 'ه', text)
            self.logger.debug(f"تم توحيد التاء المربوطة والهاء في نص طوله {len(text)} حرف")
            return result
        except Exception as e:
            self.logger.error(f"خطأ في توحيد التاء المربوطة والهاء", exception=e)
            raise
    
    @cached_arabic_processing
    @log_arabic_processing(main_logger)
    def normalize_text(self, text: str) -> str:
        """
        تطبيع النص العربي الكامل
        
        يطبق جميع عمليات التطبيع على النص حسب الإعدادات:
        - إزالة التشكيل
        - توحيد أشكال الألف
        - توحيد أشكال الهمزة
        - توحيد الياء والألف المقصورة
        
        Args:
            text: النص العربي المراد تطبيعه
            
        Returns:
            النص المطبع بالكامل
        """
        if not text or not isinstance(text, str):
            return text  # إرجاع النص كما هو إذا كان فارغاً
        
        try:
            # تطبيق عمليات التطبيع حسب الإعدادات
            result = text
            
            # إزالة التشكيل إذا كان مفعلاً
            if get_setting('arabic_processing', 'remove_tashkeel', True):
                result = self.remove_tashkeel(result)
            
            # توحيد أشكال الألف إذا كان مفعلاً
            if get_setting('arabic_processing', 'normalize_alef', True):
                result = self.normalize_alef(result)
            
            # توحيد أشكال الهمزة إذا كان مفعلاً
            if get_setting('arabic_processing', 'normalize_hamza', True):
                result = self.normalize_hamza(result)
            
            # توحيد الياء والألف المقصورة إذا كان مفعلاً
            if get_setting('arabic_processing', 'normalize_yaa', True):
                result = self.normalize_yaa(result)
            
            # توحيد التاء المربوطة والهاء إذا كان مفعلاً
            if get_setting('arabic_processing', 'normalize_taa', False):
                result = self.normalize_taa(result)
            
            self.stats['texts_processed'] += 1
            self.logger.info(f"تم تطبيع نص طوله {len(text)} حرف")
            return result
            
        except Exception as e:
            self.stats['errors_handled'] += 1
            self.logger.error(f"خطأ في تطبيع النص", exception=e)
            return text  # إرجاع النص الأصلي في حالة الخطأ
    
    def remove_al_prefix(self, word):
        """إزالة ال التعريف"""
        for prefix in self.PREFIXES:
            if word.startswith(prefix):
                return word[len(prefix):]
        return word
    
    def remove_prefixes(self, word):
        """إزالة البادئات الشائعة"""
        for prefix in ['و', 'ف', 'ب', 'ك', 'ل']:
            if word.startswith(prefix) and len(word) > 2:
                word = word[1:]
                break
        return self.remove_al_prefix(word)
    
    def remove_suffixes(self, word):
        """إزالة اللواحق الشائعة"""
        for suffix in self.SUFFIXES:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        return word
    
    def light_stem(self, word):
        """استخراج جذر تقريبي للكلمة (light stemming)"""
        word = self.normalize_text(word)
        word = self.remove_prefixes(word)
        word = self.remove_suffixes(word)
        return word
    
    def is_arabic(self, text):
        """التحقق من كون النص عربياً"""
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(arabic_pattern.search(text))
    
    def extract_arabic_words(self, text):
        """استخراج الكلمات العربية فقط"""
        text = self.remove_tashkeel(text)
        words = re.findall(r'[\u0600-\u06FF]+', text)
        return words
    
    def remove_stop_words(self, words):
        """إزالة كلمات الوقف"""
        return [w for w in words if w not in self.STOP_WORDS]
    
    def count_arabic_chars(self, text):
        """عد الحروف العربية"""
        return len(re.findall(r'[\u0600-\u06FF]', text))
    
    @parallel_processing(chunk_size=500)
    @cached_arabic_processing
    @log_arabic_processing(main_logger)
    def tokenize_advanced(self, text: str, remove_stop: bool = None, stem: bool = None) -> List[str]:
        """
        تقسيم متقدم للنص العربي مع خيارات معالجة
        
        Args:
            text: النص العربي المراد تقسيمه
            remove_stop: إزالة كلمات الوقف (إذا لم يتم تحديده، سيستخدم الإعدادات)
            stem: استخراج الجذور (إذا لم يتم تحديده، سيستخدم الإعدادات)
            
        Returns:
            قائمة بالكلمات المعالجة
            
        Raises:
            ValueError: إذا كان النص فارغاً أو غير صالح
        """
        if not text or not isinstance(text, str):
            raise ValueError("النص يجب أن يكون سلسلة نصية غير فارغة")
        
        try:
            # استخدام الإعدادات إذا لم يتم تحديد القيم
            if remove_stop is None:
                remove_stop = get_setting('arabic_processing', 'remove_stop_words', True)
            
            if stem is None:
                stem = get_setting('arabic_processing', 'enable_stemming', True)
            
            # إزالة التشكيل
            text = self.remove_tashkeel(text)
            
            # استخراج الكلمات العربية فقط
            words = self.extract_arabic_words(text)
            
            # تطبيع الكلمات
            words = [self.normalize_text(w) for w in words]
            
            # فلترة الكلمات حسب الطول
            min_length = get_setting('arabic_processing', 'min_word_length', 2)
            max_length = get_setting('arabic_processing', 'max_word_length', 50)
            words = [w for w in words if min_length <= len(w) <= max_length]
            
            # إزالة كلمات الوقف إذا طلب
            if remove_stop:
                words = self.remove_stop_words(words)
                
                # إضافة كلمات وقف مخصصة إذا كانت موجودة
                custom_stop_words = get_setting('arabic_processing', 'custom_stop_words', [])
                if custom_stop_words:
                    words = [w for w in words if w not in custom_stop_words]
            
            # استخراج الجذور إذا طلب
            if stem:
                stemming_algorithm = get_setting('arabic_processing', 'stemming_algorithm', 'light')
                if stemming_algorithm == 'light':
                    words = [self.light_stem(w) for w in words]
                # يمكن إضافة خوارزميات أخرى هنا
            
            self.stats['words_tokenized'] += len(words)
            self.logger.info(f"تم تقسيم النص إلى {len(words)} كلمة")
            
            return words
            
        except Exception as e:
            self.stats['errors_handled'] += 1
            self.logger.error(f"خطأ في تقسيم النص المتقدم", exception=e)
            raise
    
    def get_word_info(self, word: str) -> Dict[str, Any]:
        """
        معلومات شاملة عن الكلمة العربية
        
        Args:
            word: الكلمة المراد تحليلها
            
        Returns:
            قاموس يحتوي على معلومات الكلمة
        """
        if not word:
            return {}
        
        try:
            info = {
                'أصلية': word,
                'بدون تشكيل': self.remove_tashkeel(word),
                'مطبعة': self.normalize_text(word),
                'جذر تقريبي': self.light_stem(word),
                'عربية': self.is_arabic(word),
                'طول': len(word),
                'طول بدون تشكيل': len(self.remove_tashkeel(word))
            }
            return info
        except Exception as e:
            self.logger.error(f"خطأ في تحليل معلومات الكلمة '{word}'", exception=e)
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الأداء
        
        Returns:
            قاموس يحتوي على إحصائيات الأداء
        """
        return {
            'texts_processed': self.stats['texts_processed'],
            'words_tokenized': self.stats['words_tokenized'],
            'errors_handled': self.stats['errors_handled'],
            'stop_words_count': len(self.STOP_WORDS),
            'prefixes_count': len(self.PREFIXES),
            'suffixes_count': len(self.SUFFIXES)
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الأداء الشاملة
        
        Returns:
            قاموس يحتوي على إحصائيات الأداء والتخزين المؤقت
        """
        stats = self.get_stats()
        
        # إضافة إحصائيات التخزين المؤقت إذا كان متاحاً
        if main_cache:
            cache_stats = main_cache.get_stats()
            stats['cache'] = cache_stats
        
        # إضافة إحصائيات محسن الأداء إذا كان متاحاً
        if performance_optimizer:
            perf_stats = performance_optimizer.get_stats()
            stats['performance'] = perf_stats
        
        return stats
    
    def cleanup_resources(self):
        """تنظيف الموارد وإغلاق الاتصالات"""
        if performance_optimizer:
            performance_optimizer.cleanup()
        
        if main_cache:
            # يمكن إضافة تنظيف إضافي للتخزين المؤقت هنا
            pass
        
        self.logger.info("تم تنظيف الموارد")

