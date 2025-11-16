"""
اختبارات شاملة للمعالج اللغوي العربي
Comprehensive Tests for Arabic Linguistic Processor
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
import time
import threading
from unittest.mock import patch, MagicMock

# إضافة مسار المشروع للاستيراد
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from arabic_processor import ArabicProcessor
    from utils.advanced_logger import AdvancedLogger, ErrorHandler
    from utils.performance_optimizer import AdvancedCache, PerformanceOptimizer
except ImportError as e:
    print(f"خطأ في استيراد الوحدات: {e}")
    sys.exit(1)


class TestArabicProcessor(unittest.TestCase):
    """اختبارات شاملة للمعالج العربي"""
    
    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        self.processor = ArabicProcessor()
        
        # نصوص اختبار متنوعة
        self.test_texts = {
            'simple': "اللغة العربية جميلة",
            'with_tashkeel': "اللُّغة العَرَبِيَّة جَمِيلَةٌ",
            'mixed_encoding': "اللغة العربية واللغة الإنجليزية",
            'long_text': " ".join(["اللغة العربية"] * 100),
            'special_chars': "اللغة العربية: جميلة! (ممتازة)",
            'numbers': "اللغة العربية 123 جميلة 456",
            'empty': "",
            'whitespace': "   اللغة العربية   ",
            'newlines': "اللغة العربية\nجميلة\nوممتازة"
        }
    
    def test_remove_tashkeel(self):
        """اختبار إزالة التشكيل"""
        test_cases = [
            ("اللُّغة العَرَبِيَّة", "اللغة العربية"),
            ("كِتَابٌ جَمِيلٌ", "كتاب جميل"),
            ("مُدَرِّسٌ", "مدرس"),
            ("", ""),
            ("بدون تشكيل", "بدون تشكيل")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.remove_tashkeel(input_text)
                self.assertEqual(result, expected)
    
    def test_normalize_alef(self):
        """اختبار توحيد أشكال الألف"""
        test_cases = [
            ("إسلام", "اسلام"),
            ("أحمد", "احمد"),
            ("آمن", "امن"),
            ("اللغة", "اللغة"),  # الألف العادية لا تتغير
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.normalize_alef(input_text)
                self.assertEqual(result, expected)
    
    def test_normalize_hamza(self):
        """اختبار توحيد أشكال الهمزة"""
        test_cases = [
            ("سؤال", "سءال"),
            ("مؤمن", "مءمن"),
            ("بدون همزة", "بدون همزة"),
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.normalize_hamza(input_text)
                self.assertEqual(result, expected)
    
    def test_normalize_yaa(self):
        """اختبار توحيد الياء والألف المقصورة"""
        test_cases = [
            ("مستشفى", "مستشفي"),
            ("على", "علي"),
            ("بيت", "بيت"),  # الياء العادية لا تتغير
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.normalize_yaa(input_text)
                self.assertEqual(result, expected)
    
    def test_normalize_taa(self):
        """اختبار توحيد التاء المربوطة والهاء"""
        test_cases = [
            ("مدرسة", "مدرسه"),
            ("كتابة", "كتابه"),
            ("بيت", "بيت"),  # الهاء العادية لا تتغير
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.normalize_taa(input_text)
                self.assertEqual(result, expected)
    
    def test_normalize_text(self):
        """اختبار التطبيع الكامل للنص"""
        test_cases = [
            ("اللُّغة العَرَبِيَّة", "اللغة العربية"),
            ("إِسْلامٌ جَمِيلٌ", "اسلام جميل"),
            ("مُدَرِّسَةٌ", "مدرسه"),
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.normalize_text(input_text)
                self.assertEqual(result, expected)
    
    def test_extract_arabic_words(self):
        """اختبار استخراج الكلمات العربية"""
        test_cases = [
            ("اللغة العربية جميلة", ["اللغة", "العربية", "جميلة"]),
            ("اللغة العربية 123 جميلة", ["اللغة", "العربية", "جميلة"]),
            ("", []),
            ("123 456", []),
            ("اللغة العربية: جميلة!", ["اللغة", "العربية", "جميلة"])
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.extract_arabic_words(input_text)
                self.assertEqual(result, expected)
    
    def test_remove_stop_words(self):
        """اختبار إزالة كلمات الوقف"""
        test_cases = [
            (["اللغة", "في", "العربية", "جميلة"], ["اللغة", "العربية", "جميلة"]),
            (["هذا", "كتاب", "جميل"], ["كتاب", "جميل"]),
            ([], []),
            (["اللغة", "العربية"], ["اللغة", "العربية"])  # لا توجد كلمات وقف
        ]
        
        for input_words, expected in test_cases:
            with self.subTest(input_words=input_words):
                result = self.processor.remove_stop_words(input_words)
                self.assertEqual(result, expected)
    
    def test_light_stem(self):
        """اختبار استخراج الجذور الخفيف"""
        test_cases = [
            ("الكتاب", "كتاب"),
            ("الكتابة", "كتابه"),
            ("مدرسة", "مدرسه"),
            ("", ""),
            ("كتاب", "كتاب")  # بدون بادئة
        ]
        
        for input_word, expected in test_cases:
            with self.subTest(input_word=input_word):
                result = self.processor.light_stem(input_word)
                self.assertEqual(result, expected)
    
    def test_tokenize_advanced(self):
        """اختبار التقسيم المتقدم"""
        text = "اللُّغة العَرَبِيَّة جَمِيلَةٌ"
        
        # اختبار بدون خيارات
        result1 = self.processor.tokenize_advanced(text)
        self.assertIsInstance(result1, list)
        self.assertTrue(len(result1) > 0)
        
        # اختبار مع إزالة كلمات الوقف
        result2 = self.processor.tokenize_advanced(text, remove_stop=True)
        self.assertIsInstance(result2, list)
        
        # اختبار مع استخراج الجذور
        result3 = self.processor.tokenize_advanced(text, stem=True)
        self.assertIsInstance(result3, list)
        
        # اختبار مع جميع الخيارات
        result4 = self.processor.tokenize_advanced(text, remove_stop=True, stem=True)
        self.assertIsInstance(result4, list)
    
    def test_is_arabic(self):
        """اختبار التحقق من النص العربي"""
        test_cases = [
            ("اللغة العربية", True),
            ("Hello World", False),
            ("اللغة العربية 123", True),  # مختلط يعتبر عربي
            ("", False),
            ("123", False),
            ("اللغة العربية Hello", True)  # مختلط يعتبر عربي
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.is_arabic(input_text)
                self.assertEqual(result, expected)
    
    def test_count_arabic_chars(self):
        """اختبار عد الحروف العربية"""
        test_cases = [
            ("اللغة العربية", 12),
            ("Hello World", 0),
            ("اللغة العربية 123", 12),
            ("", 0),
            ("123", 0)
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.processor.count_arabic_chars(input_text)
                self.assertEqual(result, expected)
    
    def test_get_word_info(self):
        """اختبار معلومات الكلمة"""
        word = "الكتاب"
        info = self.processor.get_word_info(word)
        
        self.assertIsInstance(info, dict)
        self.assertIn('أصلية', info)
        self.assertIn('بدون تشكيل', info)
        self.assertIn('مطبعة', info)
        self.assertIn('جذر تقريبي', info)
        self.assertIn('عربية', info)
        self.assertIn('طول', info)
        
        self.assertEqual(info['أصلية'], word)
        self.assertTrue(info['عربية'])
        self.assertGreater(info['طول'], 0)
    
    def test_get_stats(self):
        """اختبار الإحصائيات"""
        stats = self.processor.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('texts_processed', stats)
        self.assertIn('words_tokenized', stats)
        self.assertIn('errors_handled', stats)
        self.assertIn('stop_words_count', stats)
        self.assertIn('prefixes_count', stats)
        self.assertIn('suffixes_count', stats)
        
        # التحقق من أن القيم رقمية
        for key, value in stats.items():
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 0)
    
    def test_error_handling(self):
        """اختبار معالجة الأخطاء"""
        # اختبار النص الفارغ
        with self.assertRaises(ValueError):
            self.processor.normalize_text("")
        
        with self.assertRaises(ValueError):
            self.processor.normalize_text(None)
        
        # اختبار النص غير الصالح
        with self.assertRaises(ValueError):
            self.processor.tokenize_advanced("")
        
        with self.assertRaises(ValueError):
            self.processor.tokenize_advanced(None)
    
    def test_performance_stats(self):
        """اختبار إحصائيات الأداء"""
        stats = self.processor.get_performance_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('texts_processed', stats)
        self.assertIn('words_tokenized', stats)
        self.assertIn('errors_handled', stats)
    
    def test_concurrent_access(self):
        """اختبار الوصول المتزامن"""
        def process_text(text):
            return self.processor.normalize_text(text)
        
        # اختبار معالجة متزامنة لنفس النص
        text = "اللغة العربية جميلة"
        threads = []
        results = []
        
        def worker():
            result = process_text(text)
            results.append(result)
        
        # إنشاء عدة خيوط
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # انتظار انتهاء جميع الخيوط
        for thread in threads:
            thread.join()
        
        # التحقق من أن جميع النتائج متطابقة
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertEqual(result, results[0])


class TestAdvancedLogger(unittest.TestCase):
    """اختبارات نظام التسجيل المتقدم"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = AdvancedLogger("test_logger", self.temp_dir)
    
    def tearDown(self):
        """تنظيف البيئة"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """اختبار تهيئة المسجل"""
        self.assertIsNotNone(self.logger)
        self.assertEqual(self.logger.name, "test_logger")
    
    def test_logging_levels(self):
        """اختبار مستويات التسجيل المختلفة"""
        # اختبار التسجيل بدون أخطاء
        self.logger.debug("رسالة تشخيصية")
        self.logger.info("رسالة معلوماتية")
        self.logger.warning("رسالة تحذير")
        self.logger.error("رسالة خطأ")
        self.logger.critical("رسالة حرجة")
        
        # اختبار التسجيل مع استثناء
        try:
            raise ValueError("خطأ تجريبي")
        except ValueError as e:
            self.logger.error("خطأ في الاختبار", exception=e)
    
    def test_performance_logging(self):
        """اختبار تسجيل الأداء"""
        self.logger.performance("test_operation", 1.5, {"items": 100})
    
    def test_arabic_text_logging(self):
        """اختبار تسجيل النصوص العربية"""
        self.logger.arabic_text("normalize", "اللغة العربية", "اللغة العربية")


class TestAdvancedCache(unittest.TestCase):
    """اختبارات نظام التخزين المؤقت المتقدم"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = AdvancedCache(self.temp_dir, max_size=10, ttl=1)
    
    def tearDown(self):
        """تنظيف البيئة"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_initialization(self):
        """اختبار تهيئة التخزين المؤقت"""
        self.assertIsNotNone(self.cache)
        self.assertEqual(self.cache.max_size, 10)
        self.assertEqual(self.cache.ttl, 1)
    
    def test_cache_set_get(self):
        """اختبار حفظ واسترجاع البيانات"""
        key = "test_key"
        data = "test_data"
        
        # حفظ البيانات
        self.cache.set(key, data)
        
        # استرجاع البيانات
        result = self.cache.get(key)
        self.assertEqual(result, data)
    
    def test_cache_expiration(self):
        """اختبار انتهاء صلاحية البيانات"""
        key = "expired_key"
        data = "expired_data"
        
        # حفظ البيانات
        self.cache.set(key, data)
        
        # انتظار انتهاء الصلاحية
        time.sleep(2)
        
        # محاولة استرجاع البيانات المنتهية الصلاحية
        result = self.cache.get(key)
        self.assertIsNone(result)
    
    def test_cache_eviction(self):
        """اختبار إزالة العناصر عند الوصول للحد الأقصى"""
        # ملء التخزين المؤقت
        for i in range(15):  # أكثر من الحد الأقصى (10)
            self.cache.set(f"key_{i}", f"data_{i}")
        
        # التحقق من أن بعض العناصر تم إزالتها
        self.assertLessEqual(len(self.cache.memory_cache), 10)
    
    def test_cache_stats(self):
        """اختبار إحصائيات التخزين المؤقت"""
        # إجراء بعض العمليات
        self.cache.set("key1", "data1")
        self.cache.get("key1")  # hit
        self.cache.get("key2")  # miss
        
        stats = self.cache.get_stats()
        
        self.assertIn('hit_rate', stats)
        self.assertIn('memory_items', stats)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
    
    def test_cache_clear(self):
        """اختبار مسح التخزين المؤقت"""
        # إضافة بعض البيانات
        self.cache.set("key1", "data1")
        self.cache.set("key2", "data2")
        
        # مسح التخزين المؤقت
        self.cache.clear()
        
        # التحقق من أن البيانات تم حذفها
        self.assertEqual(len(self.cache.memory_cache), 0)
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))


class TestPerformanceOptimizer(unittest.TestCase):
    """اختبارات محسن الأداء"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.optimizer = PerformanceOptimizer(max_workers=2)
    
    def test_optimizer_initialization(self):
        """اختبار تهيئة محسن الأداء"""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.max_workers, 2)
    
    def test_split_text_into_chunks(self):
        """اختبار تقسيم النص إلى أجزاء"""
        text = " ".join(["كلمة"] * 10)
        chunks = self.optimizer.split_text_into_chunks(text, chunk_size=3)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 1)
        
        # التحقق من أن مجموع الكلمات في الأجزاء يساوي النص الأصلي
        total_words = sum(len(chunk.split()) for chunk in chunks)
        self.assertEqual(total_words, 10)
    
    def test_process_text_parallel(self):
        """اختبار المعالجة المتوازية للنص"""
        def simple_processor(text):
            return text.split()
        
        text = " ".join(["كلمة"] * 20)
        result = self.optimizer.process_text_parallel(text, simple_processor, chunk_size=5)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 20)  # 20 كلمة
    
    def test_batch_process(self):
        """اختبار المعالجة المتوازية لمجموعة نصوص"""
        def simple_processor(text):
            return len(text.split())
        
        texts = ["كلمة واحدة", "كلمتان اثنتان", "ثلاث كلمات هنا"]
        results = self.optimizer.batch_process(texts, simple_processor)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results, [1, 2, 3])
    
    def test_performance_stats(self):
        """اختبار إحصائيات الأداء"""
        stats = self.optimizer.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('parallel_operations', stats)
        self.assertIn('texts_processed', stats)
        self.assertIn('total_time_saved', stats)
        self.assertIn('max_workers', stats)
    
    def test_cleanup(self):
        """اختبار تنظيف الموارد"""
        # يجب ألا يسبب خطأ
        self.optimizer.cleanup()


