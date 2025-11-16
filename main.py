"""
المعالج اللغوي - برنامج تحليل النصوص اللغوية المتقدم
مشابه لـ LancsBox
"""
import sys
import os
import json
import glob
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
import math
import re

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QTabWidget, QTableWidget, 
    QTableWidgetItem, QFileDialog, QMenuBar, QMenu, QMessageBox,
    QSplitter, QGroupBox, QSpinBox, QToolBar, QTreeWidget, 
    QTreeWidgetItem, QComboBox, QProgressBar, QStatusBar,
    QDialog, QLineEdit, QCheckBox, QListWidget, QDockWidget,
    QFrame, QScrollArea, QInputDialog, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QSlider, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QRectF
from PyQt6.QtGui import QFont, QIcon, QAction, QColor, QPalette, QPixmap, QPainter, QPen, QBrush

# مكتبات إضافية للعربية والتحليل
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
from wordcloud import WordCloud
import nltk
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import arabic_reshaper
from bidi.algorithm import get_display


class ArabicTextProcessor:
    """معالج متخصص للنصوص العربية"""
    
    def __init__(self):
        self.arabic_processor = None
        self.setup_arabic_processing()
    
    def setup_arabic_processing(self):
        """إعداد معالجة النصوص العربية"""
        try:
            from arabic_processor import ArabicProcessor
            self.arabic_processor = ArabicProcessor()
        except ImportError:
            print("تحذير: لم يتم العثور على معالج العربية المتقدم")
    
    def process_arabic_text(self, text):
        """معالجة النص العربي"""
        if self.arabic_processor:
            return self.arabic_processor.tokenize_advanced(text, remove_stop=True, stem=True)
        else:
            # معالجة أساسية
            import re
            text = re.sub(r'[^\u0600-\u06FF\s]', '', text)
            return text.split()


class KWICAnalyzer:
    """محلل KWIC (الكلمة في السياق)"""
    
    def __init__(self):
        self.results = []
    
    def search_kwic(self, text, search_term, context_size=5):
        """البحث عن الكلمة في السياق"""
        words = text.split()
        results = []
        
        for i, word in enumerate(words):
            if search_term.lower() in word.lower():
                start = max(0, i - context_size)
                end = min(len(words), i + context_size + 1)
                
                left_context = ' '.join(words[start:i])
                right_context = ' '.join(words[i+1:end])
                
                results.append({
                    'left': left_context,
                    'keyword': word,
                    'right': right_context,
                    'position': i
                })
        
        self.results = results
        return results


class PlotVisualizer:
    """مصور البيانات البصرية"""
    
    def __init__(self):
        self.fig = None
        self.canvas = None
    
    def create_word_distribution_plot(self, text, search_term):
        """إنشاء مخطط توزيع الكلمات"""
        words = text.split()
        positions = []
        
        for i, word in enumerate(words):
            if search_term.lower() in word.lower():
                positions.append(i)
        
        if not positions:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.scatter(positions, [1] * len(positions), alpha=0.7, s=50)
        ax.set_xlabel('موضع الكلمة في النص')
        ax.set_ylabel('')
        ax.set_title(f'توزيع كلمة "{search_term}" في النص')
        ax.grid(True, alpha=0.3)
        
        return fig


