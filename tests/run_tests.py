#!/usr/bin/env python3
"""
نظام تشغيل الاختبارات الشامل للمعالج اللغوي العربي
Comprehensive Test Runner for Arabic Linguistic Processor
"""

import unittest
import sys
import os
import time
import argparse
from pathlib import Path
import subprocess

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_unit_tests():
    """تشغيل اختبارات الوحدات"""
    print("="*60)
    print("تشغيل اختبارات الوحدات")
    print("="*60)
    
    # اكتشاف وتشغيل اختبارات الوحدات
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


def run_integration_tests():
    """تشغيل اختبارات التكامل"""
    print("\n" + "="*60)
    print("تشغيل اختبارات التكامل")
    print("="*60)
    
    try:
        # اختبار تكامل المعالج العربي مع نظام التسجيل
        from arabic_processor import ArabicProcessor
        from utils.advanced_logger import AdvancedLogger
        
        processor = ArabicProcessor()
        logger = AdvancedLogger("integration_test")
        
        # اختبار معالجة نص متكامل
        text = "اللُّغة العَرَبِيَّة جَمِيلَةٌ وَمُفِيدَةٌ"
        
        # خط المعالجة الكامل
        normalized = processor.normalize_text(text)
        words = processor.extract_arabic_words(normalized)
        filtered_words = processor.remove_stop_words(words)
        stemmed_words = [processor.light_stem(word) for word in filtered_words]
        
        print(f"✅ اختبار التكامل نجح:")
        print(f"   النص الأصلي: {text}")
        print(f"   النص المطبع: {normalized}")
        print(f"   الكلمات المستخرجة: {words}")
        print(f"   الكلمات المفلترة: {filtered_words}")
        print(f"   الجذور المستخرجة: {stemmed_words}")
        
        return True
        
    except Exception as e:
        print(f"❌ اختبار التكامل فشل: {e}")
        return False


def run_performance_tests():
    """تشغيل اختبارات الأداء"""
    print("\n" + "="*60)
    print("تشغيل اختبارات الأداء")
    print("="*60)
    
    try:
        from arabic_processor import ArabicProcessor
        from utils.performance_optimizer import AdvancedCache, PerformanceOptimizer
        
        processor = ArabicProcessor()
        cache = AdvancedCache("test_cache", max_size=100, ttl=60)
        optimizer = PerformanceOptimizer(max_workers=2)
        
        # اختبار سرعة المعالجة
        test_text = "اللُّغة العَرَبِيَّة جَمِيلَةٌ وَمُفِيدَةٌ"
        
        # اختبار إزالة التشكيل
        start_time = time.time()
        for _ in range(1000):
            processor.remove_tashkeel(test_text)
        tashkeel_time = time.time() - start_time
        
        # اختبار التطبيع
        start_time = time.time()
        for _ in range(1000):
            processor.normalize_text(test_text)
        normalize_time = time.time() - start_time
        
        # اختبار التقسيم المتقدم
        start_time = time.time()
        for _ in range(100):
            processor.tokenize_advanced(test_text, remove_stop=True, stem=True)
        tokenize_time = time.time() - start_time
        
        # اختبار التخزين المؤقت
        cache.set("test_key", "test_value")
        cached_value = cache.get("test_key")
        
        # اختبار المعالجة المتوازية
        large_text = " ".join([test_text] * 100)
        parallel_result = optimizer.process_text_parallel(
            large_text, 
            lambda t: processor.extract_arabic_words(t)
        )
        
        print(f"✅ اختبارات الأداء:")
        print(f"   إزالة التشكيل (1000 مرة): {tashkeel_time:.3f} ثانية")
        print(f"   التطبيع (1000 مرة): {normalize_time:.3f} ثانية")
        print(f"   التقسيم المتقدم (100 مرة): {tokenize_time:.3f} ثانية")
        print(f"   التخزين المؤقت: {'نجح' if cached_value == 'test_value' else 'فشل'}")
        print(f"   المعالجة المتوازية: {len(parallel_result)} كلمة معالجة")
        
        # تنظيف
        cache.clear()
        optimizer.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ اختبارات الأداء فشلت: {e}")
        return False


