"""
محلل المركبات - تحليل المركبات اللفظية في النص
"""

import re
from collections import Counter
from math import log2


class CompoundAnalyzer:
    """محلل المركبات اللفظية"""
    
    def __init__(self):
        self.stop_words = self.load_stop_words()
    
    def load_stop_words(self):
        """تحميل كلمات الإيقاف"""
        stop_words = {
            'في', 'من', 'إلى', 'على', 'عن', 'مع', 'بين', 'من', 'هذا', 'هذه', 'ذلك', 'تلك',
            'الذي', 'التي', 'الذين', 'اللاتي', 'اللواتي', 'كان', 'كانت', 'كانوا', 'كانتا',
            'يكون', 'تكون', 'يكونون', 'يكونان', 'تكونان', 'ليس', 'ليست', 'ليسوا', 'ليسا',
            'أو', 'و', 'لكن', 'إلا', 'بل', 'أما', 'إما', 'أن', 'أنه', 'أنها', 'أنهم', 'أنهن'
        }
        return stop_words
    
    def extract_words(self, text):
        """استخراج الكلمات من النص"""
        # إزالة التشكيل
        text = re.sub(r'[\u064B-\u065F\u0670\u0617-\u061A]', '', text)
        
        # استخراج الكلمات العربية
        arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
        words = arabic_pattern.findall(text)
        
        # تصفية الكلمات
        filtered_words = []
        for word in words:
            if (len(word) > 1 and 
                word not in self.stop_words and
                not word.isdigit()):
                filtered_words.append(word)
        
        return filtered_words
    
    def extract_bigrams(self, words):
        """استخراج المركبات الثنائية"""
        bigrams = []
        for i in range(len(words) - 1):
            bigram = (words[i], words[i + 1])
            bigrams.append(bigram)
        return bigrams
    
    def extract_trigrams(self, words):
        """استخراج المركبات الثلاثية"""
        trigrams = []
        for i in range(len(words) - 2):
            trigram = (words[i], words[i + 1], words[i + 2])
            trigrams.append(trigram)
        return trigrams
    
    def calculate_pmi(self, bigram, word_counts, total_words):
        """حساب PMI (Pointwise Mutual Information)"""
        word1, word2 = bigram
        count1 = word_counts.get(word1, 0)
        count2 = word_counts.get(word2, 0)
        bigram_count = word_counts.get(bigram, 0)
        
        if count1 == 0 or count2 == 0 or bigram_count == 0:
            return 0
        
        p_word1 = count1 / total_words
        p_word2 = count2 / total_words
        p_bigram = bigram_count / total_words
        
        if p_bigram == 0:
            return 0
        
        pmi = log2(p_bigram / (p_word1 * p_word2))
        return pmi
    
    def analyze(self, text):
        """تحليل المركبات في النص"""
        # استخراج الكلمات
        words = self.extract_words(text)
        
        if len(words) < 2:
            return {
                'total_bigrams_all': 0,
                'unique_bigrams': 0,
                'total_trigrams_all': 0,
                'unique_trigrams': 0,
                'top_bigrams': [],
                'top_trigrams': []
            }
        
        # استخراج المركبات
        bigrams = self.extract_bigrams(words)
        trigrams = self.extract_trigrams(words)
        
        # حساب التكرارات
        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)
        word_counts = Counter(words)
        
        # حساب PMI للمركبات الثنائية
        total_words = len(words)
        bigrams_with_pmi = []
        
        for bigram, count in bigram_counts.most_common(50):
            pmi = self.calculate_pmi(bigram, word_counts, total_words)
            bigrams_with_pmi.append({
                'text': ' '.join(bigram),
                'count': count,
                'pmi': pmi
            })
        
        # ترتيب المركبات حسب PMI
        bigrams_with_pmi.sort(key=lambda x: x['pmi'], reverse=True)
        
        # حساب PMI للمركبات الثلاثية
        trigrams_with_pmi = []
        for trigram, count in trigram_counts.most_common(30):
            word1, word2, word3 = trigram
            count1 = word_counts.get(word1, 0)
            count2 = word_counts.get(word2, 0)
            count3 = word_counts.get(word3, 0)
            
            if count1 > 0 and count2 > 0 and count3 > 0:
                p_word1 = count1 / total_words
                p_word2 = count2 / total_words
                p_word3 = count3 / total_words
                p_trigram = count / total_words
                
                if p_trigram > 0:
                    pmi = log2(p_trigram / (p_word1 * p_word2 * p_word3))
                    trigrams_with_pmi.append({
                        'text': ' '.join(trigram),
                        'count': count,
                        'pmi': pmi
                    })
        
        # ترتيب المركبات الثلاثية حسب PMI
        trigrams_with_pmi.sort(key=lambda x: x['pmi'], reverse=True)
        
        return {
            'total_bigrams_all': len(bigrams),
            'unique_bigrams': len(bigram_counts),
            'total_trigrams_all': len(trigrams),
            'unique_trigrams': len(trigram_counts),
            'top_bigrams': bigrams_with_pmi[:20],
            'top_trigrams': trigrams_with_pmi[:15]
        }