class TestIntegration(unittest.TestCase):
    """اختبارات التكامل الشاملة"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.processor = ArabicProcessor()
    
    def test_full_processing_pipeline(self):
        """اختبار خط المعالجة الكامل"""
        text = "اللُّغة العَرَبِيَّة جَمِيلَةٌ وَمُفِيدَةٌ"
        
        # خط المعالجة الكامل
        normalized = self.processor.normalize_text(text)
        words = self.processor.extract_arabic_words(normalized)
        filtered_words = self.processor.remove_stop_words(words)
        stemmed_words = [self.processor.light_stem(word) for word in filtered_words]
        
        # التحقق من النتائج
        self.assertIsInstance(normalized, str)
        self.assertIsInstance(words, list)
        self.assertIsInstance(filtered_words, list)
        self.assertIsInstance(stemmed_words, list)
        
        # التحقق من أن النص المطبع لا يحتوي على تشكيل
        self.assertNotIn('ُ', normalized)
        self.assertNotIn('َ', normalized)
        self.assertNotIn('ِ', normalized)
    
    def test_large_text_processing(self):
        """اختبار معالجة النصوص الكبيرة"""
        # إنشاء نص كبير
        large_text = " ".join(["اللغة العربية جميلة ومفيدة"] * 1000)
        
        # معالجة النص
        start_time = time.time()
        result = self.processor.tokenize_advanced(large_text, remove_stop=True, stem=True)
        processing_time = time.time() - start_time
        
        # التحقق من النتائج
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertLess(processing_time, 10)  # يجب أن يكون سريعاً
    
    def test_error_recovery(self):
        """اختبار استعادة الأخطاء"""
        # اختبار معالجة نص صالح بعد خطأ
        try:
            self.processor.normalize_text("")  # يجب أن يسبب خطأ
        except ValueError:
            pass
        
        # اختبار معالجة نص صالح
        result = self.processor.normalize_text("اللغة العربية")
        self.assertEqual(result, "اللغة العربية")


def run_performance_tests():
    """تشغيل اختبارات الأداء"""
    print("تشغيل اختبارات الأداء...")
    
    processor = ArabicProcessor()
    
    # اختبار سرعة إزالة التشكيل
    text_with_tashkeel = "اللُّغة العَرَبِيَّة جَمِيلَةٌ وَمُفِيدَةٌ"
    start_time = time.time()
    
    for _ in range(1000):
        processor.remove_tashkeel(text_with_tashkeel)
    
    tashkeel_time = time.time() - start_time
    print(f"إزالة التشكيل (1000 مرة): {tashkeel_time:.3f} ثانية")
    
    # اختبار سرعة التطبيع
    start_time = time.time()
    
    for _ in range(1000):
        processor.normalize_text(text_with_tashkeel)
    
    normalize_time = time.time() - start_time
    print(f"التطبيع (1000 مرة): {normalize_time:.3f} ثانية")
    
    # اختبار سرعة التقسيم المتقدم
    start_time = time.time()
    
    for _ in range(100):
        processor.tokenize_advanced(text_with_tashkeel, remove_stop=True, stem=True)
    
    tokenize_time = time.time() - start_time
    print(f"التقسيم المتقدم (100 مرة): {tokenize_time:.3f} ثانية")
    
    # طباعة إحصائيات الأداء
    stats = processor.get_performance_stats()
    print(f"\nإحصائيات الأداء:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    # تشغيل الاختبارات
    print("بدء الاختبارات الشاملة للمعالج اللغوي العربي...")
    
    # إنشاء مجموعة اختبارات
    test_suite = unittest.TestSuite()
    
    # إضافة اختبارات الوحدات
    test_suite.addTest(unittest.makeSuite(TestArabicProcessor))
    test_suite.addTest(unittest.makeSuite(TestAdvancedLogger))
    test_suite.addTest(unittest.makeSuite(TestAdvancedCache))
    test_suite.addTest(unittest.makeSuite(TestPerformanceOptimizer))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # طباعة النتائج
    print(f"\nنتائج الاختبارات:")
    print(f"الاختبارات المنجزة: {result.testsRun}")
    print(f"الأخطاء: {len(result.errors)}")
    print(f"الفشل: {len(result.failures)}")
    
    if result.errors:
        print("\nالأخطاء:")
        for test, error in result.errors:
            print(f"  {test}: {error}")
    
    if result.failures:
        print("\nالفشل:")
        for test, failure in result.failures:
            print(f"  {test}: {failure}")
    
    # تشغيل اختبارات الأداء
    print("\n" + "="*50)
    run_performance_tests()
    
    print("\nانتهت الاختبارات الشاملة!")
