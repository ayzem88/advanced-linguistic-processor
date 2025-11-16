"""
اختبارات الواجهة الرسومية للمعالج اللغوي
GUI Tests for Linguistic Processor
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest
    from PyQt6.QtGui import QTextCursor
    
    # استيراد الوحدات الرئيسية
    from main import MainWindow, TextAnalyzer, CorpusManager
    from arabic_processor import ArabicProcessor
    
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 غير متاح - سيتم تخطي اختبارات الواجهة الرسومية")


# @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
class TestMainWindow(unittest.TestCase):
    """اختبارات النافذة الرئيسية"""
    
    @classmethod
    def setUpClass(cls):
        """إعداد البيئة للفئة"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        self.window = MainWindow()
    
    def tearDown(self):
        """تنظيف البيئة بعد كل اختبار"""
        if hasattr(self, 'window'):
            self.window.close()
    
    def test_window_initialization(self):
        """اختبار تهيئة النافذة"""
        self.assertIsNotNone(self.window)
        self.assertIsNotNone(self.window.text_analyzer)
        self.assertIsNotNone(self.window.corpus_manager)
    
    def test_text_area_exists(self):
        """اختبار وجود منطقة النص"""
        self.assertIsNotNone(self.window.text_area)
        self.assertIsNotNone(self.window.results_area)
    
    def test_menu_bar_exists(self):
        """اختبار وجود شريط القوائم"""
        self.assertIsNotNone(self.window.menuBar())
        self.assertGreater(len(self.window.menuBar().actions()), 0)
    
    def test_toolbar_exists(self):
        """اختبار وجود شريط الأدوات"""
        self.assertIsNotNone(self.window.toolbar)
        self.assertGreater(len(self.window.toolbar.actions()), 0)
    
    def test_sidebar_exists(self):
        """اختبار وجود الشريط الجانبي"""
        self.assertIsNotNone(self.window.sidebar)
    
    def test_set_text(self):
        """اختبار تعيين النص"""
        test_text = "اللغة العربية جميلة"
        self.window.text_area.setPlainText(test_text)
        
        actual_text = self.window.text_area.toPlainText()
        self.assertEqual(actual_text, test_text)
    
    def test_get_text(self):
        """اختبار الحصول على النص"""
        test_text = "اللغة العربية جميلة"
        self.window.text_area.setPlainText(test_text)
        
        retrieved_text = self.window.get_current_text()
        self.assertEqual(retrieved_text, test_text)
    
    def test_clear_text(self):
        """اختبار مسح النص"""
        self.window.text_area.setPlainText("نص تجريبي")
        self.window.clear_text()
        
        cleared_text = self.window.text_area.toPlainText()
        self.assertEqual(cleared_text, "")
    
    def test_file_operations(self):
        """اختبار عمليات الملفات"""
        # اختبار إنشاء ملف جديد
        self.window.new_file()
        self.assertEqual(self.window.text_area.toPlainText(), "")
        
        # اختبار مسح النص
        self.window.text_area.setPlainText("نص تجريبي")
        self.window.clear_text()
        self.assertEqual(self.window.text_area.toPlainText(), "")
    
    def test_analysis_buttons(self):
        """اختبار أزرار التحليل"""
        # التحقق من وجود الأزرار
        self.assertIsNotNone(self.window.analyze_btn)
        self.assertIsNotNone(self.window.frequency_btn)
        self.assertIsNotNone(self.window.collocations_btn)
        self.assertIsNotNone(self.window.kwic_btn)
        self.assertIsNotNone(self.window.keywords_btn)
        self.assertIsNotNone(self.window.wordcloud_btn)
        self.assertIsNotNone(self.window.ngrams_btn)
    
    def test_sidebar_buttons(self):
        """اختبار أزرار الشريط الجانبي"""
        # التحقق من وجود الأزرار في الشريط الجانبي
        sidebar_buttons = self.window.sidebar.findChildren(type(self.window.analyze_btn))
        self.assertGreater(len(sidebar_buttons), 0)


