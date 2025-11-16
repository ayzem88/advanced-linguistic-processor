#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المحلل الصرفي بعد إضافة قاعدة البيانات الكاملة
"""

import sys
from pathlib import Path

# إضافة المسار
sys.path.insert(0, str(Path(__file__).parent / 'features' / 'morphological_generation'))

try:
    from khalil_analyzer import KhalilAnalyzer
    
    print("=" * 60)
    print("اختبار المحلل الصرفي - محلل الخليل")
    print("=" * 60)
    print()
    
    # إنشاء المحلل
    print("📦 جاري تحميل المحلل...")
    analyzer = KhalilAnalyzer()
    print()
    
    # كلمات الاختبار
    test_words = [
        "كتاب",
        "مدرسة", 
        "يكتبون",
        "المعلمون",
        "والطلاب",
        "بالقلم"
    ]
    
    print("=" * 60)
    print("اختبار الكلمات")
    print("=" * 60)
    print()
    
    for word in test_words:
        print(f"\n🔍 تحليل كلمة: {word}")
        print("-" * 40)
        
        results = analyzer.analyze_word(word)
        
        if results:
            print(f"✅ عدد النتائج: {len(results)}")
            
            # عرض أول 3 نتائج
            for i, result in enumerate(results[:3], 1):
                print(f"\n   النتيجة {i}:")
                
                if 'root' in result:
                    print(f"   - الجذر: {result.get('root', 'غير معروف')}")
                
                if 'pattern' in result:
                    print(f"   - الوزن: {result.get('pattern', 'غير معروف')}")
                
                if 'prefix' in result:
                    prefix = result.get('prefix', '')
                    if prefix:
                        print(f"   - البادئة: {prefix}")
                
                if 'suffix' in result:
                    suffix = result.get('suffix', '')
                    if suffix:
                        print(f"   - اللاحقة: {suffix}")
                
                if 'type' in result:
                    print(f"   - النوع: {result.get('type', 'غير معروف')}")
        else:
            print("❌ لم يتم العثور على نتائج")
    
    print("\n")
    print("=" * 60)
    print("✅ اكتمل الاختبار")
    print("=" * 60)
    print()
    
    # إحصائيات قاعدة البيانات
    print("=" * 60)
    print("📊 إحصائيات قاعدة البيانات")
    print("=" * 60)
    print(f"البادئات: {len(analyzer.prefixes):,}")
    print(f"اللواحق: {len(analyzer.suffixes):,}")
    print(f"الأنماط: {len(analyzer.patterns):,}")
    print(f"الجذور: {len(analyzer.roots):,}")
    print(f"الكلمات الأدوات: {len(analyzer.toolwords):,}")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    print("تأكد من وجود ملف khalil_analyzer.py في المجلد الصحيح")
except Exception as e:
    print(f"❌ خطأ: {e}")
    import traceback
    traceback.print_exc()

