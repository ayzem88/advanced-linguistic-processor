"""
مولد سحابة الكلمات - توليد سحابة الكلمات المتقدمة
"""

import re
from typing import Optional, List
from pathlib import Path
from collections import Counter


class WordCloudGenerator:
    """مولد سحابة الكلمات المتقدم"""
    
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
            'اللذان', 'اللتان', 'اللذين', 'اللواتي', 'اللوات', 'اللائي', 'اللائي', 'اللائي',
            'هو', 'هي', 'هم', 'هن', 'هما', 'هما', 'أنت', 'أنت', 'أنتم', 'أنتن', 'أنا', 'نحن'
        }
        return stop_words
    
    def clean_text(self, text):
        """تنظيف النص"""
        # إزالة التشكيل
        text = re.sub(r'[\u064B-\u065F\u0670\u0617-\u061A]', '', text)
        
        # إزالة علامات الترقيم
        text = re.sub(r'[^\u0600-\u06FF\s]', ' ', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_words(self, text):
        """استخراج الكلمات من النص"""
        # تنظيف النص
        text = self.clean_text(text)
        
        # استخراج الكلمات العربية
        arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
        words = arabic_pattern.findall(text)
        
        # تصفية الكلمات
        filtered_words = []
        for word in words:
            if (len(word) > 2 and 
                word not in self.stop_words and
                not word.isdigit() and
                not re.match(r'^[^\u0600-\u06FF]+$', word)):
                filtered_words.append(word)
        
        return filtered_words
    
    def prepare_text_for_wordcloud(self, text):
        """تحضير النص لسحابة الكلمات"""
        # استخراج الكلمات
        words = self.extract_words(text)
        
        # حساب التكرارات
        word_counts = Counter(words)
        
        # إزالة الكلمات قليلة التكرار
        filtered_words = {word: count for word, count in word_counts.items() if count > 1}
        
        # تحويل إلى نص
        wordcloud_text = []
        for word, count in filtered_words.items():
            wordcloud_text.extend([word] * count)
        
        return ' '.join(wordcloud_text)
    
    def find_arabic_font_path(self) -> Optional[str]:
        """البحث عن خط عربي مناسب"""
        candidate_names: List[str] = [
            # macOS
            "Geeza Pro", "Al Nile", "KufiStandardGK", "DecoType Naskh",
            # Google / Linux
            "Noto Naskh Arabic", "NotoNaskhArabic-Regular", "Amiri", "Amiri-Regular",
            "Scheherazade New", "ScheherazadeNew-Regular", "Lateef", "Cairo",
            # Windows
            "Traditional Arabic", "Arial", "Tahoma", "Times New Roman",
        ]

        search_dirs = [
            Path.home() / "Library/Fonts",
            Path("/Library/Fonts"),
            Path("/System/Library/Fonts"),
            Path("/System/Library/Fonts/Supplemental"),
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path("C:/Windows/Fonts"),
        ]
        extensions = (".ttf", ".ttc", ".otf")

        def name_matches(p: Path) -> bool:
            stem = p.stem.lower().replace(" ", "")
            for n in candidate_names:
                if n.lower().replace(" ", "") in stem:
                    return True
            return False

        for base in search_dirs:
            try:
                if base.exists():
                    for path in base.rglob("*"):
                        if path.suffix.lower() in extensions and name_matches(path):
                            return str(path)
            except Exception:
                continue
        return None
    
    def generate_wordcloud(self, text, max_words=200, width=1000, height=600):
        """توليد سحابة الكلمات"""
        try:
            from wordcloud import WordCloud
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            # تحضير النص
            prepared_text = self.prepare_text_for_wordcloud(text)
            
            if not prepared_text.strip():
                return None
            
            # إعادة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(prepared_text)
            visual_text = get_display(reshaped_text)
            
            # البحث عن خط عربي
            font_path = self.find_arabic_font_path()
            
            # إعداد سحابة الكلمات
            wordcloud = WordCloud(
                width=width,
                height=height,
                background_color="white",
                colormap="viridis",  # تغيير اللون إلى viridis
                prefer_horizontal=0.9,
                max_words=max_words,
                relative_scaling=0.5,
                font_path=font_path if font_path else None,
                min_font_size=10,
                max_font_size=100,
                collocations=False
            )
            
            # توليد السحابة
            wordcloud.generate(visual_text)
            
            return wordcloud
            
        except Exception as e:
            print(f"خطأ في توليد سحابة الكلمات: {e}")
            return None
