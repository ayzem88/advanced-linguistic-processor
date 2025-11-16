"""
مستخرج الكيانات - استخراج الكيانات المسماة من النص
"""

import re
from collections import Counter


class EntityExtractor:
    """مستخرج الكيانات المسماة"""
    
    def __init__(self):
        self.name_patterns = self.load_name_patterns()
        self.place_patterns = self.load_place_patterns()
        self.organization_patterns = self.load_organization_patterns()
    
    def load_name_patterns(self):
        """تحميل أنماط الأسماء"""
        patterns = [
            r'الشيخ\s+\w+',
            r'الإمام\s+\w+',
            r'العلامة\s+\w+',
            r'الحافظ\s+\w+',
            r'الفقيه\s+\w+',
            r'ابن\s+\w+',
            r'أبو\s+\w+',
            r'أم\s+\w+',
            r'بنت\s+\w+',
            r'أخو\s+\w+',
            r'أخت\s+\w+',
            r'والد\s+\w+',
            r'والدة\s+\w+',
            r'زوج\s+\w+',
            r'زوجة\s+\w+',
            r'ابن\s+\w+\s+ابن\s+\w+',
            r'أبو\s+\w+\s+ابن\s+\w+',
            r'أم\s+\w+\s+ابن\s+\w+'
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def load_place_patterns(self):
        """تحميل أنماط الأماكن"""
        patterns = [
            r'مدينة\s+\w+',
            r'قرية\s+\w+',
            r'بلدة\s+\w+',
            r'مكة\s+المكرمة',
            r'المدينة\s+المنورة',
            r'القدس',
            r'دمشق',
            r'بغداد',
            r'القاهرة',
            r'الإسكندرية',
            r'تونس',
            r'الجزائر',
            r'المغرب',
            r'اليمن',
            r'العراق',
            r'الشام',
            r'مصر',
            r'الحجاز',
            r'نجد',
            r'اليمامة',
            r'البحرين',
            r'عُمان',
            r'العراق',
            r'الشام',
            r'الجزيرة\s+العربية',
            r'شبه\s+الجزيرة\s+العربية'
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def load_organization_patterns(self):
        """تحميل أنماط المؤسسات"""
        patterns = [
            r'جامعة\s+\w+',
            r'معهد\s+\w+',
            r'مدرسة\s+\w+',
            r'كلية\s+\w+',
            r'دار\s+\w+',
            r'مكتبة\s+\w+',
            r'مؤسسة\s+\w+',
            r'جمعية\s+\w+',
            r'نقابة\s+\w+',
            r'اتحاد\s+\w+',
            r'رابطة\s+\w+',
            r'حزب\s+\w+',
            r'حركة\s+\w+',
            r'جماعة\s+\w+',
            r'طائفة\s+\w+',
            r'مذهب\s+\w+',
            r'فرقة\s+\w+',
            r'طريقة\s+\w+',
            r'زاوية\s+\w+',
            r'تكية\s+\w+',
            r'خانقاه\s+\w+',
            r'رباط\s+\w+',
            r'مسجد\s+\w+',
            r'جامع\s+\w+',
            r'مدرسة\s+\w+',
            r'مكتب\s+\w+',
            r'ديوان\s+\w+',
            r'قصر\s+\w+',
            r'قلعة\s+\w+',
            r'حصن\s+\w+'
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def extract_entities_by_patterns(self, text, patterns):
        """استخراج الكيانات باستخدام الأنماط"""
        entities = []
        for pattern in patterns:
            matches = pattern.findall(text)
            entities.extend(matches)
        return entities
    
    def clean_entity(self, entity):
        """تنظيف الكيان من الأخطاء"""
        # إزالة المسافات الزائدة
        entity = re.sub(r'\s+', ' ', entity.strip())
        # إزالة علامات الترقيم في البداية والنهاية
        entity = re.sub(r'^[^\w\u0600-\u06FF]+|[^\w\u0600-\u06FF]+$', '', entity)
        return entity
    
    def extract(self, text):
        """استخراج الكيانات من النص"""
        # استخراج الأسماء
        names = self.extract_entities_by_patterns(text, self.name_patterns)
        names = [self.clean_entity(name) for name in names if len(name.strip()) > 2]
        
        # استخراج الأماكن
        places = self.extract_entities_by_patterns(text, self.place_patterns)
        places = [self.clean_entity(place) for place in places if len(place.strip()) > 2]
        
        # استخراج المؤسسات
        organizations = self.extract_entities_by_patterns(text, self.organization_patterns)
        organizations = [self.clean_entity(org) for org in organizations if len(org.strip()) > 2]
        
        # حساب التكرارات
        name_counts = Counter(names)
        place_counts = Counter(places)
        org_counts = Counter(organizations)
        
        return {
            'names': names,
            'places': places,
            'organizations': organizations,
            'names_count': len(name_counts),
            'places_count': len(place_counts),
            'organizations_count': len(org_counts),
            'top_names': name_counts.most_common(20),
            'top_places': place_counts.most_common(20),
            'top_organizations': org_counts.most_common(20)
        }
