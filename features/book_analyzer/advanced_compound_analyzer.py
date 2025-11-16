"""
محلل المركبات المتقدم - تحليل متقدم للمركبات اللفظية
"""

import re
from collections import Counter
from math import log2, sqrt


class AdvancedCompoundAnalyzer:
    """محلل المركبات المتقدم"""
    
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
    
    def calculate_t_score(self, bigram, word_counts, total_words):
        """حساب T-Score"""
        word1, word2 = bigram
        count1 = word_counts.get(word1, 0)
        count2 = word_counts.get(word2, 0)
        bigram_count = word_counts.get(bigram, 0)
        
        if bigram_count == 0:
            return 0
        
        expected = (count1 * count2) / total_words
        if expected == 0:
            return 0
        
        t_score = (bigram_count - expected) / sqrt(bigram_count)
        return t_score
    
    def calculate_log_likelihood(self, bigram, word_counts, total_words):
        """حساب Log-Likelihood"""
        word1, word2 = bigram
        count1 = word_counts.get(word1, 0)
        count2 = word_counts.get(word2, 0)
        bigram_count = word_counts.get(bigram, 0)
        
        if bigram_count == 0:
            return 0
        
        # حساب الاحتمالات
        p_bigram = bigram_count / total_words
        p_word1 = count1 / total_words
        p_word2 = count2 / total_words
        
        if p_word1 == 0 or p_word2 == 0:
            return 0
        
        # حساب Log-Likelihood
        ll = 2 * total_words * (p_bigram * log2(p_bigram / (p_word1 * p_word2)) if p_bigram > 0 else 0)
        return ll
    
    def categorize_compound(self, bigram, pmi, t_score, ll):
        """تصنيف المركب حسب قوة الترابط"""
        if pmi > 3 and t_score > 2 and ll > 10:
            return "قوي جداً"
        elif pmi > 2 and t_score > 1.5 and ll > 5:
            return "قوي"
        elif pmi > 1 and t_score > 1 and ll > 2:
            return "متوسط"
        elif pmi > 0 and t_score > 0.5 and ll > 1:
            return "ضعيف"
        else:
            return "ضعيف جداً"
    
    def analyze(self, text):
        """تحليل المركبات المتقدم"""
        # استخراج الكلمات
        words = self.extract_words(text)
        
        if len(words) < 2:
            return {
                'compounds': [],
                'statistics': {
                    'total_compounds': 0,
                    'strong_compounds': 0,
                    'medium_compounds': 0,
                    'weak_compounds': 0
                }
            }
        
        # استخراج المركبات
        bigrams = self.extract_bigrams(words)
        bigram_counts = Counter(bigrams)
        word_counts = Counter(words)
        
        total_words = len(words)
        compounds = []
        
        # تحليل كل مركب
        for bigram, count in bigram_counts.most_common(100):
            if count < 2:  # تجاهل المركبات التي تظهر مرة واحدة فقط
                continue
                
            pmi = self.calculate_pmi(bigram, word_counts, total_words)
            t_score = self.calculate_t_score(bigram, word_counts, total_words)
            ll = self.calculate_log_likelihood(bigram, word_counts, total_words)
            
            category = self.categorize_compound(bigram, pmi, t_score, ll)
            
            compounds.append({
                'text': ' '.join(bigram),
                'count': count,
                'pmi': round(pmi, 3),
                't_score': round(t_score, 3),
                'log_likelihood': round(ll, 3),
                'category': category
            })
        
        # ترتيب المركبات حسب PMI
        compounds.sort(key=lambda x: x['pmi'], reverse=True)
        
        # إحصائيات التصنيف
        strong_count = sum(1 for c in compounds if c['category'] in ['قوي جداً', 'قوي'])
        medium_count = sum(1 for c in compounds if c['category'] == 'متوسط')
        weak_count = sum(1 for c in compounds if c['category'] in ['ضعيف', 'ضعيف جداً'])
        
        return {
            'compounds': compounds[:50],  # أفضل 50 مركب
            'statistics': {
                'total_compounds': len(compounds),
                'strong_compounds': strong_count,
                'medium_compounds': medium_count,
                'weak_compounds': weak_count
            }
        }