class WordCloudGenerator:
    """مولد سحب الكلمات"""
    
    def __init__(self):
        self.wordcloud = None
    
    def generate_wordcloud(self, text, max_words=100):
        """إنشاء سحابة الكلمات"""
        try:
            # إعداد الخط العربي
            font_path = self.get_arabic_font()
            
            wordcloud = WordCloud(
                font_path=font_path,
                width=800,
                height=400,
                background_color='white',
                max_words=max_words,
                colormap='viridis',
                relative_scaling=0.5
            ).generate(text)
            
            self.wordcloud = wordcloud
            return wordcloud
        except Exception as e:
            print(f"خطأ في إنشاء سحابة الكلمات: {e}")
            return None
    
    def get_arabic_font(self):
        """الحصول على خط عربي"""
        # البحث عن خطوط عربية متاحة
        font_paths = [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/tahoma.ttf',
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        return None


class KeywordAnalyzer:
    """محلل الكلمات المفتاحية"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    def analyze_keywords(self, target_text, reference_text=None):
        """تحليل الكلمات المفتاحية"""
        if reference_text is None:
            # تحليل بسيط للنص الواحد
            return self.simple_keyword_analysis(target_text)
        else:
            # مقارنة مع نص مرجعي
            return self.comparative_keyword_analysis(target_text, reference_text)
    
    def simple_keyword_analysis(self, text):
        """تحليل بسيط للكلمات المفتاحية"""
        words = text.split()
        word_freq = Counter(words)
        
        # حساب TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        
        keywords = []
        for i, word in enumerate(feature_names):
            score = tfidf_matrix[0, i]
            keywords.append({
                'word': word,
                'frequency': word_freq.get(word, 0),
                'tfidf_score': score
            })
        
        return sorted(keywords, key=lambda x: x['tfidf_score'], reverse=True)
    
    def comparative_keyword_analysis(self, target_text, reference_text):
        """تحليل مقارن للكلمات المفتاحية"""
        # حساب التكرارات
        target_words = target_text.split()
        reference_words = reference_text.split()
        
        target_freq = Counter(target_words)
        reference_freq = Counter(reference_words)
        
        # حساب النسب
        keywords = []
        all_words = set(target_words) | set(reference_words)
        
        for word in all_words:
            target_count = target_freq.get(word, 0)
            reference_count = reference_freq.get(word, 0)
            
            # حساب النسبة المئوية
            target_percent = (target_count / len(target_words)) * 100 if target_words else 0
            reference_percent = (reference_count / len(reference_words)) * 100 if reference_words else 0
            
            # حساب الفرق
            diff = target_percent - reference_percent
            
            keywords.append({
                'word': word,
                'target_freq': target_count,
                'reference_freq': reference_count,
                'target_percent': target_percent,
                'reference_percent': reference_percent,
                'difference': diff
            })
        
        return sorted(keywords, key=lambda x: abs(x['difference']), reverse=True)


class TextAnalyzer:
    """محلل النصوص اللغوية المتقدم"""
    
    def __init__(self):
        self.text = ""
        self.words = []
        self.tokens = []
        self.sentences = []
        self.arabic_processor = ArabicTextProcessor()
        self.kwic_analyzer = KWICAnalyzer()
        self.plot_visualizer = PlotVisualizer()
        self.wordcloud_generator = WordCloudGenerator()
        self.keyword_analyzer = KeywordAnalyzer()
        
    def load_text(self, text):
        """تحميل النص للتحليل"""
        self.text = text
        self.tokenize()
        self.segment_sentences()
        
    def tokenize(self):
        """تقسيم النص إلى كلمات"""
        text_cleaned = re.sub(r'[^\w\s]', ' ', self.text)
        self.tokens = text_cleaned.split()
        self.words = [w.lower() for w in self.tokens if len(w) > 0]
        
    def segment_sentences(self):
        """تقسيم النص إلى جمل"""
        self.sentences = [s.strip() for s in re.split(r'[.!?؟]+', self.text) if s.strip()]
        
    def get_word_frequency(self, limit=None):
        """حساب تكرار الكلمات"""
        freq = Counter(self.words)
        if limit:
            return dict(freq.most_common(limit))
        return dict(freq)
    
    def get_statistics(self):
        """إحصائيات عامة"""
        unique_words = len(set(self.words))
        total_words = len(self.words)
        
        return {
            'عدد الأحرف': len(self.text),
            'عدد الأحرف (بدون مسافات)': len(self.text.replace(' ', '')),
            'عدد الكلمات الكلي': total_words,
            'عدد الكلمات الفريدة': unique_words,
            'نسبة التنوع': round((unique_words / total_words * 100), 2) if total_words > 0 else 0,
            'متوسط طول الكلمة': round(sum(len(w) for w in self.words) / total_words, 2) if total_words > 0 else 0,
            'عدد الجمل': len(self.sentences),
            'متوسط الكلمات بالجملة': round(total_words / len(self.sentences), 2) if self.sentences else 0
        }
    
    def get_collocations(self, window_size=5, min_freq=2):
        """تحليل التلازمات اللفظية"""
        collocations = defaultdict(int)
        
        for i in range(len(self.words)):
            for j in range(max(0, i-window_size), min(len(self.words), i+window_size+1)):
                if i != j:
                    pair = tuple(sorted([self.words[i], self.words[j]]))
                    collocations[pair] += 1
        
        return {k: v for k, v in collocations.items() if v >= min_freq}
    
    def calculate_mi_score(self, word1, word2):
        """حساب درجة MI (Mutual Information)"""
        total = len(self.words)
        freq_w1 = self.words.count(word1)
        freq_w2 = self.words.count(word2)
        
        colloc_freq = 0
        for i in range(len(self.words) - 1):
            if (self.words[i] == word1 and self.words[i+1] == word2) or \
               (self.words[i] == word2 and self.words[i+1] == word1):
                colloc_freq += 1
        
        if colloc_freq == 0 or freq_w1 == 0 or freq_w2 == 0:
            return 0
        
        p_xy = colloc_freq / total
        p_x = freq_w1 / total
        p_y = freq_w2 / total
        
        try:
            return round(math.log2(p_xy / (p_x * p_y)), 3)
        except:
            return 0

    def get_ngrams(self, n=2):
        """استخراج N-grams"""
        ngrams = []
        for i in range(len(self.words) - n + 1):
            ngrams.append(tuple(self.words[i:i+n]))
        return Counter(ngrams)
    
    def compare_texts(self, other_analyzer):
        """مقارنة نصين"""
        freq1 = Counter(self.words)
        freq2 = Counter(other_analyzer.words)
        
        all_words = set(freq1.keys()) | set(freq2.keys())
        
        comparison = {}
        for word in all_words:
            comparison[word] = {
                'نص1': freq1.get(word, 0),
                'نص2': freq2.get(word, 0),
                'الفرق': freq1.get(word, 0) - freq2.get(word, 0)
            }
        
        return comparison


class CorpusManager:
    """مدير المجموعات النصية"""
    
    def __init__(self):
        self.corpora = {}
        self.current_corpus = None
        
    def add_corpus(self, name, files):
        """إضافة مجموعة نصية"""
        self.corpora[name] = {
            'files': files,
            'created': datetime.now().isoformat(),
            'size': sum(os.path.getsize(f) for f in files if os.path.exists(f))
        }
        
    def get_corpus_text(self, name):
        """قراءة نصوص المجموعة"""
        if name not in self.corpora:
            return ""
        
        texts = []
        for file_path in self.corpora[name]['files']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    texts.append(f.read())
            except:
                continue
        
        return "\n\n".join(texts)
    
    def list_corpora(self):
        """قائمة المجموعات"""
        return list(self.corpora.keys())


class CompareDialog(QDialog):
    """نافذة المقارنة بين نصين"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("مقارنة النصوص")
        self.setGeometry(200, 200, 900, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # منطقة النصوص
        texts_layout = QHBoxLayout()
        
        # النص الأول
        left_group = QGroupBox("النص الأول")
        left_layout = QVBoxLayout()
        self.text1 = QTextEdit()
        self.text1.setPlaceholderText("أدخل النص الأول...")
        left_layout.addWidget(self.text1)
        
        browse1_btn = QPushButton("فتح ملف")
        browse1_btn.clicked.connect(lambda: self.load_file(1))
        left_layout.addWidget(browse1_btn)
        
        left_group.setLayout(left_layout)
        texts_layout.addWidget(left_group)
        
        # النص الثاني
        right_group = QGroupBox("النص الثاني")
        right_layout = QVBoxLayout()
        self.text2 = QTextEdit()
        self.text2.setPlaceholderText("أدخل النص الثاني...")
        right_layout.addWidget(self.text2)
        
        browse2_btn = QPushButton("فتح ملف")
        browse2_btn.clicked.connect(lambda: self.load_file(2))
        right_layout.addWidget(browse2_btn)
        
        right_group.setLayout(right_layout)
        texts_layout.addWidget(right_group)
        
        layout.addLayout(texts_layout)
        
        # زر المقارنة
        compare_btn = QPushButton("مقارنة")
        compare_btn.clicked.connect(self.compare_texts)
        layout.addWidget(compare_btn)
        
        # جدول النتائج
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["الكلمة", "النص 1", "النص 2", "الفرق"])
        layout.addWidget(self.results_table)
        
        self.setLayout(layout)
        
    def load_file(self, text_num):
        """تحميل ملف نصي"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "فتح ملف", "", "ملفات نصية (*.txt);;جميع الملفات (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                    if text_num == 1:
                        self.text1.setPlainText(text)
                    else:
                        self.text2.setPlainText(text)
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل فتح الملف:\n{str(e)}")
                
    def compare_texts(self):
        """مقارنة النصين"""
        analyzer1 = TextAnalyzer()
        analyzer1.load_text(self.text1.toPlainText())
        
        analyzer2 = TextAnalyzer()
        analyzer2.load_text(self.text2.toPlainText())
        
        comparison = analyzer1.compare_texts(analyzer2)
        
        # ترتيب حسب الفرق المطلق
        sorted_comp = sorted(
            comparison.items(), 
            key=lambda x: abs(x[1]['الفرق']), 
            reverse=True
        )[:100]
        
        self.results_table.setRowCount(len(sorted_comp))
        
        for i, (word, data) in enumerate(sorted_comp):
            self.results_table.setItem(i, 0, QTableWidgetItem(word))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(data['نص1'])))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(data['نص2'])))
            
            diff_item = QTableWidgetItem(str(data['الفرق']))
            if data['الفرق'] > 0:
                diff_item.setForeground(QColor('green'))
            elif data['الفرق'] < 0:
                diff_item.setForeground(QColor('red'))
            self.results_table.setItem(i, 3, diff_item)


class MainWindow(QMainWindow):
    """النافذة الرئيسية"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = TextAnalyzer()
        self.corpus_manager = CorpusManager()
        self.current_file = None
        self.init_ui()
        
    def init_ui(self):
        """تهيئة الواجهة"""
        self.setWindowTitle("المختار اللّغويّ الجديد")
        self.setGeometry(100, 100, 1400, 900)
        
        # القوائم
        self.create_menu_bar()
        
        # شريط الأدوات
        self.create_toolbar()
        
        # الواجهة المركزية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # الشريط الجانبي
        self.create_sidebar()
        main_layout.addWidget(self.sidebar_dock)
        
        # المنطقة الرئيسية
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # منطقة النص
        text_panel = self.create_text_panel()
        content_splitter.addWidget(text_panel)
        
        # منطقة النتائج
        results_panel = self.create_results_panel()
        content_splitter.addWidget(results_panel)
        
        content_splitter.setSizes([500, 900])
        main_layout.addWidget(content_splitter)
        
        # شريط الحالة
        self.create_status_bar()
        
        # الأنماط
        self.apply_professional_styles()
        
    def create_menu_bar(self):
        """إنشاء القائمة الرئيسية"""
        menubar = self.menuBar()
        
        # ملف
        file_menu = menubar.addMenu("ملف")
        
        new_action = QAction("جديد", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("فتح", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("حفظ", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        save_results_action = QAction("حفظ النتائج", self)
        save_results_action.triggered.connect(self.save_results)
        file_menu.addAction(save_results_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # أدوات
        tools_menu = menubar.addMenu("أدوات")
        
        analyze_action = QAction("تحليل النص", self)
        analyze_action.setShortcut("F5")
        analyze_action.triggered.connect(self.analyze_text)
        tools_menu.addAction(analyze_action)
        
        compare_action = QAction("مقارنة النصوص", self)
        compare_action.triggered.connect(self.show_compare_dialog)
        tools_menu.addAction(compare_action)
        
        tools_menu.addSeparator()
        
        # الخدمات المتقدمة
        advanced_menu = tools_menu.addMenu("خدمات متقدمة")
        
        kwic_action = QAction("KWIC - الكلمة في السياق", self)
        kwic_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        advanced_menu.addAction(kwic_action)
        
        plot_action = QAction("Plot - التمثيل البصري", self)
        plot_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        advanced_menu.addAction(plot_action)
        
        keyword_action = QAction("الكلمات المفتاحية", self)
        keyword_action.triggered.connect(lambda: self.tabs.setCurrentIndex(5))
        advanced_menu.addAction(keyword_action)
        
        wordcloud_action = QAction("سحابة الكلمات", self)
        wordcloud_action.triggered.connect(lambda: self.tabs.setCurrentIndex(6))
        advanced_menu.addAction(wordcloud_action)
        
        ngram_action = QAction("N-grams", self)
        ngram_action.triggered.connect(lambda: self.tabs.setCurrentIndex(7))
        advanced_menu.addAction(ngram_action)
        
        tools_menu.addSeparator()
        
        corpus_action = QAction("إدارة المجموعات", self)
        corpus_action.triggered.connect(self.manage_corpus)
        tools_menu.addAction(corpus_action)
        
        # مساعدة
        help_menu = menubar.addMenu("مساعدة")
        
        about_action = QAction("حول البرنامج", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = QToolBar("الأدوات الرئيسية")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # قائمة الملف (في أول السطر)
        self.file_menu_action = QAction("📁 ملف", self)
        self.file_menu_action.triggered.connect(self.show_file_menu)
        toolbar.addAction(self.file_menu_action)
        
        toolbar.addSeparator()
        
        analyze_action = QAction("🔍 تحليل", self)
        analyze_action.triggered.connect(self.analyze_text)
        toolbar.addAction(analyze_action)
        
        # محلل الكتب (قبل المقارنة)
        book_analyzer_action = QAction("📚 محلل الكتب", self)
        book_analyzer_action.triggered.connect(self.show_book_analyzer)
        toolbar.addAction(book_analyzer_action)
        
        compare_action = QAction("⚖️ مقارنة", self)
        compare_action.triggered.connect(self.show_compare_dialog)
        toolbar.addAction(compare_action)
        
        toolbar.addSeparator()
        
        # الخدمات الأساسية
        stats_action = QAction("📊 إحصائيات", self)
        stats_action.triggered.connect(self.show_statistics)
        toolbar.addAction(stats_action)
        
        freq_action = QAction("📈 تكرار", self)
        freq_action.triggered.connect(self.show_frequency)
        toolbar.addAction(freq_action)
        
        colloc_action = QAction("🔗 تلازمات", self)
        colloc_action.triggered.connect(self.show_collocations)
        toolbar.addAction(colloc_action)
        
        toolbar.addSeparator()
        
        # الخدمات المتقدمة
        kwic_action = QAction("🔍 KWIC", self)
        kwic_action.triggered.connect(self.show_kwic)
        toolbar.addAction(kwic_action)
        
        plot_action = QAction("📊 Plot", self)
        plot_action.triggered.connect(self.show_plot)
        toolbar.addAction(plot_action)
        
        keyword_action = QAction("🔑 كلمات", self)
        keyword_action.triggered.connect(self.show_keywords)
        toolbar.addAction(keyword_action)
        
        wordcloud_action = QAction("☁️ سحابة", self)
        wordcloud_action.triggered.connect(self.show_wordcloud)
        toolbar.addAction(wordcloud_action)
        
        toolbar.addSeparator()
        
        # خدمة N-grams
        ngram_action = QAction("📝 N-grams", self)
        ngram_action.triggered.connect(self.show_ngrams)
        toolbar.addAction(ngram_action)
        
        # البحث بالجذع
        branches_action = QAction("🌿 جذع", self)
        branches_action.triggered.connect(self.show_branches_search)
        toolbar.addAction(branches_action)
        
        # التوليد الصرفي
        morphological_action = QAction("🔤 صرفي", self)
        morphological_action.triggered.connect(self.show_morphological_generation)
        toolbar.addAction(morphological_action)
        
    def create_sidebar(self):
        """إنشاء الشريط الجانبي"""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)
        
        # شجرة الملفات
        self.corpus_tree = QTreeWidget()
        self.corpus_tree.setHeaderHidden(True)
        self.corpus_tree.itemDoubleClicked.connect(self.load_corpus_item)
        sidebar_layout.addWidget(self.corpus_tree)
        
        # أزرار الإدارة
        add_corpus_btn = QPushButton("إضافة مجموعة")
        add_corpus_btn.clicked.connect(self.add_corpus_dialog)
        sidebar_layout.addWidget(add_corpus_btn)
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_corpus_tree)
        sidebar_layout.addWidget(refresh_btn)
        
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(250)
        
        self.sidebar_dock = sidebar_widget
        
    def create_text_panel(self):
        """إنشاء لوحة النص"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # منطقة النص
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("أدخل النص هنا أو افتح ملف نصي...")
        self.text_input.textChanged.connect(self.update_text_stats)
        layout.addWidget(self.text_input)
        
        # إحصائيات سريعة
        stats_layout = QHBoxLayout()
        self.quick_stats_label = QLabel("الكلمات: 0 | الأحرف: 0")
        self.quick_stats_label.setStyleSheet("background: #f0f0f0; padding: 5px; border-radius: 3px;")
        stats_layout.addWidget(self.quick_stats_label)
        layout.addLayout(stats_layout)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton(" تحليل النص")
        self.analyze_btn.clicked.connect(self.analyze_text)
        buttons_layout.addWidget(self.analyze_btn)
        
        clear_btn = QPushButton("️ مسح")
        clear_btn.clicked.connect(self.clear_all)
        buttons_layout.addWidget(clear_btn)
        
        layout.addLayout(buttons_layout)
        
        panel.setLayout(layout)
        return panel
        
    def create_results_panel(self):
        """إنشاء لوحة النتائج"""
        results_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # منطقة النتائج
        self.results_area = QTextEdit()
        self.results_area.setPlaceholderText("النتائج ستظهر هنا...")
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)
        
        results_widget.setLayout(layout)
        return results_widget
        
    def create_stats_tab(self):
        """تبويب الإحصائيات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(400)
        stats_layout.addWidget(self.stats_text)
        
        stats_widget.setLayout(stats_layout)
        scroll.setWidget(stats_widget)
        
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
        
    def create_frequency_tab(self):
        """تبويب التكرارات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("عرض أول:"))
        
        self.freq_limit_spin = QSpinBox()
        self.freq_limit_spin.setRange(10, 1000)
        self.freq_limit_spin.setValue(100)
        options_layout.addWidget(self.freq_limit_spin)
        
        options_layout.addWidget(QLabel("كلمة"))
        
        options_layout.addStretch()
        
        export_freq_btn = QPushButton("💾 تصدير")
        export_freq_btn.clicked.connect(self.export_frequency)
        options_layout.addWidget(export_freq_btn)
        
        layout.addLayout(options_layout)
        
        # الجدول
        self.freq_table = QTableWidget()
        self.freq_table.setColumnCount(4)
        self.freq_table.setHorizontalHeaderLabels(["الترتيب", "الكلمة", "التكرار", "النسبة %"])
        self.freq_table.setAlternatingRowColors(True)
        layout.addWidget(self.freq_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_kwic_tab(self):
        """تبويب KWIC (الكلمة في السياق)"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث عن:"))
        
        self.kwic_search = QLineEdit()
        self.kwic_search.setPlaceholderText("أدخل الكلمة أو العبارة...")
        search_layout.addWidget(self.kwic_search)
        
        self.kwic_context_spin = QSpinBox()
        self.kwic_context_spin.setRange(1, 20)
        self.kwic_context_spin.setValue(5)
        self.kwic_context_spin.setSuffix(" كلمة")
        search_layout.addWidget(QLabel("حجم السياق:"))
        search_layout.addWidget(self.kwic_context_spin)
        
        search_btn = QPushButton("🔍 بحث")
        search_btn.clicked.connect(self.search_kwic)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # جدول النتائج
        self.kwic_table = QTableWidget()
        self.kwic_table.setColumnCount(4)
        self.kwic_table.setHorizontalHeaderLabels(["السياق الأيسر", "الكلمة المستهدفة", "السياق الأيمن", "الموضع"])
        self.kwic_table.setAlternatingRowColors(True)
        layout.addWidget(self.kwic_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_plot_tab(self):
        """تبويب Plot (التمثيل البصري)"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات الرسم
        plot_layout = QHBoxLayout()
        plot_layout.addWidget(QLabel("الكلمة المستهدفة:"))
        
        self.plot_search = QLineEdit()
        self.plot_search.setPlaceholderText("أدخل الكلمة...")
        plot_layout.addWidget(self.plot_search)
        
        plot_btn = QPushButton("📊 رسم")
        plot_btn.clicked.connect(self.create_plot)
        plot_layout.addWidget(plot_btn)
        
        layout.addLayout(plot_layout)
        
        # منطقة الرسم
        self.plot_canvas = FigureCanvas(Figure(figsize=(12, 6)))
        layout.addWidget(self.plot_canvas)
        
        widget.setLayout(layout)
        return widget
    
    def create_keyword_tab(self):
        """تبويب الكلمات المفتاحية"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات التحليل
        options_layout = QHBoxLayout()
        
        self.keyword_mode = QComboBox()
        self.keyword_mode.addItems(["تحليل بسيط", "مقارنة مع نص مرجعي"])
        options_layout.addWidget(QLabel("نوع التحليل:"))
        options_layout.addWidget(self.keyword_mode)
        
        self.keyword_mode.currentTextChanged.connect(self.toggle_reference_text)
        options_layout.addStretch()
        
        analyze_btn = QPushButton("🔑 تحليل")
        analyze_btn.clicked.connect(self.analyze_keywords)
        options_layout.addWidget(analyze_btn)
        
        layout.addLayout(options_layout)
        
        # النص المرجعي (مخفي افتراضياً)
        self.reference_text_widget = QWidget()
        ref_layout = QVBoxLayout()
        ref_layout.addWidget(QLabel("النص المرجعي:"))
        self.reference_text = QTextEdit()
        self.reference_text.setMaximumHeight(100)
        self.reference_text.setPlaceholderText("أدخل النص المرجعي للمقارنة...")
        ref_layout.addWidget(self.reference_text)
        self.reference_text_widget.setLayout(ref_layout)
        self.reference_text_widget.setVisible(False)
        layout.addWidget(self.reference_text_widget)
        
        # جدول النتائج
        self.keyword_table = QTableWidget()
        self.keyword_table.setColumnCount(6)
        self.keyword_table.setHorizontalHeaderLabels(["الكلمة", "التكرار", "النسبة %", "المرجع", "الفرق", "الدرجة"])
        self.keyword_table.setAlternatingRowColors(True)
        layout.addWidget(self.keyword_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_wordcloud_tab(self):
        """تبويب سحابة الكلمات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات السحابة
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("عدد الكلمات:"))
        
        self.wordcloud_max = QSpinBox()
        self.wordcloud_max.setRange(10, 500)
        self.wordcloud_max.setValue(100)
        options_layout.addWidget(self.wordcloud_max)
        
        generate_btn = QPushButton("☁️ إنشاء سحابة")
        generate_btn.clicked.connect(self.generate_wordcloud)
        options_layout.addWidget(generate_btn)
        
        options_layout.addStretch()
        
        save_btn = QPushButton("💾 حفظ")
        save_btn.clicked.connect(self.save_wordcloud)
        options_layout.addWidget(save_btn)
        
        layout.addLayout(options_layout)
        
        # منطقة عرض السحابة
        self.wordcloud_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(self.wordcloud_canvas)
        
        widget.setLayout(layout)
        return widget
        
    def create_collocations_tab(self):
        """تبويب التلازمات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("نافذة البحث:"))
        self.window_spin = QSpinBox()
        self.window_spin.setRange(1, 10)
        self.window_spin.setValue(5)
        options_layout.addWidget(self.window_spin)
        
        options_layout.addWidget(QLabel("الحد الأدنى:"))
        self.min_freq_spin = QSpinBox()
        self.min_freq_spin.setRange(1, 50)
        self.min_freq_spin.setValue(2)
        options_layout.addWidget(self.min_freq_spin)
        
        options_layout.addStretch()
        
        recalc_btn = QPushButton("🔄 إعادة حساب")
        recalc_btn.clicked.connect(self.update_collocations_table)
        options_layout.addWidget(recalc_btn)
        
        layout.addLayout(options_layout)
        
        # الجدول
        self.colloc_table = QTableWidget()
        self.colloc_table.setColumnCount(5)
        self.colloc_table.setHorizontalHeaderLabels(["الترتيب", "الكلمة 1", "الكلمة 2", "التكرار", "MI Score"])
        self.colloc_table.setAlternatingRowColors(True)
        layout.addWidget(self.colloc_table)
        
        widget.setLayout(layout)
        return widget
        
    def create_ngrams_tab(self):
        """تبويب N-grams"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # خيارات
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("حجم N-gram:"))
        
        self.ngram_size = QSpinBox()
        self.ngram_size.setRange(2, 5)
        self.ngram_size.setValue(2)
        options_layout.addWidget(self.ngram_size)
        
        calc_ngram_btn = QPushButton("🔍 حساب")
        calc_ngram_btn.clicked.connect(self.calculate_ngrams)
        options_layout.addWidget(calc_ngram_btn)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # الجدول
        self.ngrams_table = QTableWidget()
        self.ngrams_table.setColumnCount(3)
        self.ngrams_table.setHorizontalHeaderLabels(["الترتيب", "N-gram", "التكرار"])
        self.ngrams_table.setAlternatingRowColors(True)
        layout.addWidget(self.ngrams_table)
        
        widget.setLayout(layout)
        return widget
        
    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("جاهز")
        
    def update_text_stats(self):
        """تحديث الإحصائيات السريعة"""
        text = self.text_input.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.quick_stats_label.setText(f"الكلمات: {words:,} | الأحرف: {chars:,}")
        
    def analyze_text(self):
        """تحليل النص"""
        text = self.text_input.toPlainText()
        
        if not text.strip():
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال نص للتحليل")
            return
        
        self.status_bar.showMessage("جاري التحليل...")
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # تحميل النص
        self.analyzer.load_text(text)
        self.progress_bar.setValue(20)
        
        # عرض رسالة نجاح التحليل
        self.progress_bar.setValue(100)
        
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("اكتمل التحليل ✓ - استخدم شريط الأدوات العلوي لعرض النتائج")
        
        QTimer.singleShot(3000, lambda: self.status_bar.showMessage("جاهز"))
    
    def show_statistics(self):
        """عرض الإحصائيات في منطقة النتائج"""
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        stats = self.analyzer.get_statistics()
        
        stats_text = "==============================\n"
        stats_text += "الإحصائيات العامة للنص\n"
        stats_text += "==============================\n\n"
        
        for key, value in stats.items():
            stats_text += "------------------------------\n"
            stats_text += f"{key}\n"
            if isinstance(value, float):
                stats_text += f"{value:,.2f}\n"
            else:
                stats_text += f"{value:,}\n"
        
        stats_text += "==============================\n"
        
        self.results_area.setPlainText(stats_text)
        self.status_bar.showMessage("تم عرض الإحصائيات")
    
    def show_frequency(self):
        """عرض تكرار الكلمات في منطقة النتائج"""
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        freq = self.analyzer.get_word_frequency()
        total = sum(freq.values())
        
        freq_text = "==============================\n"
        freq_text += "أكثر الكلمات تكراراً\n"
        freq_text += "==============================\n\n"
        
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]
        
        for i, (word, count) in enumerate(sorted_freq, 1):
            percentage = (count / total * 100) if total > 0 else 0
            freq_text += f"{i:2d}. {word:<20} {count:>5} ({percentage:5.2f}%)\n"
        
        freq_text += "==============================\n"
        
        self.results_area.setPlainText(freq_text)
        self.status_bar.showMessage("تم عرض تكرار الكلمات")
    
    def show_collocations(self):
        """عرض التلازمات في منطقة النتائج"""
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        collocations = self.analyzer.get_collocations(5, 2)
        
        colloc_text = "==============================\n"
        colloc_text += "التلازمات اللفظية\n"
        colloc_text += "==============================\n\n"
        
        sorted_colloc = sorted(collocations.items(), key=lambda x: x[1], reverse=True)[:30]
        
        for i, (pair, count) in enumerate(sorted_colloc, 1):
            mi_score = self.analyzer.calculate_mi_score(pair[0], pair[1])
            colloc_text += f"{i:2d}. {pair[0]} + {pair[1]:<15} {count:>3} (MI: {mi_score:5.2f})\n"
        
        colloc_text += "==============================\n"
        
        self.results_area.setPlainText(colloc_text)
        self.status_bar.showMessage("تم عرض التلازمات")
    
    def show_kwic(self):
        """عرض KWIC في منطقة النتائج"""
        search_term, ok = QInputDialog.getText(self, "KWIC", "أدخل الكلمة للبحث:")
        if not ok or not search_term:
            return
        
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        results = self.analyzer.kwic_analyzer.search_kwic(self.analyzer.text, search_term, 5)
        
        kwic_text = "==============================\n"
        kwic_text += f"الكلمة في السياق: {search_term}\n"
        kwic_text += "==============================\n\n"
        
        for i, result in enumerate(results[:20], 1):
            kwic_text += f"{i:2d}. {result['left']} **{result['keyword']}** {result['right']}\n"
        
        if len(results) > 20:
            kwic_text += f"\n... و {len(results) - 20} نتيجة أخرى\n"
        
        kwic_text += "==============================\n"
        
        self.results_area.setPlainText(kwic_text)
        self.status_bar.showMessage(f"تم العثور على {len(results)} نتيجة")
    
    def show_plot(self):
        """عرض Plot في منطقة النتائج"""
        search_term, ok = QInputDialog.getText(self, "Plot", "أدخل الكلمة للرسم:")
        if not ok or not search_term:
            return
        
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        words = self.analyzer.text.split()
        positions = []
        
        for i, word in enumerate(words):
            if search_term.lower() in word.lower():
                positions.append(i)
        
        if not positions:
            QMessageBox.warning(self, "تحذير", f"لم يتم العثور على كلمة '{search_term}' في النص")
            return
        
        plot_text = "==============================\n"
        plot_text += f"توزيع كلمة '{search_term}' في النص\n"
        plot_text += "==============================\n\n"
        
        plot_text += f"المواضع: {', '.join(map(str, positions))}\n"
        plot_text += f"عدد التكرارات: {len(positions)}\n"
        plot_text += f"نسبة التكرار: {len(positions)/len(words)*100:.2f}%\n"
        
        plot_text += "\nالمواضع في النص:\n"
        plot_text += "------------------------------\n"
        for pos in positions[:10]:  # أول 10 مواضع
            context_start = max(0, pos - 3)
            context_end = min(len(words), pos + 4)
            context = ' '.join(words[context_start:context_end])
            plot_text += f"الموضع {pos}: ...{context}...\n"
        
        if len(positions) > 10:
            plot_text += f"... و {len(positions) - 10} موضع آخر\n"
        
        plot_text += "==============================\n"
        
        self.results_area.setPlainText(plot_text)
        self.status_bar.showMessage(f"تم إنشاء مخطط لكلمة '{search_term}'")
    
    def show_keywords(self):
        """عرض الكلمات المفتاحية في منطقة النتائج"""
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        keywords = self.analyzer.keyword_analyzer.analyze_keywords(self.analyzer.text)
        
        keyword_text = "==============================\n"
        keyword_text += "الكلمات المفتاحية\n"
        keyword_text += "==============================\n\n"
        
        for i, keyword in enumerate(keywords[:20], 1):
            keyword_text += f"{i:2d}. {keyword['word']:<20} تكرار: {keyword['frequency']:>3} (درجة: {keyword['tfidf_score']:.4f})\n"
        
        keyword_text += "==============================\n"
        
        self.results_area.setPlainText(keyword_text)
        self.status_bar.showMessage("تم عرض الكلمات المفتاحية")
    
    def show_wordcloud(self):
        """عرض سحابة الكلمات في نافذة منفصلة"""
        text = self.text_input.toPlainText()
        
        if not text.strip():
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال نص لإنشاء سحابة الكلمات")
            return
        
        try:
            from features.wordcloud_analyzer.wordcloud_dialog import WordCloudDialog
            
            # إنشاء نافذة سحابة الكلمات
            dialog = WordCloudDialog("النص المدخل", text, self)
            dialog.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"لا يمكن بدء خدمة سحابة الكلمات:\n{str(e)}\n\nتأكد من وجود مجلد features/wordcloud_analyzer"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إنشاء سحابة الكلمات:\n{str(e)}")
    
    def show_ngrams(self):
        """عرض N-grams في منطقة النتائج"""
        if not self.analyzer.text:
            QMessageBox.warning(self, "تحذير", "يجب تحليل النص أولاً")
            return
        
        n, ok = QInputDialog.getInt(self, "N-grams", "حجم N-gram:", 2, 2, 5)
        if not ok:
            return
        
        ngrams = self.analyzer.get_ngrams(n)
        
        ngram_text = "==============================\n"
        ngram_text += f"{n}-grams\n"
        ngram_text += "==============================\n\n"
        
        sorted_ngrams = sorted(ngrams.items(), key=lambda x: x[1], reverse=True)[:30]
        
        for i, (ngram, count) in enumerate(sorted_ngrams, 1):
            ngram_text += f"{i:2d}. {' '.join(ngram):<30} {count:>3}\n"
        
        ngram_text += "==============================\n"
        
        self.results_area.setPlainText(ngram_text)
        self.status_bar.showMessage(f"تم عرض {n}-grams")
    
    def show_branches_search(self):
        """عرض البحث بالجذع"""
        text = self.text_input.toPlainText()
        
        if not text.strip():
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال نص للبحث فيه")
            return
        
        try:
            from features.branches_search.branches_dialog import BranchesSearchDialog
            
            # إنشاء نافذة البحث بالجذع
            dialog = BranchesSearchDialog(text, self)
            dialog.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"لا يمكن بدء خدمة البحث بالجذع:\n{str(e)}\n\nتأكد من وجود مجلد features/branches_search"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء البحث بالجذع:\n{str(e)}")
    
    def show_morphological_generation(self):
        """عرض التوليد الصرفي"""
        # الحصول على النص المحدد أولاً، وإذا لم يكن هناك نص محدد، استخدم النص كاملاً
        selected_text = self.text_input.textCursor().selectedText()
        if not selected_text.strip():
            text = self.text_input.toPlainText()
            if not text.strip():
                QMessageBox.warning(self, "تحذير", "الرجاء تحديد نص أو إدخال نص للتحليل الصرفي")
                return
        else:
            text = selected_text
        
        try:
            from features.morphological_generation.morphological_dialog import MorphologicalDialog
            
            # إنشاء نافذة التوليد الصرفي
            dialog = MorphologicalDialog(text, self)
            dialog.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"لا يمكن بدء خدمة التوليد الصرفي:\n{str(e)}\n\nتأكد من وجود مجلد features/morphological_generation"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التوليد الصرفي:\n{str(e)}")
    
    def show_file_menu(self):
        """عرض قائمة الملف الكلاسيكية"""
        try:
            # إنشاء قائمة منبثقة
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 10px 30px 10px 20px;
                    font-size: 13px;
                    color: #333;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #e0e0e0;
                    margin: 4px 0px;
                }
            """)
            
            # إضافة عناصر القائمة
            new_action = menu.addAction("🆕 جديد")
            new_action.setShortcut("Ctrl+N")
            new_action.triggered.connect(self.new_file)
            
            open_action = menu.addAction("📂 فتح")
            open_action.setShortcut("Ctrl+O")
            open_action.triggered.connect(self.open_file)
            
            save_action = menu.addAction("💾 حفظ")
            save_action.setShortcut("Ctrl+S")
            save_action.triggered.connect(self.save_file)
            
            menu.addSeparator()
            
            save_results_action = menu.addAction("💾 حفظ النتائج")
            save_results_action.triggered.connect(self.save_results)
            
            menu.addSeparator()
            
            settings_action = menu.addAction("⚙️ إعدادات")
            settings_action.triggered.connect(self.show_settings)
            
            about_action = menu.addAction("ℹ️ حول البرنامج")
            about_action.triggered.connect(self.show_about)
            
            menu.addSeparator()
            
            exit_action = menu.addAction("❌ خروج")
            exit_action.triggered.connect(self.close)
            
            # عرض القائمة مباشرة تحت زر الملف
            toolbar = self.findChild(QToolBar)
            if toolbar:
                # البحث عن الزر المرتبط بـ file_menu_action
                file_button = toolbar.widgetForAction(self.file_menu_action)
                if file_button:
                    # عرض القائمة تحت الزر مباشرة (RTL: نستخدم bottomRight)
                    button_pos = file_button.mapToGlobal(file_button.rect().bottomRight())
                    menu.exec(button_pos)
                else:
                    menu.exec(toolbar.mapToGlobal(toolbar.rect().topRight()))
            else:
                menu.exec(self.mapToGlobal(self.geometry().topRight()))
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في قائمة الملف:\n{str(e)}")
    
    def new_file(self):
        """إنشاء ملف جديد"""
        # مسح النص الحالي
        self.text_input.clear()
        self.results_area.clear()
        self.status_bar.showMessage("تم إنشاء ملف جديد")
    
    def open_file(self):
        """فتح ملف"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "فتح ملف",
            "",
            "ملفات نصية (*.txt);;جميع الملفات (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_input.setPlainText(content)
                    self.status_bar.showMessage(f"تم فتح الملف: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل فتح الملف:\n{str(e)}")
    
    def save_file(self):
        """حفظ ملف"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "حفظ ملف",
            "untitled.txt",
            "ملفات نصية (*.txt);;جميع الملفات (*)"
        )
        
        if file_path:
            try:
                content = self.text_input.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    self.status_bar.showMessage(f"تم حفظ الملف: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل حفظ الملف:\n{str(e)}")
    
    def show_settings(self):
        """عرض الإعدادات"""
        QMessageBox.information(
            self,
            "الإعدادات",
            "قريباً ستكون الإعدادات متاحة في إصدارات لاحقة"
        )
    
    def update_statistics(self):
        """تحديث الإحصائيات - تم دمجها في show_statistics"""
        pass
        
    def update_frequency_table(self):
        """تحديث جدول التكرارات - تم دمجها في show_frequency"""
        pass
            
    def update_collocations_table(self):
        """تحديث جدول التلازمات - تم دمجها في show_collocations"""
        pass
            
    def calculate_ngrams(self):
        """حساب N-grams - تم دمجها في show_ngrams"""
        pass
    
    def search_kwic(self):
        """البحث عن الكلمة في السياق - تم دمجها في show_kwic"""
        pass
    
    def create_plot(self):
        """إنشاء مخطط توزيع الكلمات - تم دمجها في show_plot"""
        pass
    
    def toggle_reference_text(self):
        """إظهار/إخفاء النص المرجعي - تم دمجها في show_keywords"""
        pass
    
    def analyze_keywords(self):
        """تحليل الكلمات المفتاحية - تم دمجها في show_keywords"""
        pass
    
    def display_simple_keywords(self, keywords):
        """عرض الكلمات المفتاحية البسيطة - تم دمجها في show_keywords"""
        pass
    
    def display_comparative_keywords(self, keywords):
        """عرض الكلمات المفتاحية المقارنة - تم دمجها في show_keywords"""
        pass
    
    def generate_wordcloud(self):
        """إنشاء سحابة الكلمات - تم دمجها في show_wordcloud"""
        pass
    
    def save_wordcloud(self):
        """حفظ سحابة الكلمات"""
        if not hasattr(self.analyzer.wordcloud_generator, 'wordcloud') or not self.analyzer.wordcloud_generator.wordcloud:
            QMessageBox.warning(self, "تحذير", "يجب إنشاء سحابة الكلمات أولاً")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "حفظ سحابة الكلمات", "", "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf)"
        )
        
        if filename:
            try:
                self.analyzer.wordcloud_generator.wordcloud.to_file(filename)
                self.status_bar.showMessage(f"تم حفظ سحابة الكلمات: {filename}")
                QMessageBox.information(self, "نجح", "تم حفظ سحابة الكلمات بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في الحفظ:\n{str(e)}")
                
    def save_results(self):
        """حفظ النتائج"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "حفظ النتائج", "", 
            "JSON (*.json);;CSV (*.csv);;ملف نصي (*.txt)"
        )
        
        if filename:
            try:
                results = {
                    'timestamp': datetime.now().isoformat(),
                    'file': self.current_file or "غير محفوظ",
                    'statistics': self.analyzer.get_statistics(),
                    'word_frequency': self.analyzer.get_word_frequency(100),
                    'collocations': {
                        f"{k[0]}-{k[1]}": v 
                        for k, v in list(self.analyzer.get_collocations().items())[:100]
                    }
                }
                
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['الكلمة', 'التكرار'])
                        for word, count in results['word_frequency'].items():
                            writer.writerow([word, count])
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.stats_text.toPlainText())
                        
                self.status_bar.showMessage(f"تم حفظ النتائج: {filename}")
                QMessageBox.information(self, "نجح", "تم حفظ النتائج بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الحفظ:\n{str(e)}")
                
    def export_frequency(self):
        """تصدير جدول التكرارات"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "تصدير التكرارات", "", "CSV (*.csv);;Excel (*.xlsx)"
        )
        
        if filename:
            try:
                freq = self.analyzer.get_word_frequency()
                
                if filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['الترتيب', 'الكلمة', 'التكرار', 'النسبة'])
                        total = sum(freq.values())
                        for i, (word, count) in enumerate(sorted(freq.items(), key=lambda x: x[1], reverse=True), 1):
                            percentage = (count / total * 100) if total > 0 else 0
                            writer.writerow([i, word, count, f"{percentage:.2f}%"])
                
                self.status_bar.showMessage(f"تم التصدير: {filename}")
                QMessageBox.information(self, "نجح", "تم التصدير بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل التصدير:\n{str(e)}")
                
    def show_book_analyzer(self):
        """عرض محلل الكتب"""
        text = self.text_input.toPlainText()
        
        if not text.strip():
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال نص للتحليل")
            return
        
        try:
            from features.book_analyzer.analysis_dialog import BookAnalysisDialog
            
            # إنشاء نافذة تحليل الكتب
            dialog = BookAnalysisDialog("النص المدخل", text, self)
            dialog.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"لا يمكن بدء خدمة محلل الكتب:\n{str(e)}\n\nتأكد من وجود مجلد features/book_analyzer"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحليل النص:\n{str(e)}")
    
    def show_compare_dialog(self):
        """عرض نافذة المقارنة"""
        dialog = CompareDialog(self)
        dialog.exec()
        
    def manage_corpus(self):
        """إدارة المجموعات"""
        QMessageBox.information(
            self, "قريباً", 
            "ستتوفر هذه الميزة في التحديثات القادمة"
        )
        
    def add_corpus_dialog(self):
        """إضافة مجموعة نصية"""
        # نافذة اختيار الطريقة
        msg = QMessageBox()
        msg.setWindowTitle("إضافة مجموعة نصية")
        msg.setText("كيف تريد إضافة الملفات؟")
        msg.setInformativeText("اختر 'نعم' لاستيراد مجلد كامل\nاختر 'لا' لاختيار ملفات منفصلة")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | 
            QMessageBox.StandardButton.No | 
            QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        choice = msg.exec()
        
        files = []
        folder = None
        
        if choice == QMessageBox.StandardButton.Yes:
            # اختيار مجلد كامل
            folder = QFileDialog.getExistingDirectory(
                self, "اختر مجلد المدونة النصية", "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            if folder:
                # البحث عن جميع ملفات txt في المجلد والمجلدات الفرعية
                files = glob.glob(os.path.join(folder, "**/*.txt"), recursive=True)
                
                if not files:
                    QMessageBox.warning(
                        self, "تحذير",
                        f"لم يتم العثور على ملفات نصية في المجلد:\n{folder}"
                    )
                    return
                    
                QMessageBox.information(
                    self, "نجح",
                    f"تم العثور على {len(files)} ملف نصي"
                )
                
        elif choice == QMessageBox.StandardButton.No:
            # اختيار ملفات منفصلة
            files, _ = QFileDialog.getOpenFileNames(
                self, "اختر ملفات المجموعة", "",
                "ملفات نصية (*.txt);;جميع الملفات (*.*)"
            )
        else:
            return
        
        if files:
            default_name = ""
            if folder:
                default_name = os.path.basename(folder)
            
            name, ok = QInputDialog.getText(
                self, "اسم المجموعة",
                "أدخل اسم المجموعة:",
                QLineEdit.EchoMode.Normal,
                default_name
            )
            
            if ok:
                # إذا لم يُدخل اسم، استخدم اسم افتراضي
                if not name:
                    name = f"مجموعة_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                self.corpus_manager.add_corpus(name, files)
                self.refresh_corpus_tree()
                self.status_bar.showMessage(f"تمت إضافة المجموعة: {name} ({len(files)} ملف)")
                QMessageBox.information(
                    self, "تم بنجاح",
                    f"تمت إضافة المجموعة '{name}'\n{len(files)} ملف نصي"
                )
                
    def refresh_corpus_tree(self):
        """تحديث شجرة المجموعات"""
        self.corpus_tree.clear()
        
        for corpus_name in self.corpus_manager.list_corpora():
            item = QTreeWidgetItem([corpus_name])
            corpus_data = self.corpus_manager.corpora[corpus_name]
            
            for file_path in corpus_data['files']:
                file_item = QTreeWidgetItem([os.path.basename(file_path)])
                file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                item.addChild(file_item)
            
            self.corpus_tree.addTopLevelItem(item)
            
    def load_corpus_item(self, item, column):
        """تحميل ملف من المجموعة"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.text_input.setPlainText(f.read())
                    self.current_file = file_path
                    self.status_bar.showMessage(f"تم فتح: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل فتح الملف:\n{str(e)}")
                
    def clear_all(self):
        """مسح كل شيء"""
        self.text_input.clear()
        self.results_area.clear()
        self.status_bar.showMessage("تم المسح")
        
    def clear_results(self):
        """مسح النتائج فقط - تم دمجها في clear_all"""
        self.results_area.clear()
        
    def show_about(self):
        """معلومات البرنامج"""
        about_text = """
        <h2 style="color: #2196F3;">المختار اللغوي المتقدم</h2>
        <p><b>الإصدار:</b> 3.0 Professional</p>
        <p>برنامج متقدم لتحليل النصوص العربية</p>
        <br>
        <p><b>الخدمات الأساسية:</b></p>
        <ul>
            <li>✓ تحليل تكرار الكلمات</li>
            <li>✓ إحصائيات نصية متقدمة</li>
            <li>✓ تحليل التلازمات اللفظية مع 14 مقياس إحصائي</li>
            <li>✓ تحليل N-grams</li>
            <li>✓ مقارنة النصوص</li>
        </ul>
        <br>
        <p><b>الخدمات المتقدمة:</b></p>
        <ul>
            <li>✓ KWIC - الكلمة في السياق</li>
            <li>✓ Plot - التمثيل البصري</li>
            <li>✓ تحليل الكلمات المفتاحية</li>
            <li>✓ سحابة الكلمات</li>
            <li>✓ إدارة المجموعات النصية</li>
            <li>✓ تصدير النتائج (JSON, CSV, TXT, PNG)</li>
        </ul>
        <br>
        <p><b>تم التطوير باستخدام:</b> Python 3.x + PyQt6 + Matplotlib + NLTK</p>
        <p style="color: #666; font-size: 11px;">مستوحى من AntConc و LancsBox</p>
        """
        QMessageBox.about(self, "حول البرنامج", about_text)
        
    def apply_professional_styles(self):
        """تطبيق الأنماط الاحترافية"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                gridline-color: #f0f0f0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: #000;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                padding: 10px 20px;
                margin-right: 3px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #E3F2FD;
            }
            QToolBar {
                background-color: #f5f5f5;
                border-bottom: 2px solid #e0e0e0;
                padding: 5px;
                spacing: 10px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border-radius: 5px;
                padding: 8px;
            }
            QToolBar QToolButton:hover {
                background-color: #E3F2FD;
            }
            QDockWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
            }
            QTreeWidget {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #BBDEFB;
            }
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            }
            QMenuBar {
                background-color: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
            }
            QMenuBar::item:selected {
                background-color: #E3F2FD;
            }
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setStyle('Fusion')
    
    # الخط
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