# @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
class TestTextAnalyzer(unittest.TestCase):
    """اختبارات محلل النصوص"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.analyzer = TextAnalyzer()
    
    def test_analyzer_initialization(self):
        """اختبار تهيئة المحلل"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.processor)
    
    def test_analyze_text(self):
        """اختبار تحليل النص"""
        text = "اللغة العربية جميلة ومفيدة"
        result = self.analyzer.analyze_text(text)
        
        self.assertIsInstance(result, dict)
        self.assertIn('words', result)
        self.assertIn('characters', result)
        self.assertIn('sentences', result)
    
    def test_get_word_frequency(self):
        """اختبار تكرار الكلمات"""
        text = "اللغة العربية جميلة واللغة العربية مفيدة"
        frequency = self.analyzer.get_word_frequency(text)
        
        self.assertIsInstance(frequency, dict)
        self.assertGreater(len(frequency), 0)
        self.assertIn('اللغة', frequency)
        self.assertIn('العربية', frequency)
    
    def test_get_collocations(self):
        """اختبار الكلمات المتجاورة"""
        text = "اللغة العربية جميلة ومفيدة"
        collocations = self.analyzer.get_collocations(text)
        
        self.assertIsInstance(collocations, list)
    
    def test_get_kwic(self):
        """اختبار KWIC"""
        text = "اللغة العربية جميلة ومفيدة"
        kwic = self.analyzer.get_kwic(text, "اللغة")
        
        self.assertIsInstance(kwic, list)
    
    def test_get_keywords(self):
        """اختبار الكلمات المفتاحية"""
        text = "اللغة العربية جميلة ومفيدة"
        keywords = self.analyzer.get_keywords(text)
        
        self.assertIsInstance(keywords, list)
    
    def test_get_ngrams(self):
        """اختبار N-grams"""
        text = "اللغة العربية جميلة ومفيدة"
        ngrams = self.analyzer.get_ngrams(text, n=2)
        
        self.assertIsInstance(ngrams, list)
        self.assertGreater(len(ngrams), 0)


# @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
class TestCorpusManager(unittest.TestCase):
    """اختبارات مدير المجموعة النصية"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.corpus_manager = CorpusManager()
    
    def test_corpus_initialization(self):
        """اختبار تهيئة مدير المجموعة"""
        self.assertIsNotNone(self.corpus_manager)
        self.assertIsInstance(self.corpus_manager.texts, list)
    
    def test_add_text(self):
        """اختبار إضافة نص"""
        text = "اللغة العربية جميلة"
        self.corpus_manager.add_text(text)
        
        self.assertEqual(len(self.corpus_manager.texts), 1)
        self.assertEqual(self.corpus_manager.texts[0], text)
    
    def test_remove_text(self):
        """اختبار إزالة نص"""
        text = "اللغة العربية جميلة"
        self.corpus_manager.add_text(text)
        self.corpus_manager.remove_text(0)
        
        self.assertEqual(len(self.corpus_manager.texts), 0)
    
    def test_get_all_texts(self):
        """اختبار الحصول على جميع النصوص"""
        texts = ["النص الأول", "النص الثاني", "النص الثالث"]
        
        for text in texts:
            self.corpus_manager.add_text(text)
        
        all_texts = self.corpus_manager.get_all_texts()
        self.assertEqual(len(all_texts), 3)
        self.assertEqual(all_texts, texts)
    
    def test_clear_corpus(self):
        """اختبار مسح المجموعة"""
        texts = ["النص الأول", "النص الثاني"]
        
        for text in texts:
            self.corpus_manager.add_text(text)
        
        self.corpus_manager.clear_corpus()
        self.assertEqual(len(self.corpus_manager.texts), 0)
    
    def test_get_corpus_stats(self):
        """اختبار إحصائيات المجموعة"""
        texts = ["اللغة العربية جميلة", "اللغة العربية مفيدة"]
        
        for text in texts:
            self.corpus_manager.add_text(text)
        
        stats = self.corpus_manager.get_corpus_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_texts', stats)
        self.assertIn('total_words', stats)
        self.assertIn('total_characters', stats)
        
        self.assertEqual(stats['total_texts'], 2)


# @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
class TestDialogIntegration(unittest.TestCase):
    """اختبارات تكامل النوافذ المنبثقة"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
    
    def test_wordcloud_dialog_creation(self):
        """اختبار إنشاء نافذة سحابة الكلمات"""
        try:
            from features.wordcloud_analyzer.wordcloud_dialog import WordCloudDialog
            
            dialog = WordCloudDialog("اللغة العربية جميلة")
            self.assertIsNotNone(dialog)
            dialog.close()
        except ImportError:
            self.skipTest("WordCloudDialog غير متاح")
    
    def test_morphological_dialog_creation(self):
        """اختبار إنشاء نافذة التحليل الصرفي"""
        try:
            from features.morphological_generation.morphological_dialog import MorphologicalDialog
            
            dialog = MorphologicalDialog("اللغة العربية جميلة")
            self.assertIsNotNone(dialog)
            dialog.close()
        except ImportError:
            self.skipTest("MorphologicalDialog غير متاح")
    
    def test_branches_search_dialog_creation(self):
        """اختبار إنشاء نافذة البحث في الفروع"""
        try:
            from features.branches_search.branches_dialog import BranchesSearchDialog
            
            dialog = BranchesSearchDialog("اللغة العربية جميلة")
            self.assertIsNotNone(dialog)
            dialog.close()
        except ImportError:
            self.skipTest("BranchesSearchDialog غير متاح")


