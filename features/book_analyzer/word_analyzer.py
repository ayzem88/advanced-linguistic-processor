"""
محلل الكلمات - تحليل الكلمات المفردة في النص
"""

import re
from collections import Counter


class WordAnalyzer:
    """محلل الكلمات المفردة"""
    
    def __init__(self):
        self.stop_words = self.load_stop_words()
    
    def load_stop_words(self):
        """تحميل كلمات الإيقاف"""
        stop_words = {
            'في', 'من', 'إلى', 'على', 'عن', 'مع', 'بين', 'من', 'هذا', 'هذه', 'ذلك', 'تلك',
            'الذي', 'التي', 'الذين', 'اللاتي', 'اللواتي', 'كان', 'كانت', 'كانوا', 'كانتا',
            'يكون', 'تكون', 'يكونون', 'يكونان', 'تكونان', 'ليس', 'ليست', 'ليسوا', 'ليسا',
            'أو', 'و', 'لكن', 'إلا', 'بل', 'أما', 'إما', 'أن', 'أنه', 'أنها', 'أنهم', 'أنهن',
            'أو', 'أي', 'أين', 'كيف', 'متى', 'لماذا', 'ما', 'من', 'التي', 'الذي', 'اللتي',
            'اللذان', 'اللتان', 'اللذين', 'اللواتي', 'اللوات', 'اللائي', 'اللائي', 'اللائي'
        }
        return stop_words
    
    def remove_diacritics(self, text):
        """إزالة التشكيل من النص"""
        diacritics = re.compile(r'[\u064B-\u065F\u0670\u0617-\u061A]')
        return diacritics.sub('', text)
    
    def extract_arabic_words(self, text):
        """استخراج الكلمات العربية فقط"""
        # تنظيف النص
        text = self.remove_diacritics(text)
        
        # استخراج الكلمات العربية
        arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
        words = arabic_pattern.findall(text)
        
        return words
    
    def filter_words(self, words):
        """تصفية الكلمات وإزالة كلمات الإيقاف"""
        filtered_words = []
        
        for word in words:
            # تجاهل الكلمات القصيرة جداً وكلمات الإيقاف
            if (len(word) > 1 and 
                word not in self.stop_words and
                not word.isdigit() and
                not re.match(r'^[^\u0600-\u06FF]+$', word)):
                filtered_words.append(word)
        
        return filtered_words
    
    def analyze(self, text):
        """تحليل الكلمات في النص"""
        # استخراج الكلمات العربية
        words = self.extract_arabic_words(text)
        
        # تصفية الكلمات
        filtered_words = self.filter_words(words)
        
        # حساب التكرارات
        word_counts = Counter(filtered_words)
        
        # الحصول على أكثر الكلمات تكراراً
        top_words = word_counts.most_common(100)
        
        return {
            'total_words': len(filtered_words),
            'unique_words': len(word_counts),
            'top_words': top_words,
            'word_counts': dict(word_counts)
        }
