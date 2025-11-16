"""
نظام التخزين المؤقت المتقدم للمعالج اللغوي
Advanced Caching System for Linguistic Processor
"""

import pickle
import hashlib
import os
import time
import threading
from pathlib import Path
from typing import Any, Optional, Dict, Callable
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import json
from datetime import datetime, timedelta


class AdvancedCache:
    """نظام تخزين مؤقت متقدم مع دعم متعدد المستويات"""
    
    def __init__(self, cache_dir: str = "cache", max_size: int = 1000, ttl: int = 3600):
        """
        تهيئة نظام التخزين المؤقت
        
        Args:
            cache_dir: مجلد التخزين المؤقت
            max_size: الحد الأقصى لعدد العناصر في الذاكرة
            ttl: وقت انتهاء الصلاحية بالثواني
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size = max_size
        self.ttl = ttl
        
        # تخزين مؤقت في الذاكرة
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        
        # قفل للعمليات المتزامنة
        self.lock = threading.RLock()
        
        # إحصائيات الأداء
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'disk_reads': 0,
            'disk_writes': 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """توليد مفتاح فريد للعنصر"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float) -> bool:
        """التحقق من انتهاء صلاحية العنصر"""
        return time.time() - timestamp > self.ttl
    
    def _evict_lru(self):
        """إزالة العنصر الأقل استخداماً"""
        if not self.access_times:
            return
        
        # العثور على العنصر الأقدم
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # إزالة العنصر
        if oldest_key in self.memory_cache:
            del self.memory_cache[oldest_key]
        if oldest_key in self.access_times:
            del self.access_times[oldest_key]
        
        self.stats['evictions'] += 1
    
    def _save_to_disk(self, key: str, data: Any):
        """حفظ البيانات على القرص"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'data': data,
                    'timestamp': time.time()
                }, f)
            self.stats['disk_writes'] += 1
        except Exception as e:
            print(f"خطأ في حفظ التخزين المؤقت: {e}")
    
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """تحميل البيانات من القرص"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # التحقق من انتهاء الصلاحية
            if self._is_expired(cached_data['timestamp']):
                cache_file.unlink()  # حذف الملف المنتهي الصلاحية
                return None
            
            self.stats['disk_reads'] += 1
            return cached_data['data']
        except Exception as e:
            print(f"خطأ في تحميل التخزين المؤقت: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """الحصول على عنصر من التخزين المؤقت"""
        with self.lock:
            # البحث في الذاكرة أولاً
            if key in self.memory_cache:
                if not self._is_expired(self.access_times[key]):
                    self.access_times[key] = time.time()
                    self.stats['hits'] += 1
                    return self.memory_cache[key]['data']
                else:
                    # إزالة العنصر المنتهي الصلاحية
                    del self.memory_cache[key]
                    del self.access_times[key]
            
            # البحث على القرص
            disk_data = self._load_from_disk(key)
            if disk_data is not None:
                # إعادة تخزين في الذاكرة
                self.memory_cache[key] = {'data': disk_data}
                self.access_times[key] = time.time()
                self.stats['hits'] += 1
                return disk_data
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, data: Any):
        """حفظ عنصر في التخزين المؤقت"""
        with self.lock:
            # التحقق من الحد الأقصى
            if len(self.memory_cache) >= self.max_size:
                self._evict_lru()
            
            # حفظ في الذاكرة
            self.memory_cache[key] = {'data': data}
            self.access_times[key] = time.time()
            
            # حفظ على القرص أيضاً
            self._save_to_disk(key, data)
    
    def clear(self):
        """مسح التخزين المؤقت بالكامل"""
        with self.lock:
            self.memory_cache.clear()
            self.access_times.clear()
            
            # مسح ملفات القرص
            for cache_file in self.cache_dir.glob("*.pkl"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    print(f"خطأ في حذف ملف التخزين المؤقت: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات التخزين المؤقت"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'memory_items': len(self.memory_cache),
            'disk_files': len(list(self.cache_dir.glob("*.pkl"))),
            **self.stats
        }


def cached(cache: AdvancedCache, ttl: Optional[int] = None):
    """ديكوراتور للتخزين المؤقت"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # توليد المفتاح
            key = cache._generate_key(func.__name__, *args, **kwargs)
            
            # محاولة الحصول من التخزين المؤقت
            result = cache.get(key)
            if result is not None:
                return result
            
            # تنفيذ الدالة وحفظ النتيجة
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator


class PerformanceOptimizer:
    """محسن الأداء للنصوص الكبيرة"""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        تهيئة محسن الأداء
        
        Args:
            max_workers: الحد الأقصى لعدد العمال المتوازيين
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        
        # إحصائيات الأداء
        self.stats = {
            'parallel_operations': 0,
            'total_time_saved': 0,
            'texts_processed': 0
        }
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 1000) -> list:
        """تقسيم النص إلى أجزاء للمعالجة المتوازية"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def process_text_parallel(self, text: str, processor_func: Callable, chunk_size: int = 1000) -> list:
        """معالجة النص بشكل متوازي"""
        start_time = time.time()
        
        # تقسيم النص
        chunks = self.split_text_into_chunks(text, chunk_size)
        
        # معالجة متوازية
        futures = [self.thread_pool.submit(processor_func, chunk) for chunk in chunks]
        results = [future.result() for future in futures]
        
        # دمج النتائج
        final_result = []
        for result in results:
            if isinstance(result, list):
                final_result.extend(result)
            else:
                final_result.append(result)
        
        # تحديث الإحصائيات
        duration = time.time() - start_time
        self.stats['parallel_operations'] += 1
        self.stats['texts_processed'] += len(chunks)
        self.stats['total_time_saved'] += duration
        
        return final_result
    
    def batch_process(self, texts: list, processor_func: Callable) -> list:
        """معالجة مجموعة من النصوص بشكل متوازي"""
        start_time = time.time()
        
        futures = [self.thread_pool.submit(processor_func, text) for text in texts]
        results = [future.result() for future in futures]
        
        duration = time.time() - start_time
        self.stats['parallel_operations'] += 1
        self.stats['texts_processed'] += len(texts)
        self.stats['total_time_saved'] += duration
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الأداء"""
        return {
            'parallel_operations': self.stats['parallel_operations'],
            'texts_processed': self.stats['texts_processed'],
            'total_time_saved': self.stats['total_time_saved'],
            'max_workers': self.max_workers,
            'average_time_per_text': (
                self.stats['total_time_saved'] / self.stats['texts_processed']
                if self.stats['texts_processed'] > 0 else 0
            )
        }
    
    def cleanup(self):
        """تنظيف الموارد"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


# إنشاء مثيلات عامة
main_cache = AdvancedCache("cache", max_size=2000, ttl=7200)  # ساعتان
performance_optimizer = PerformanceOptimizer()


# ديكوراتورات مساعدة
def cached_arabic_processing(func):
    """ديكوراتور للتخزين المؤقت لمعالجة النصوص العربية"""
    return cached(main_cache)(func)


def parallel_processing(chunk_size: int = 1000):
    """ديكوراتور للمعالجة المتوازية"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, text: str, *args, **kwargs):
            if isinstance(text, str) and len(text.split()) > chunk_size:
                return performance_optimizer.process_text_parallel(
                    text, lambda t: func(self, t, *args, **kwargs), chunk_size
                )
            else:
                return func(self, text, *args, **kwargs)
        return wrapper
    return decorator