class TestGUIPerformance(unittest.TestCase):
    """اختبارات أداء الواجهة الرسومية"""
    
    # @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
    def test_large_text_handling(self):
        """اختبار التعامل مع النصوص الكبيرة"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        window = MainWindow()
        
        # إنشاء نص كبير
        large_text = " ".join(["اللغة العربية جميلة ومفيدة"] * 1000)
        
        # اختبار تعيين النص
        start_time = time.time()
        window.text_area.setPlainText(large_text)
        set_time = time.time() - start_time
        
        # اختبار الحصول على النص
        start_time = time.time()
        retrieved_text = window.text_area.toPlainText()
        get_time = time.time() - start_time
        
        # التحقق من النتائج
        self.assertEqual(len(retrieved_text), len(large_text))
        self.assertLess(set_time, 1.0)  # يجب أن يكون سريعاً
        self.assertLess(get_time, 0.5)  # يجب أن يكون سريعاً
        
        window.close()
    
    # @unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 غير متاح")
    def test_memory_usage(self):
        """اختبار استخدام الذاكرة"""
        import psutil
        import os
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # قياس الذاكرة قبل إنشاء النافذة
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # إنشاء عدة نوافذ
        windows = []
        for _ in range(5):
            window = MainWindow()
            windows.append(window)
        
        # قياس الذاكرة بعد إنشاء النوافذ
        current_memory = process.memory_info().rss
        memory_increase = current_memory - initial_memory
        
        # التحقق من أن الزيادة في الذاكرة معقولة
        self.assertLess(memory_increase, 100 * 1024 * 1024)  # أقل من 100 ميجابايت
        
        # إغلاق النوافذ
        for window in windows:
            window.close()


def run_gui_tests():
    """تشغيل اختبارات الواجهة الرسومية"""
    if not PYQT_AVAILABLE:
        print("PyQt6 غير متاح - لا يمكن تشغيل اختبارات الواجهة الرسومية")
        return
    
    print("تشغيل اختبارات الواجهة الرسومية...")
    
    # إنشاء مجموعة اختبارات
    test_suite = unittest.TestSuite()
    
    # إضافة اختبارات الواجهة الرسومية
    test_suite.addTest(unittest.makeSuite(TestMainWindow))
    test_suite.addTest(unittest.makeSuite(TestTextAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestCorpusManager))
    test_suite.addTest(unittest.makeSuite(TestDialogIntegration))
    test_suite.addTest(unittest.makeSuite(TestGUIPerformance))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # طباعة النتائج
    print(f"\nنتائج اختبارات الواجهة الرسومية:")
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


if __name__ == '__main__':
    import time
    
    print("بدء اختبارات الواجهة الرسومية للمعالج اللغوي...")
    
    # تشغيل اختبارات الواجهة الرسومية
    run_gui_tests()
    
    print("\nانتهت اختبارات الواجهة الرسومية!")
