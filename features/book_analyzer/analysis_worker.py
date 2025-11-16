"""
خيط التحليل - تنفيذ تحليل الكتاب في الخلفية
"""

import re
from collections import Counter
from PyQt6.QtCore import QThread, pyqtSignal

from .word_analyzer import WordAnalyzer
from .compound_analyzer import CompoundAnalyzer
from .entity_extractor import EntityExtractor
from .advanced_compound_analyzer import AdvancedCompoundAnalyzer


class BookAnalysisWorker(QThread):
    """خيط منفصل لتحليل كتاب واحد - شامل ومتقدم"""
    
    progress_update = pyqtSignal(str)  # رسالة التقدم
    analysis_complete = pyqtSignal(dict)  # النتائج النهائية
    analysis_error = pyqtSignal(str)  # رسالة الخطأ
    
    def __init__(self, book_id, book_content):
        super().__init__()
        self.book_id = book_id
        self.book_content = book_content
        self.is_cancelled = False
        
        # إنشاء المحللات
        self.word_analyzer = WordAnalyzer()
        self.compound_analyzer = CompoundAnalyzer()
        self.entity_extractor = EntityExtractor()
        self.advanced_analyzer = AdvancedCompoundAnalyzer()
    
    def run(self):
        """تنفيذ التحليل الشامل المتقدم"""
        try:
            results = {}
            
            # 1. تحليل المركبات والكلمات الأساسي
            self.progress_update.emit("تحليل المركّبات والكلمات الأساسي ...")
            if self.is_cancelled:
                return
            compound_results = self.compound_analyzer.analyze(self.book_content)
            results.update(compound_results)
            
            # 2. التحليل المتقدم للمركبات (PMI, T-Score, etc.)
            self.progress_update.emit("التحليل المتقدم للمركّبات (PMI, T-Score, Log-Likelihood) ...")
            if self.is_cancelled:
                return
            advanced_results = self.advanced_analyzer.analyze(self.book_content)
            results['advanced_compounds'] = advanced_results
            
            # 3. استخراج الكيانات
            self.progress_update.emit("استخراج الكيانات المسمّاة ...")
            if self.is_cancelled:
                return
            results['entities'] = self.entity_extractor.extract(self.book_content)
            
            # 4. تحليل الكلمات المفردة
            self.progress_update.emit("تحليل الكلمات المفردة ...")
            if self.is_cancelled:
                return
            word_results = self.word_analyzer.analyze(self.book_content)
            results.update(word_results)
            
            # إرسال النتائج
            if not self.is_cancelled:
                self.progress_update.emit("انتهى التّحليل الشامل!")
                self.analysis_complete.emit(results)
            
        except Exception as e:
            self.analysis_error.emit(str(e))
    
    def cancel(self):
        """إلغاء عملية التحليل"""
        self.is_cancelled = True