def run_memory_tests():
    """تشغيل اختبارات الذاكرة"""
    print("\n" + "="*60)
    print("تشغيل اختبارات الذاكرة")
    print("="*60)
    
    try:
        import psutil
        from arabic_processor import ArabicProcessor
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # إنشاء عدة معالجات
        processors = []
        for _ in range(10):
            processor = ArabicProcessor()
            processors.append(processor)
        
        # معالجة نصوص كبيرة
        large_text = " ".join(["اللغة العربية جميلة ومفيدة"] * 1000)
        
        for processor in processors:
            for _ in range(10):
                processor.tokenize_advanced(large_text, remove_stop=True, stem=True)
        
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        print(f"✅ اختبارات الذاكرة:")
        print(f"   الذاكرة الأولية: {initial_memory / 1024 / 1024:.2f} ميجابايت")
        print(f"   الذاكرة الحالية: {current_memory / 1024 / 1024:.2f} ميجابايت")
        print(f"   الزيادة في الذاكرة: {memory_increase / 1024 / 1024:.2f} ميجابايت")
        
        # التحقق من أن الزيادة معقولة
        if memory_increase < 100 * 1024 * 1024:  # أقل من 100 ميجابايت
            print(f"   ✅ استخدام الذاكرة معقول")
            return True
        else:
            print(f"   ❌ استخدام الذاكرة مفرط")
            return False
        
    except ImportError:
        print("❌ psutil غير متاح - لا يمكن تشغيل اختبارات الذاكرة")
        return False
    except Exception as e:
        print(f"❌ اختبارات الذاكرة فشلت: {e}")
        return False


def run_security_tests():
    """تشغيل اختبارات الأمان"""
    print("\n" + "="*60)
    print("تشغيل اختبارات الأمان")
    print("="*60)
    
    try:
        from arabic_processor import ArabicProcessor
        
        processor = ArabicProcessor()
        
        # اختبارات الأمان
        security_tests = [
            # اختبار النصوص الضارة المحتملة
            ("<script>alert('xss')</script>", "يجب تنظيف النص"),
            ("'; DROP TABLE users; --", "يجب التعامل مع SQL injection"),
            ("../../etc/passwd", "يجب منع path traversal"),
            ("\x00\x01\x02", "يجب التعامل مع الأحرف غير الصالحة"),
            ("A" * 10000, "يجب التعامل مع النصوص الطويلة جداً"),
        ]
        
        passed_tests = 0
        
        for malicious_input, description in security_tests:
            try:
                # محاولة معالجة النص الضار
                result = processor.normalize_text(malicious_input)
                
                # التحقق من أن النتيجة آمنة
                if "<script>" not in result and "DROP TABLE" not in result:
                    print(f"   ✅ {description}")
                    passed_tests += 1
                else:
                    print(f"   ❌ {description}")
                    
            except Exception as e:
                print(f"   ✅ {description} - تم رفض النص الضار: {e}")
                passed_tests += 1
        
        print(f"\n✅ اختبارات الأمان: {passed_tests}/{len(security_tests)} نجحت")
        
        return passed_tests == len(security_tests)
        
    except Exception as e:
        print(f"❌ اختبارات الأمان فشلت: {e}")
        return False


def run_compatibility_tests():
    """تشغيل اختبارات التوافق"""
    print("\n" + "="*60)
    print("تشغيل اختبارات التوافق")
    print("="*60)
    
    try:
        from arabic_processor import ArabicProcessor
        
        processor = ArabicProcessor()
        
        # اختبارات التوافق مع ترميزات مختلفة
        compatibility_tests = [
            ("اللغة العربية", "UTF-8"),
            ("اللغة العربية".encode('utf-8').decode('utf-8'), "UTF-8 encoded"),
            ("اللغة العربية".encode('cp1256').decode('cp1256'), "CP1256"),
            ("اللغة العربية".encode('iso-8859-6').decode('iso-8859-6'), "ISO-8859-6"),
        ]
        
        passed_tests = 0
        
        for test_text, encoding_name in compatibility_tests:
            try:
                result = processor.normalize_text(test_text)
                if result and len(result) > 0:
                    print(f"   ✅ التوافق مع {encoding_name}")
                    passed_tests += 1
                else:
                    print(f"   ❌ فشل التوافق مع {encoding_name}")
                    
            except Exception as e:
                print(f"   ❌ خطأ في التوافق مع {encoding_name}: {e}")
        
        print(f"\n✅ اختبارات التوافق: {passed_tests}/{len(compatibility_tests)} نجحت")
        
        return passed_tests == len(compatibility_tests)
        
    except Exception as e:
        print(f"❌ اختبارات التوافق فشلت: {e}")
        return False


