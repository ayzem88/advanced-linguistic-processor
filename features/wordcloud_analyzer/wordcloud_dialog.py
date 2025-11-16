"""
نافذة سحابة الكلمات - الواجهة الرئيسية لسحابة الكلمات
"""

from __future__ import annotations

from typing import Optional
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QGroupBox, QScrollArea, QWidget,
    QSpinBox, QComboBox
)


class WordCloudDialog(QDialog):
    """نافذة سحابة الكلمات المتقدمة"""
    
    def __init__(self, title: str, text: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.text = text
        
        self.setWindowTitle(f"سحابة الكلمات: {self.title}")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(1000, 800)
        
        # تطبيق تصميم المعالج اللغوي
        self.apply_linguistic_processor_theme()
        
        self._image: Optional[QImage] = None
        self._html_path: Optional[str] = None
        
        self._init_ui()
        self._generate_wordcloud()
    
    def apply_linguistic_processor_theme(self):
        """تطبيق تصميم المعالج اللغوي"""
        self.setStyleSheet("""
            QDialog {
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
            QSpinBox {
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
        """)
    
    def _init_ui(self):
        """تهيئة الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # العنوان والمعلومات
        self.create_header(layout)
        
        # خيارات السحابة
        self.create_options_section(layout)
        
        # منطقة العرض
        self.create_display_area(layout)
        
        # أزرار التحكم
        self.create_control_buttons(layout)
    
    def create_header(self, parent_layout):
        """إنشاء العنوان والمعلومات"""
        header = QGroupBox("سحابة الكلمات")
        header.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #e0e0e0; 
                border-radius: 8px; 
                padding: 15px; 
                background-color: #f9f9f9; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 5px; 
                color: #2196F3; 
            }
        """)
        
        header_layout = QHBoxLayout(header)
        title_lbl = QLabel(f"📚 {self.title}")
        title_lbl.setStyleSheet("QLabel { font-size: 16px; color: #2196F3; font-weight: bold; }")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        parent_layout.addWidget(header)
    
    def create_options_section(self, parent_layout):
        """إنشاء قسم الخيارات"""
        options_group = QGroupBox("خيارات السحابة")
        options_layout = QHBoxLayout(options_group)
        
        # عدد الكلمات
        options_layout.addWidget(QLabel("عدد الكلمات:"))
        self.max_words_spin = QSpinBox()
        self.max_words_spin.setRange(50, 500)
        self.max_words_spin.setValue(200)
        options_layout.addWidget(self.max_words_spin)
        
        # خريطة الألوان
        options_layout.addWidget(QLabel("خريطة الألوان:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems([
            "viridis", "plasma", "inferno", "magma", "tab20", 
            "Set3", "Pastel1", "Pastel2", "Dark2", "Accent"
        ])
        self.colormap_combo.setCurrentText("viridis")
        options_layout.addWidget(self.colormap_combo)
        
        # زر إعادة توليد
        regenerate_btn = QPushButton("🔄 إعادة توليد")
        regenerate_btn.clicked.connect(self._regenerate_wordcloud)
        options_layout.addWidget(regenerate_btn)
        
        options_layout.addStretch()
        parent_layout.addWidget(options_group)
    
    def create_display_area(self, parent_layout):
        """إنشاء منطقة العرض"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: 1px solid #e0e0e0; 
                border-radius: 6px; 
                background: white; 
            }
        """)
        
        container = QWidget()
        self.preview_layout = QVBoxLayout(container)
        self.preview_layout.setContentsMargins(10, 10, 10, 10)
        self.preview_label = QLabel("جاري توليد السحابة...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 20px;
            }
        """)
        self.preview_layout.addWidget(self.preview_label)
        scroll.setWidget(container)
        parent_layout.addWidget(scroll)
    
    def create_control_buttons(self, parent_layout):
        """إنشاء أزرار التحكم"""
        btns = QHBoxLayout()
        
        # زر حفظ الصورة
        self.save_img_btn = QPushButton("💾 حفظ الصورة")
        self.save_img_btn.clicked.connect(self._save_image)
        self.save_img_btn.setEnabled(False)
        btns.addWidget(self.save_img_btn)
        
        # زر تصدير HTML
        self.export_html_btn = QPushButton("🌐 تصدير HTML")
        self.export_html_btn.clicked.connect(self._export_html)
        self.export_html_btn.setEnabled(False)
        btns.addWidget(self.export_html_btn)
        
        btns.addStretch()
        
        # زر إغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        
        parent_layout.addLayout(btns)
    
    def _generate_wordcloud(self):
        """توليد سحابة الكلمات"""
        try:
            from .wordcloud_generator import WordCloudGenerator
            
            # إنشاء مولد السحابة
            generator = WordCloudGenerator()
            
            # توليد السحابة
            wordcloud = generator.generate_wordcloud(
                self.text,
                max_words=self.max_words_spin.value(),
                width=1200,
                height=800
            )
            
            if wordcloud is None:
                self.preview_label.setText("لا يمكن توليد سحابة الكلمات من النص المحدد.")
                return
            
            # تحويل إلى QImage للعرض
            img = wordcloud.to_image()
            qimg = self._pil_to_qimage(img)
            self._image = qimg
            
            pix = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pix)
            self.preview_label.setMinimumSize(pix.width() // 2, pix.height() // 2)
            self.preview_label.setScaledContents(True)
            
            # تمكين الأزرار
            self.save_img_btn.setEnabled(True)
            self.export_html_btn.setEnabled(True)
            
        except Exception as e:
            self.preview_label.setText(f"حدث خطأ أثناء توليد السحابة: {e}")
    
    def _regenerate_wordcloud(self):
        """إعادة توليد السحابة"""
        self.preview_label.setText("جاري إعادة توليد السحابة...")
        self.preview_label.setPixmap(QPixmap())
        self.save_img_btn.setEnabled(False)
        self.export_html_btn.setEnabled(False)
        
        # إعادة توليد
        self._generate_wordcloud()
    
    def _pil_to_qimage(self, pil_image):
        """تحويل صورة PIL إلى QImage"""
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_image.size[0], pil_image.size[1], QImage.Format.Format_RGBA8888)
        return qimg
    
    def _save_image(self):
        """حفظ الصورة"""
        if not self._image:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "حفظ صورة السحابة",
            f"سحابة_{self.title.replace(' ', '_')}.png",
            "صور (*.png *.jpg *.jpeg)"
        )
        
        if not file_path:
            return
        
        ok = self._image.save(file_path)
        if ok:
            QMessageBox.information(self, "تم الحفظ", f"حُفظت الصورة في:\n{file_path}")
        else:
            QMessageBox.warning(self, "فشل الحفظ", "تعذر حفظ الصورة.")
    
    def _export_html(self):
        """تصدير HTML"""
        try:
            from .wordcloud_generator import WordCloudGenerator
            import arabic_reshaper
            from bidi.algorithm import get_display
            from wordcloud import WordCloud
            
            # إنشاء مولد السحابة
            generator = WordCloudGenerator()
            
            # تحضير النص
            prepared_text = generator.prepare_text_for_wordcloud(self.text)
            reshaped_text = arabic_reshaper.reshape(prepared_text)
            visual_text = get_display(reshaped_text)
            
            # البحث عن خط عربي
            font_path = generator.find_arabic_font_path()
            
            # إعداد سحابة الكلمات
            wc = WordCloud(
                width=1000,
                height=700,
                background_color="white",
                colormap=self.colormap_combo.currentText(),
                prefer_horizontal=0.9,
                max_words=self.max_words_spin.value(),
                relative_scaling=0.5,
                font_path=font_path if font_path else None,
            )
            wc.generate(visual_text)
            
            # تحويل إلى SVG
            svg = wc.to_svg(embed_font=True)
            
            # اختيار ملف الحفظ
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "تصدير سحابة الكلمات كـ HTML",
                f"سحابة_{self.title.replace(' ', '_')}.html",
                "ملفات HTML (*.html)"
            )
            
            if not file_path:
                return
            
            # إعداد الخط
            font_family = f"'{Path(font_path).stem}'" if font_path else "Tahoma,Arial,sans-serif"
            
            # إنشاء HTML
            html = (
                "<!DOCTYPE html><html lang=\"ar\" dir=\"rtl\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                f"<title>سحابة الكلمات - {self.title}</title>"
                f"<style>body{{font-family:{font_family};background:#fff;margin:0;padding:20px;}}"
                "h1{{color:#2196F3;text-align:center;}}"
                ".box{{text-align:center;margin:20px 0;}}</style>"
                "</head><body>"
                f"<h1>سحابة الكلمات - {self.title}</h1>"
                "<div class=\"box\">"
                f"{svg}"
                "</div>"
                "</body></html>"
            )
            
            # حفظ الملف
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            self._html_path = file_path
            QMessageBox.information(self, "تم التصدير", f"حُفظت صفحة HTML في:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تصدير HTML:\n{e}")
