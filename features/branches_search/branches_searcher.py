"""
باحث الفروع - البحث عن الكلمات التي تحتوي على تسلسل حروف معين
"""

import re
from collections import Counter


class BranchesSearcher:
    """باحث الفروع للكلمات العربية"""
    
    def __init__(self):
        # الحروف المسموحة فقط: س إ آ ء ؤ أ ل ت م و ن ي ه ا ى + التشكيل
        self.allowed_base_letters = set('سإآءؤألتمونيهاى')
        self.hamza_variations = ['ء', 'أ', 'إ', 'آ', 'ؤ', 'ئ']
        self.wawi_variations = ['و', 'ي', 'ا']
        # التشكيل
        self.diacritics = set('ًٌٍَُِّْ')
    
    def parse_search_input(self, search_input):
        """تحليل إدخال البحث لفصل الجذر عن الحروف المستثناة"""
        # البحث عن الحروف المستثناة بين قوسين
        excluded_pattern = r'\(([^)]+)\)'
        match = re.search(excluded_pattern, search_input)
        
        if match:
            # استخراج الجذر (قبل القوسين)
            root_text = search_input[:match.start()].strip()
            # استخراج الحروف المستثناة (داخل القوسين)
            excluded_text = match.group(1)
            excluded_letters = [char.strip() for char in excluded_text.split('،') if char.strip()]
        else:
            # لا توجد حروف مستثناة
            root_text = search_input.strip()
            excluded_letters = []
        
        # تحويل الجذر إلى قائمة من الحروف (إزالة المسافات)
        root_letters = [char for char in root_text.replace(' ', '') if char.strip()]
        
        return root_letters, excluded_letters
    
    def build_search_pattern(self, root_letters):
        """بناء نمط البحث للجذر"""
        def letter_pattern(letter):
            if letter == 'ء':
                return '[ءأإآؤئ]'
            elif letter == 'و':
                return '[ويا]'
            elif letter == 'ي':
                return '[ويا]'
            else:
                return letter
        
        # بناء نمط البحث - يجب أن تظهر الحروف بالترتيب
        pattern_parts = []
        for letter in root_letters:
            pattern_parts.append(letter_pattern(letter))
        
        # النمط النهائي: أي حرف + الحروف المطلوبة بالترتيب + أي حرف
        pattern = '.*' + ''.join(pattern_parts) + '.*'
        
        return pattern
    
    def get_allowed_chars(self, root_letters):
        """الحصول على الحروف المسموحة للكلمة"""
        # البداية: حروف الجذر + الحروف الأساسية المسموحة فقط
        allowed_chars = set(root_letters)
        allowed_chars.update(self.allowed_base_letters)
        allowed_chars.update(self.diacritics)
        
        # إضافة تنوعات الهمزة
        if 'ء' in root_letters:
            allowed_chars.update(self.hamza_variations)
        
        # إضافة تنوعات الواو والياء
        if 'و' in root_letters or 'ي' in root_letters:
            allowed_chars.update(self.wawi_variations)
        
        return allowed_chars
    
    def clean_word(self, word):
        """تنظيف الكلمة من التشكيل"""
        return re.sub(r'[ًٌٍَُِّْ]', '', word)
    
    def extract_arabic_words(self, text):
        """استخراج الكلمات العربية من النص"""
        arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
        return arabic_pattern.findall(text)
    
    def is_valid_word(self, word, min_length=3, max_length=12):
        """التحقق من صحة الكلمة (الطول)"""
        word_length = len(word)
        return min_length <= word_length <= max_length
    
    def contains_excluded_letters(self, word, excluded_letters):
        """التحقق من وجود الحروف المستثناة في الكلمة"""
        return any(letter in word for letter in excluded_letters)
    
    def search_branches_in_text(self, text, root_letters, excluded_letters=None):
        """البحث عن الفروع في نص معين"""
        if excluded_letters is None:
            excluded_letters = []
        
        # بناء نمط البحث
        pattern = self.build_search_pattern(root_letters)
        allowed_chars = self.get_allowed_chars(root_letters)
        
        # استخراج الكلمات العربية
        words = self.extract_arabic_words(text)
        
        branch_counts = {}
        
        for word in words:
            # تنظيف الكلمة
            cleaned_word = self.clean_word(word)
            
            # التحقق من صحة الكلمة
            if not self.is_valid_word(cleaned_word):
                continue
            
            # التحقق من وجود الحروف المستثناة
            if self.contains_excluded_letters(cleaned_word, excluded_letters):
                continue
            
            # التحقق من مطابقة النمط
            if re.search(pattern, cleaned_word):
                # التحقق من الحروف المسموحة (اختياري)
                if set(cleaned_word).issubset(allowed_chars):
                    branch_counts[word] = branch_counts.get(word, 0) + 1
        
        return branch_counts
    
    def search_branches_in_book(self, book_content, root_letters, excluded_letters=None):
        """البحث عن الفروع في كتاب واحد"""
        branches = self.search_branches_in_text(book_content, root_letters, excluded_letters)
        
        # ترتيب النتائج حسب التكرار (من الأكثر للأقل)
        sorted_branches = sorted(branches.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_branches
    
    def format_branches_results(self, results, source_info=None):
        """تنسيق نتائج البحث للعرض"""
        if not results:
            return "لم نعثر على أيّ فرع في النص!"
        
        # ترتيب النتائج حسب التكرار
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        formatted_text = "==============================\n"
        formatted_text += "نتائج البحث بالجذع\n"
        formatted_text += "==============================\n\n"
        
        # إضافة معلومات المصدر
        if source_info:
            formatted_text += f"المصدر: {source_info}\n"
            formatted_text += "==============================\n\n"
        else:
            formatted_text += "المصدر: غير محدد\n"
            formatted_text += "==============================\n\n"
        
        for i, (word, count) in enumerate(sorted_results, 1):
            formatted_text += f"{i:2d}. {word:<20} - {count:>3}\n"
        
        formatted_text += "==============================\n"
        formatted_text += f"إجمالي النتائج: {len(sorted_results)} كلمة\n"
        
        return formatted_text