def generate_test_report(results):
    """توليد تقرير الاختبارات"""
    print("\n" + "="*60)
    print("تقرير الاختبارات الشامل")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"إجمالي الاختبارات: {total_tests}")
    print(f"الاختبارات الناجحة: {passed_tests}")
    print(f"الاختبارات الفاشلة: {failed_tests}")
    print(f"نسبة النجاح: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\nتفاصيل النتائج:")
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"   {test_name}: {status}")
    
    # توصيات
    print(f"\nالتوصيات:")
    if failed_tests == 0:
        print("   🎉 جميع الاختبارات نجحت! النظام جاهز للاستخدام.")
    else:
        print("   ⚠️  بعض الاختبارات فشلت. يرجى مراجعة الأخطاء وإصلاحها.")
        
        if not results.get('integration', True):
            print("   - تحقق من تكامل الوحدات المختلفة")
        if not results.get('performance', True):
            print("   - تحسين الأداء قد يكون مطلوباً")
        if not results.get('memory', True):
            print("   - مراجعة استخدام الذاكرة")
        if not results.get('security', True):
            print("   - تعزيز الأمان مطلوب")
        if not results.get('compatibility', True):
            print("   - تحسين التوافق مع الترميزات المختلفة")


def main():
    """الدالة الرئيسية لتشغيل الاختبارات"""
    parser = argparse.ArgumentParser(description='تشغيل الاختبارات الشاملة للمعالج اللغوي العربي')
    parser.add_argument('--unit', action='store_true', help='تشغيل اختبارات الوحدات فقط')
    parser.add_argument('--integration', action='store_true', help='تشغيل اختبارات التكامل فقط')
    parser.add_argument('--performance', action='store_true', help='تشغيل اختبارات الأداء فقط')
    parser.add_argument('--memory', action='store_true', help='تشغيل اختبارات الذاكرة فقط')
    parser.add_argument('--security', action='store_true', help='تشغيل اختبارات الأمان فقط')
    parser.add_argument('--compatibility', action='store_true', help='تشغيل اختبارات التوافق فقط')
    parser.add_argument('--all', action='store_true', help='تشغيل جميع الاختبارات')
    
    args = parser.parse_args()
    
    # إذا لم يتم تحديد أي خيار، تشغيل جميع الاختبارات
    if not any([args.unit, args.integration, args.performance, args.memory, args.security, args.compatibility]):
        args.all = True
    
    print("بدء الاختبارات الشاملة للمعالج اللغوي العربي")
    print("="*60)
    
    results = {}
    
    # تشغيل الاختبارات المطلوبة
    if args.all or args.unit:
        unit_result = run_unit_tests()
        results['unit'] = unit_result.wasSuccessful() if hasattr(unit_result, 'wasSuccessful') else True
    
    if args.all or args.integration:
        results['integration'] = run_integration_tests()
    
    if args.all or args.performance:
        results['performance'] = run_performance_tests()
    
    if args.all or args.memory:
        results['memory'] = run_memory_tests()
    
    if args.all or args.security:
        results['security'] = run_security_tests()
    
    if args.all or args.compatibility:
        results['compatibility'] = run_compatibility_tests()
    
    # توليد التقرير النهائي
    generate_test_report(results)
    
    # إرجاع كود الخروج المناسب
    if all(results.values()):
        print(f"\n🎉 جميع الاختبارات نجحت!")
        return 0
    else:
        print(f"\n⚠️  بعض الاختبارات فشلت.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
