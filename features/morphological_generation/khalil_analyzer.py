#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محلل الخليل الصرفي - النسخة النهائية المطابقة للمنهج الأصلي
Khalil Morphological Analyzer - Final Version Matching Original Methodology
"""

import sys
import os
import xml.etree.ElementTree as ET
import re
import logging
from typing import List, Dict, Tuple, Optional

class KhalilAnalyzer:
    """محلل الخليل الصرفي - النسخة النهائية"""
    
    def __init__(self):
        # إعداد نظام التسجيل
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # إنشاء handler إذا لم يكن موجوداً
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.db_path = os.path.join(os.path.dirname(__file__), 'db')
        
        # تحميل قاعدة البيانات مع معالجة الأخطاء المحسنة
        try:
            self.prefixes = self._load_prefixes()
            self.suffixes = self._load_suffixes()
            self.patterns = self._load_patterns()
            self.roots = self._load_roots()
            self.toolwords = self._load_toolwords()

            # خرائط مساعدة للوصول إلى فئة السابقة/اللاحقة بسرعة
            self._pref_class = {p.get('unvoweled'): (p.get('class') or '') for p in self.prefixes if p.get('unvoweled') is not None}
            self._suf_class = {s.get('unvoweled'): (s.get('class') or '') for s in self.suffixes if s.get('unvoweled') is not None}
            
            self.logger.info(f"✅ تم تحميل قاعدة البيانات بنجاح:")
            self.logger.info(f"   📝 البادئات: {len(self.prefixes)}")
            self.logger.info(f"   📝 اللواحق: {len(self.suffixes)}")
            self.logger.info(f"   📝 الأنماط: {len(self.patterns)}")
            self.logger.info(f"   📝 الجذور: {len(self.roots)}")
            self.logger.info(f"   📝 الكلمات المساعدة: {len(self.toolwords)}")
            
        except Exception as e:
            self.logger.error(f"فشل في تحميل قاعدة البيانات: {e}")
            raise RuntimeError(f"لا يمكن تحميل قاعدة البيانات الصرفية: {e}")
    
    def _load_xml_file(self, file_path: str) -> ET.ElementTree:
        """
        تحميل ملف XML مع دعم ترميزات متعددة
        
        Args:
            file_path: مسار ملف XML
            
        Returns:
            ElementTree: شجرة XML المحملة
            
        Raises:
            ValueError: إذا فشل في قراءة الملف بجميع الترميزات
        """
        encodings = ['utf-8', 'utf-8-sig', 'windows-1256', 'cp1256', 'iso-8859-6']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    tree = ET.parse(f)
                    self.logger.debug(f"تم تحميل {file_path} بترميز {encoding}")
                    return tree
            except UnicodeDecodeError:
                self.logger.debug(f"فشل ترميز {encoding} للملف {file_path}")
                continue
            except ET.ParseError as e:
                self.logger.error(f"خطأ في تحليل XML للملف {file_path}: {e}")
                raise
            except FileNotFoundError:
                self.logger.error(f"الملف غير موجود: {file_path}")
                raise
        
        raise ValueError(f"لا يمكن قراءة الملف {file_path} بأي من الترميزات المدعومة")
    
    def _load_prefixes(self) -> List[Dict]:
        """تحميل البادئات من قاعدة البيانات مع دعم ترميزات متعددة"""
        prefixes = []
        try:
            tree = self._load_xml_file(os.path.join(self.db_path, 'prefixes.xml'))
            root = tree.getroot()
            
            for prefix in root.findall('prefixe'):
                unvoweled = prefix.get('unvoweledform', '').strip()
                voweled = prefix.get('voweledform', '').strip()
                classe = prefix.get('classe', '').strip()
                
                if unvoweled or classe:  # تضمين البادئات الفارغة أيضاً
                    prefixes.append({
                        'unvoweled': unvoweled,
                        'voweled': voweled,
                        'class': classe
                    })
        except Exception as e:
            self.logger.error(f"خطأ في تحميل البادئات: {e}")
            raise
        
        return prefixes
    
    def _load_suffixes(self) -> List[Dict]:
        """تحميل اللواحق من قاعدة البيانات مع دعم ترميزات متعددة"""
        suffixes = []
        try:
            tree = self._load_xml_file(os.path.join(self.db_path, 'suffixes.xml'))
            root = tree.getroot()
            
            for suffix in root.findall('suffixe'):
                unvoweled = suffix.get('unvoweledform', '').strip()
                voweled = suffix.get('voweledform', '').strip()
                classe = suffix.get('classe', '').strip()
                
                if unvoweled or classe:  # تضمين اللواحق الفارغة أيضاً
                    suffixes.append({
                        'unvoweled': unvoweled,
                        'voweled': voweled,
                        'class': classe
                    })
        except Exception as e:
            self.logger.error(f"خطأ في تحميل اللواحق: {e}")
            raise
        # ضمان توفر بعض اللواحق الشائعة إن كانت غائبة من قاعدة البيانات
        ensure_suffixes = [
            {'unvoweled': 'ون', 'voweled': 'ونَ', 'class': 'C2'},
            {'unvoweled': 'ين', 'voweled': 'ينَ', 'class': 'C2'},
            {'unvoweled': 'ات', 'voweled': 'اتٌ', 'class': 'C2'},
        ]
        existing = set(s.get('unvoweled') for s in suffixes)
        for s in ensure_suffixes:
            if s['unvoweled'] not in existing:
                suffixes.append(s)
                existing.add(s['unvoweled'])

        return suffixes
    
    def _load_patterns(self) -> List[Dict]:
        """تحميل الأنماط من جميع ملفات المجلدات ذات الصلة (Unvoweled/Voweled)"""
        patterns: List[Dict] = []
        try:
            base_dirs = [
                os.path.join(self.db_path, 'nouns', 'patterns', 'Unvoweled'),
                os.path.join(self.db_path, 'nouns', 'patterns', 'Voweled'),
                os.path.join(self.db_path, 'verbs', 'patterns', 'Unvoweled'),
                os.path.join(self.db_path, 'verbs', 'patterns', 'Voweled'),
            ]
            for d in base_dirs:
                if not os.path.isdir(d):
                    continue
                for fname in os.listdir(d):
                    if not fname.lower().endswith('.xml'):
                        continue
                    fpath = os.path.join(d, fname)
                    try:
                        tree = ET.parse(fpath)
                        root = tree.getroot()
                        for pattern in root.findall('pattern'):
                            patterns.append({
                                'id': pattern.get('id', ''),
                                'diac': pattern.get('diac', ''),
                                'type': pattern.get('type', ''),
                                'aug': pattern.get('aug', ''),
                                'cas': pattern.get('cas', ''),
                                'ncg': pattern.get('ncg', ''),
                                'trans': pattern.get('trans', '')
                            })
                    except Exception:
                        continue
        except Exception as e:
            print(f"⚠️  خطأ في تحميل الأنماط: {e}")
        return patterns
    
    def _load_roots(self) -> List[Dict]:
        """تحميل الجذور من جميع ملفات المجلدات (nouns/roots/*.xml, verbs/roots/*.xml)"""
        roots: List[Dict] = []
        try:
            base_dirs = [
                os.path.join(self.db_path, 'nouns', 'roots'),
                os.path.join(self.db_path, 'verbs', 'roots'),
            ]
            for d in base_dirs:
                if not os.path.isdir(d):
                    continue
                for fname in os.listdir(d):
                    if not fname.lower().endswith('.xml'):
                        continue
                    fpath = os.path.join(d, fname)
                    try:
                        tree = ET.parse(fpath)
                        root = tree.getroot()
                        for root_elem in root.findall('root'):
                            roots.append({
                                'val': (root_elem.get('val', '') or '').strip(),
                                'vect': (root_elem.get('vect', '') or '').strip(),
                            })
                    except Exception:
                        continue
        except Exception as e:
            print(f"⚠️  خطأ في تحميل الجذور: {e}")
        return roots

    def _root_plausibility(self, stem: str) -> int:
        """قياس مدى توافق الجذع مع جذور محملة (بحروف مرتبة داخل الكلمة)."""
        if not self.roots:
            return 0
        s = stem
        best = 0
        for r in self.roots:  # نفحص كل الجذور لضمان دقة أعلى
            val = r.get('val') or ''
            if not val:
                continue
            letters = [ch for ch in val if ch.strip()]
            # بعض ملفات الجذور قد تحتوي على مسافات بين الحروف "ص د ق"
            if len(letters) >= 3:
                # تحقق من وجود الحروف بترتيبها داخل الجذع
                idx = 0
                ok = True
                for ch in letters:
                    pos = s.find(ch, idx)
                    if pos == -1:
                        ok = False
                        break
                    idx = pos + 1
                if ok:
                    best = max(best, len(letters))
        return best * 100

    def _class_compat_score(self, prefix_list: List[str], suffix_list: List[str], stem: Optional[str] = None, pattern_types: Optional[List[str]] = None) -> int:
        """تقدير توافق فئات السوابق واللواحق مع تخمين اسم/فعل (تقريب دقيق).
        - يراعي عائلات الفئات: C*, N*, V*
        - يفضّل ترتيب (و/ف) ثم (ب/ك/ل/س) ثم (ال)
        - يوازن بين دلائل الاسمية (ال، ون/ين/ات، N*) والفعلية (V*، سوابق صرفية فعلية)
        """
        def fam(c: str) -> str:
            return (c or '')[:1]

        pref_classes = [self._pref_class.get(p) or '' for p in prefix_list]
        suf_classes = [self._suf_class.get(s) or '' for s in suffix_list]

        score = 0

        # 1) ترتيب السوابق العربية المألوف
        if prefix_list:
            if prefix_list[0] in ('و', 'ف'):
                score += 10
            if any(p in ('ب', 'ك', 'ل', 'س') for p in prefix_list[1:]):
                score += 8
            if prefix_list[-1] == 'ال':
                score += 12

        # 2) دلائل الاسمية/الفعلية من الفئات والسطحيات
        noun_signals = 0
        verb_signals = 0

        if 'ال' in prefix_list:
            noun_signals += 2
        if any(s in ('ون', 'ين', 'ات') for s in suffix_list):
            noun_signals += 2
        if any(c.startswith('N') for c in suf_classes) or any(c.startswith('N') for c in pref_classes):
            noun_signals += 1

        if any(c.startswith('V') for c in suf_classes) or any(c.startswith('V') for c in pref_classes):
            verb_signals += 1
        if stem and len(stem) >= 3 and stem[0] in ('ي', 'ت', 'أ', 'ن') and 'ال' not in prefix_list:
            verb_signals += 1
        # دلائل إضافية من أنواع الأنماط
        if pattern_types:
            if any(t and 'verb' in t.lower() for t in pattern_types):
                verb_signals += 2
            if any(t and 'noun' in t.lower() for t in pattern_types):
                noun_signals += 2

        # ترجيح الفئة الغالبة ومعاقبة التضاد
        if noun_signals and verb_signals:
            score -= 8
        elif noun_signals > verb_signals:
            score += 10
        elif verb_signals > noun_signals:
            score += 10

        # 3) تجانس عائلات اللواحق
        fam_suf = [fam(c) for c in suf_classes if c]
        if fam_suf and len(set(fam_suf)) == 1:
            score += 6

        # 4) قيود عدم التوافق المعروفة
        if 'ال' in prefix_list and any(c.startswith('V') for c in suf_classes):
            score -= 15  # "ال" مع لاحقة فعلية غير شائع

        # 5) عقوبة الفئات المجهولة
        if any(not c for c in pref_classes):
            score -= 2
        if any(not c for c in suf_classes):
            score -= 2

        return score

    # تطبيع مبسط للأفعال المعتلة/الإعلال: نحاول أشكالًا بديلة للجذع لاختبار الجذر
    def _normalize_weak_stems(self, stem: str) -> List[str]:
        forms = {stem}
        s = stem
        # 0) تطبيع عام: الهمزات، الألف المقصورة، التاء المربوطة
        hamza_map = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ؤ': 'و', 'ئ': 'ي', 'ء': ''
        }
        if any(ch in s for ch in hamza_map):
            t = ''.join(hamza_map.get(ch, ch) for ch in s)
            forms.add(t)
        if 'ى' in s:
            forms.add(s.replace('ى', 'ي'))
        if 'ة' in s:
            forms.add(s.replace('ة', 'ه'))
            forms.add(s.replace('ة', ''))

        # 1) قلب الألف إلى واو/ياء حسب السياق (تبسيط)
        if 'ا' in s:
            forms.add(s.replace('ا', 'و'))
            forms.add(s.replace('ا', 'ي'))

        # 2) حذف حرف العلة النهائي
        if s and s[-1] in 'اويى':
            forms.add(s[:-1])

        # 3) حذف حرف علة أوسط مفرد
        for i, ch in enumerate(s):
            if ch in 'اويى' and 0 < i < len(s) - 1:
                forms.add(s[:i] + s[i+1:])

        # 4) معالجة التضعيف (التكرار): إزالة أحد الحرفين المتجاورين
        for i in range(1, len(s)):
            if s[i] == s[i-1]:
                forms.add(s[:i] + s[i+1:])

        return list(forms)

    # ------------------------------
    # تطبيق الأنماط لاستخراج الجذر
    # ------------------------------
    _AR_DIAC = ''.join([
        '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652',
        '\u0670', '\u0653', '\u0654', '\u0655'
    ])

    def _strip_diacritics(self, text: str) -> str:
        if not text:
            return text
        return re.sub(f"[{self._AR_DIAC}]", '', text)

    def _extract_root_via_patterns(self, stem: str) -> List[Dict]:
        """استخراج الجذر من الجذع بمطابقة الأنماط (ف/ع/ل/ل) بعد إزالة التشكيل من الأنماط.
        يعيد قائمة من المرشحين: [{'root': 'ص د ق', 'pattern_id': '...', 'pattern': 'فاعل'}]
        """
        candidates: List[Dict] = []
        if not self.patterns:
            return candidates

        # نحاول أيضاً على جذع منزوع "ال" التعريف إن وُجد
        stems_to_try = [stem]
        if stem.startswith('ال') and len(stem) > 2:
            stems_to_try.append(stem[2:])

        for st in stems_to_try:
            for pat in self.patterns[:50000]:  # حد أمان
                p = self._strip_diacritics(pat.get('diac') or '')
                if not p:
                    continue
                # بناء تعبير نمطي باستبدال placeholders (ف/ع/ل/ل)
                # ندعم الثلاثي (ف/ع/ل) والرباعي (ف/ع/ل/ل)
                placeholders = []
                regex_parts = []
                for ch in p:
                    if ch == 'ف':
                        placeholders.append('R')
                        regex_parts.append('([\u0621-\u064A])')
                    elif ch == 'ع':
                        placeholders.append('R')
                        regex_parts.append('([\u0621-\u064A])')
                    elif ch == 'ل':
                        placeholders.append('R')
                        regex_parts.append('([\u0621-\u064A])')
                    else:
                        # حرف ثابت من النمط
                        regex_parts.append(re.escape(ch))
                # يجب أن يطابق الطول الكامل
                rx = '^' + ''.join(regex_parts) + '$'
                m = re.match(rx, st)
                if not m:
                    continue
                # استخراج الجذور المقترحة
                groups = list(m.groups())
                if len(groups) < 3:
                    continue
                # ثلاثي: أول 3 مجموعات؛ رباعي: 4 مجموعات
                if len(groups) >= 4:
                    root_letters = [groups[0], groups[1], groups[2], groups[3]]
                else:
                    root_letters = [groups[0], groups[1], groups[2]]
                # تحقق من وجود الجذر في قاعدة الجذور (مع أو بدون مسافات)
                root_no_space = ''.join(root_letters)
                root_spaced = ' '.join(root_letters)
                exists = False
                for r in self.roots[:5000]:
                    val = (r.get('val') or '').replace(' ', '')
                    if val == root_no_space:
                        exists = True
                        break
                candidates.append({
                    'root': root_spaced if exists else root_spaced,
                    'pattern_id': pat.get('id'),
                    'pattern': p,
                    'type': pat.get('type'),
                    'exists': exists,
                    'cas': pat.get('cas'),
                    'ncg': pat.get('ncg'),
                    'trans': pat.get('trans')
                })

        # نفضل المرشحين الذين وُجدوا في قاعدة الجذور
        candidates.sort(key=lambda x: (1 if x['exists'] else 0), reverse=True)
        # نعيد أفضل 3
        return candidates[:3]
    
    def _load_toolwords(self) -> List[Dict]:
        """تحميل الكلمات المساعدة من قاعدة البيانات"""
        toolwords = []
        try:
            tree = ET.parse(os.path.join(self.db_path, 'underived', 'toolwords.xml'))
            root = tree.getroot()
            
            for toolword in root.findall('toolword'):
                toolwords.append({
                    'unvoweled': toolword.get('unvoweledform', ''),
                    'voweled': toolword.get('voweledform', ''),
                    'type': toolword.get('type', ''),
                    'prefix_class': toolword.get('prefixeclass', ''),
                    'suffix_class': toolword.get('suffixeclass', '')
                })
        except Exception as e:
            print(f"⚠️  خطأ في تحميل الكلمات المساعدة: {e}")
        
        return toolwords
    
    def analyze_word(self, word: str) -> List[Dict]:
        """تحليل كلمة باستخدام منهج الخليل الأصلي"""
        word = word.strip()
        if not word:
            return []
        # إزالة التشكيل من المُدخل لضمان التعرف على الكلمات المشكولة
        normalized = self._strip_diacritics(word)

        results = []
        
        # 1. البحث في الكلمات المساعدة أولاً
        toolword_results = self._analyze_toolwords(normalized)
        if toolword_results:
            # إذا كانت الكلمة أداة (مثل "في") نكتفي بنتيجة الأداة لتجنّب التكرار غير المفيد
            return toolword_results
        
        # 2. التحليل الصرفي للكلمات العادية
        morphological_results = self._analyze_morphology(normalized)
        results.extend(morphological_results)
        
        # 3. إذا لم توجد نتائج، البحث في الجذور مباشرة
        if not results:
            root_results = self._analyze_roots(normalized)
            results.extend(root_results)
        
        return results
    
    def _analyze_toolwords(self, word: str) -> List[Dict]:
        """تحليل الكلمات المساعدة"""
        results = []
        for toolword in self.toolwords:
            if word == toolword['unvoweled']:
                results.append({
                    'type': 'toolword',
                    'word': word,
                    'voweled': toolword['voweled'],
                    'toolword_type': toolword['type'],
                    'prefix_class': toolword['prefix_class'],
                    'suffix_class': toolword['suffix_class'],
                    'analysis': f"كلمة مساعدة: {word} ({toolword['type']})"
                })
        return results
    
    def _analyze_morphology(self, word: str) -> List[Dict]:
        """التحليل الصرفي للكلمة"""
        results = []

        # 1) توليد كل التركيبات المسموحة للسوابق وفق ترتيب عربي منطقي: [و/ف] ثم [ب/ك/ل/س] ثم [ال]
        stage1 = ['و', 'ف', '']
        stage2 = ['ب', 'ك', 'ل', 'س', '']
        stage3 = ['ال', '']

        prefix_candidates: List[Tuple[List[str], str]] = []  # (prefix_list, remaining_after)
        for p1 in stage1:
            for p2 in stage2:
                for p3 in stage3:
                    seq = [x for x in [p1, p2, p3] if x]
                    pref_str = ''.join(seq)
                    if pref_str and word.startswith(pref_str):
                        prefix_candidates.append((seq, word[len(pref_str):]))
        # إضافة خيار عدم وجود سوابق
        prefix_candidates.append(([], word))

        # 2) توليد التركيبات المسموحة للواحق: [جمع (ون/ين/ات)] ثم [ضمير (ه/ها/هم/هن/ك/كم/كن/ي/نا)]، مع السماح بلا أي لاحقة
        plurals = ['ون', 'ين', 'ات', '']
        pronouns = ['كما', 'هما', 'كم', 'كن', 'هم', 'هن', 'ها', 'ه', 'نا', 'ي', 'ك', '']  # الأطول أولاً

        best = None
        best_score = -1

        # تجميع كل المرشحين وتقييمهم ثم اختيار الأفضل وفق حد أدنى للجودة
        candidates_ranked: List[Tuple[int, Tuple[List[str], str, List[str], Dict]]] = []
        for pref_list, after_pref in prefix_candidates:
            if not after_pref:
                continue
            for pl in plurals:
                for pr in pronouns:
                    suf_seq = [x for x in [pl, pr] if x]
                    suf_str = ''.join(suf_seq)
                    if suf_str:
                        if after_pref.endswith(suf_str):
                            stem = after_pref[:-len(suf_str)]
                        else:
                            continue
                    else:
                        stem = after_pref
                    # شروط صلاحية الجذع
                    if not stem or len(stem) < 2:
                        continue
                    # درجة ملاءمة:
                    arabic = all('\u0600' <= ch <= '\u06FF' for ch in stem)
                    if not arabic or len(stem) < 2:
                        continue
                    # إزالة تفضيل الطول: لا نكافئ الجذع الأطول كي لا نُبقي "ال" داخله
                    score = 0
                    if 3 <= len(stem) <= 6:
                        score += 15
                    # توافق الجذور المباشر
                    score += self._root_plausibility(stem)
                    # توافق الجذور بعد التطبيع للأفعال المعتلة (نأخذ أفضل بديل فقط)
                    alt_scores = [self._root_plausibility(alt) for alt in self._normalize_weak_stems(stem)]
                    if alt_scores:
                        score += int(max(alt_scores) * 0.5)
                    # نقاط وجود تطابق نمطي فعلي
                    pattern_hits = self._extract_root_via_patterns(stem)
                    pattern_types = [c.get('type') for c in pattern_hits] if pattern_hits else []
                    if pattern_hits:
                        if any(c.get('exists') for c in pattern_hits):
                            score += 140
                        else:
                            score += 70
                    # توافق الفئات (نمرر الجذع وأنواع الأنماط)
                    score += self._class_compat_score(pref_list, suf_seq, stem, pattern_types)
                    # مكونات عربية شائعة
                    if pref_list:
                        score += 10
                    if pl:
                        score += 60
                    if pr:
                        score += 30
                    if 'ال' in pref_list:
                        score += 30
                    # عقوبة إبقاء سوابق/لواحق ظاهرة داخل الجذع بدون فصل
                    if stem.startswith('ال') and 'ال' not in pref_list:
                        score -= 120
                    if stem.startswith('ال') and any(x in ('ب','ك','ل','س') for x in pref_list) and 'ال' not in pref_list:
                        score -= 50
                    if stem.endswith(('ون','ين','ات')) and not any(x in ('ون','ين','ات') for x in suf_seq):
                        score -= 50
                    if stem and any(stem.startswith(p + 'ال') for p in ('ب','ك','ل','س')) and 'ال' not in pref_list:
                        score -= 30
                    # في حالة وجود حرف عطف ثم "ال" داخل الجذع، الأفضل فصلها كسوابق
                    if (stem.startswith('وال') or stem.startswith('فال')) and 'ال' not in pref_list:
                        score -= 60
                    # مكافأة لتقسيم غني: وجود و/ف + (ب/ك/ل/س) + ال + جمع
                    if any(x in ('و','ف') for x in pref_list) and any(x in ('ب','ك','ل','س') for x in pref_list) and 'ال' in pref_list and any(x in ('ون','ين','ات') for x in suf_seq):
                        score += 40
                    # خزّن المرشح للتصنيف لاحقًا
                    candidates_ranked.append((score, (pref_list, stem, suf_seq, {'pattern_hits': pattern_hits})))

        # اختر أفضل مرشح يتجاوز حدًا أدنى للجودة، وإلا اختر الأعلى
        if candidates_ranked:
            candidates_ranked.sort(key=lambda x: x[0], reverse=True)
            MIN_SCORE = 170  # رفع الحد الأدنى بعد تعزيز الأوزان
            chosen_score, chosen = candidates_ranked[0]
            # ابحث عن أول مرشح يتجاوز الحد
            for sc, cand in candidates_ranked:
                if sc >= MIN_SCORE:
                    chosen_score, chosen = sc, cand
                    break
            pref_list, stem, suf_seq, aux = chosen
            pattern_roots = aux.get('pattern_hits') or []
            stem_analysis = self._analyze_stem(stem)
            if pattern_roots:
                stem_analysis.setdefault('via_patterns', pattern_roots)
            results.append({
                'type': 'morphological',
                'prefixes': pref_list,
                'suffixes': suf_seq,
                'stem': stem,
                'stem_analysis': stem_analysis,
                'analysis': f"سوابق: {'+'.join(pref_list) if pref_list else 'لا يوجد'} + جذع: {stem} + لواحق: {'+'.join(suf_seq) if suf_seq else 'لا يوجد'}"
            })

        return results
    
    def _analyze_stem(self, stem: str) -> Dict:
        """تحليل الجذع للبحث عن الجذر والنمط"""
        analysis = {
            'possible_roots': [],
            'possible_patterns': [],
            'length': len(stem)
        }
        
        # البحث في الجذور
        for root in self.roots:
            if root['val'] and stem == root['val']:
                analysis['possible_roots'].append({
                    'root': root['val'],
                    'vect': root['vect'],
                    'type': 'exact_match'
                })
        
        # البحث عن أنماط مطابقة
        for pattern in self.patterns:
            if pattern['diac'] and stem == pattern['diac']:
                analysis['possible_patterns'].append({
                    'id': pattern['id'],
                    'pattern': pattern['diac'],
                    'type': pattern['type'],
                    'aug': pattern['aug'],
                    'cas': pattern['cas'],
                    'ncg': pattern['ncg'],
                    'trans': pattern['trans']
                })
        
        return analysis
    
    def _analyze_roots(self, word: str) -> List[Dict]:
        """البحث المباشر في الجذور"""
        results = []
        for root in self.roots:
            if root['val'] and word == root['val']:
                results.append({
                    'type': 'root_direct',
                    'word': word,
                    'root': root['val'],
                    'vect': root['vect'],
                    'analysis': f"جذر مباشر: {word}"
                })
        return results
