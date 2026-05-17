import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

INPUT_DIR = PROJECT_DIR / "Input"
DONE_DIR = PROJECT_DIR / "Done"
LOGS_DIR = PROJECT_DIR / "Logs"
WORK_DIR = PROJECT_DIR / "Work"
CONFIG_DIR = PROJECT_DIR / "config"
FAVORITE_CONFIG_FILE = CONFIG_DIR / "gui_favorite_config.json"

for folder in (INPUT_DIR, DONE_DIR, LOGS_DIR, WORK_DIR, CONFIG_DIR):
    folder.mkdir(parents=True, exist_ok=True)

TRANSCRIBE_PY = SCRIPT_DIR / "transcribe.py"

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".flac",
    ".ogg", ".wma", ".mp4", ".m4b", ".mov", ".mkv"
}

LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Persian / Farsi": "fa",
    "German": "de",
    "French": "fr",
    "Arabic": "ar",
    "Turkish": "tr",
    "Spanish": "es",
    "Italian": "it",
    "Dutch": "nl",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
}

DEFAULT_CONFIG = {
    "model": "large",
    "language": "Auto Detect",
    "srt": False,
    "vtt": False,
    "translate": False,
    "paragraph": False,
    "preprocess": False,
    "benchmark": False,
    "chunk_size": "Default (Auto)",
    "compute_type": "Auto (Recommended)",
    "thread_count": "Auto",
}

APP_QSS = """
QWidget {
    background-color: #0b1220;
    color: #f5f7fb;
    font-family: Segoe UI Variable, Segoe UI;
    font-size: 13px;
}

QFrame#HeaderFrame {
    background-color: #0d1728;
    border: 1px solid #1f2d44;
    border-radius: 16px;
}

QFrame#Panel {
    background-color: #121b2b;
    border: 1px solid #24344d;
    border-radius: 16px;
}

QLabel#Title {
    font-size: 27px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#Subtitle {
    font-size: 14px;
    color: #b9ff5a;
}

QLabel#SectionTitle {
    font-size: 15px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#Muted {
    color: #9aa7bd;
}

QPushButton {
    background-color: #172238;
    border: 1px solid #2e405e;
    border-radius: 11px;
    padding: 8px 14px;
    color: #f5f7fb;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #20304c;
    border: 1px solid #4aa3ff;
}

QPushButton:disabled {
    color: #6b7485;
    background-color: #121826;
    border: 1px solid #1e293b;
}

QPushButton#StartButton {
    background-color: #22a65a;
    border: 1px solid #34d17a;
    border-radius: 15px;
    font-size: 19px;
    font-weight: 900;
    padding: 10px;
}

QPushButton#StartButton:hover {
    background-color: #2cc46b;
}

QPushButton#ExitButton {
    background-color: #2a1420;
    border: 1px solid #ff5f6d;
    color: #ffffff;
    font-weight: 800;
}

QPushButton#ExitButton:hover {
    background-color: #8f1d2c;
    border: 1px solid #ff7a86;
}

QTextEdit {
    background-color: #0f1726;
    border: 1px solid #24344d;
    border-radius: 11px;
    padding: 8px;
    color: #dce7f7;
    font-size: 12px;
}

QTableWidget {
    background-color: #0f1726;
    border: 1px solid #24344d;
    border-radius: 11px;
    gridline-color: #26364e;
    color: #f5f7fb;
}

QHeaderView::section {
    background-color: #172238;
    color: #c8d4e8;
    border: none;
    padding: 6px;
    font-weight: 700;
}

QTableCornerButton::section {
    background-color: #172238;
    border: none;
}

QComboBox {
    background-color: #172238;
    border: 1px solid #2e405e;
    border-radius: 9px;
    padding: 7px;
    color: #f5f7fb;
}

QCheckBox {
    spacing: 9px;
    color: #f5f7fb;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 5px;
    border: 1px solid #60708a;
    background-color: #0f1726;
}

QCheckBox::indicator:checked {
    background-color: #34d17a;
    border: 1px solid #34d17a;
}

QLineEdit {
    background-color: #0f1726;
    border: 1px solid #2e405e;
    border-radius: 9px;
    padding: 8px;
    color: #f5f7fb;
}

QProgressBar {
    background-color: #0f1726;
    border: 1px solid #24344d;
    border-radius: 10px;
    height: 16px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #34d17a;
    border-radius: 9px;
}
"""


class ModelCard(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, key, title, subtitle, detail):
        super().__init__()
        self.key = key
        self.selected = False
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(72)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(13, 8, 13, 8)
        layout.setSpacing(2)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 800;
                border: none;
                background: transparent;
            }
        """)

        self.subtitle_label = QtWidgets.QLabel(subtitle)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #9aa7bd;
                font-size: 12px;
                border: none;
                background: transparent;
            }
        """)

        self.detail_label = QtWidgets.QLabel(detail)
        self.detail_label.setStyleSheet("""
            QLabel {
                color: #9aa7bd;
                font-size: 11px;
                border: none;
                background: transparent;
            }
        """)

        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.detail_label)

        self.update_style()

    def mousePressEvent(self, event):
        self.clicked.emit(self.key)

    def set_selected(self, selected):
        self.selected = selected
        self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #172238;
                    border: 2px solid #34d17a;
                    border-radius: 13px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #172238;
                    border: 1px solid #2e405e;
                    border-radius: 13px;
                }
            """)


class DropArea(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setAcceptDrops(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(150)

        self.setStyleSheet("""
            QFrame {
                background-color: #172238;
                border: 2px dashed #9aa7bd;
                border-radius: 16px;
            }
            QFrame:hover {
                border: 2px dashed #4aa3ff;
                background-color: #1b2941;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(3)

        icon = QtWidgets.QLabel("📁")
        icon.setAlignment(QtCore.Qt.AlignCenter)
        icon.setStyleSheet("font-size: 36px; border: none; background: transparent;")

        title = QtWidgets.QLabel("Drag & Drop Audio or Video Files Here")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 800; border: none; background: transparent;")

        browse = QtWidgets.QLabel("Browse Files")
        browse.setAlignment(QtCore.Qt.AlignCenter)
        browse.setStyleSheet("""
            QLabel {
                background-color: #1667a8;
                border: 1px solid #4aa3ff;
                border-radius: 8px;
                padding: 6px 18px;
                font-weight: 700;
            }
        """)

        formats = QtWidgets.QLabel("Supported: mp3, wav, m4a, flac, aac, mp4, mov, mkv, wma")
        formats.setAlignment(QtCore.Qt.AlignCenter)
        formats.setStyleSheet("color: #8f9db2; border: none; background: transparent; font-size: 11px;")

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(browse, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(formats)

    def mousePressEvent(self, event):
        self.parent_window.open_file_dialog()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.parent_window.add_files(files)
        event.acceptProposedAction()


class TranscribeGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("Offline Transcriber")
        self.setFixedSize(1450, 860)
        self.setStyleSheet(APP_QSS)

        self._drag_position = None

        self.process = None
        self.queue = []
        self.current_file = None
        self.cancel_requested = False
        self.selected_model = "large"
        self.output_folder = DONE_DIR

        self.build_ui()
        self.apply_config(DEFAULT_CONFIG)
        self.load_favorite_config_if_exists()
        self.refresh_existing_files()
        self.update_status_ready()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self._drag_position is not None:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        root.addWidget(self.build_header())

        content = QtWidgets.QWidget()
        main = QtWidgets.QHBoxLayout(content)
        main.setSpacing(14)
        main.setContentsMargins(0, 0, 0, 0)

        left_panel = self.build_left_panel()
        right_panel = self.build_right_panel()

        left_panel.setFixedWidth(690)
        right_panel.setFixedWidth(720)

        main.addWidget(left_panel)
        main.addWidget(right_panel)

        root.addWidget(content)
        root.addWidget(self.build_footer())

    def build_header(self):
        header = QtWidgets.QFrame()
        header.setObjectName("HeaderFrame")
        header.setFixedHeight(78)

        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20, 8, 20, 8)

        logo = QtWidgets.QLabel("▥")
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setFixedSize(52, 52)
        logo.setStyleSheet("""
            QLabel {
                background-color: #1b2a44;
                border-radius: 14px;
                color: #4aa3ff;
                font-size: 30px;
                font-weight: 900;
            }
        """)

        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(2)

        title = QtWidgets.QLabel("Offline Transcriber")
        title.setObjectName("Title")

        subtitle = QtWidgets.QLabel("100% Offline • Your Privacy, Your Data")
        subtitle.setObjectName("Subtitle")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        layout.addWidget(logo)
        layout.addLayout(title_box)
        layout.addStretch()

        self.settings_button = QtWidgets.QPushButton("⚙  Settings")
        self.settings_button.clicked.connect(self.show_settings)

        self.about_button = QtWidgets.QPushButton("ⓘ  About")
        self.about_button.clicked.connect(self.show_about)

        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.setObjectName("ExitButton")
        self.exit_button.setFixedWidth(72)
        self.exit_button.clicked.connect(self.close)

        layout.addWidget(self.settings_button)
        layout.addWidget(self.about_button)
        layout.addWidget(self.exit_button)

        return header

    def build_left_panel(self):
        panel = QtWidgets.QFrame()
        panel.setObjectName("Panel")

        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(7)

        self.drop_area = DropArea(self)
        layout.addWidget(self.drop_area)

        self.file_table = QtWidgets.QTableWidget(0, 6)
        self.file_table.setHorizontalHeaderLabels(["", "File", "Duration", "Size", "Type", "Status"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.file_table.setColumnWidth(0, 42)
        self.file_table.setColumnWidth(2, 90)
        self.file_table.setColumnWidth(3, 85)
        self.file_table.setColumnWidth(4, 70)
        self.file_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.file_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.file_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #172238;
                color: #c8d4e8;
                border: none;
            }
        """)
        self.file_table.setStyleSheet(self.file_table.styleSheet() + """
            QTableCornerButton::section {
                background-color: #172238;
                border: none;
            }
        """)
        self.file_table.setFixedHeight(158)

        self.select_all_checkbox = QtWidgets.QCheckBox("")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all_files)
        self.file_table.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem(""))
        self.file_table.setCellWidget(-1 if False else 0, 0, None)

        layout.addWidget(self.file_table)

        self.place_select_all_over_header()

        log_title = QtWidgets.QLabel("Activity Log")
        log_title.setObjectName("SectionTitle")
        layout.addWidget(log_title)

        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(76)
        layout.addWidget(self.log_box)

        out_label = QtWidgets.QLabel("Output Folder")
        out_label.setObjectName("SectionTitle")

        out_row = QtWidgets.QHBoxLayout()

        self.output_path_edit = QtWidgets.QLineEdit(str(self.output_folder))
        self.output_path_edit.setReadOnly(True)

        self.open_done_button = QtWidgets.QPushButton("Open")
        self.open_done_button.clicked.connect(self.open_done_folder)

        out_row.addWidget(self.output_path_edit)
        out_row.addWidget(self.open_done_button)

        layout.addWidget(out_label)
        layout.addLayout(out_row)

        self.status_box = QtWidgets.QFrame()
        self.status_box.setObjectName("Panel")
        self.status_box.setFixedHeight(62)

        status_layout = QtWidgets.QHBoxLayout(self.status_box)

        self.status_icon = QtWidgets.QLabel("✓")
        self.status_icon.setAlignment(QtCore.Qt.AlignCenter)
        self.status_icon.setFixedSize(40, 40)
        self.status_icon.setStyleSheet("""
            QLabel {
                color: #34d17a;
                border: 2px solid #34d17a;
                border-radius: 20px;
                font-size: 22px;
                font-weight: 900;
            }
        """)

        status_text_box = QtWidgets.QVBoxLayout()
        status_text_box.setSpacing(2)

        self.status_title = QtWidgets.QLabel("Ready to transcribe")
        self.status_title.setStyleSheet("font-size: 15px; font-weight: 800;")

        self.status_detail = QtWidgets.QLabel("No files loaded")
        self.status_detail.setObjectName("Muted")

        status_text_box.addWidget(self.status_title)
        status_text_box.addWidget(self.status_detail)

        status_layout.addWidget(self.status_icon)
        status_layout.addLayout(status_text_box)
        status_layout.addStretch()

        layout.addWidget(self.status_box)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        layout.addWidget(self.progress_bar)

        self.start_button = QtWidgets.QPushButton("▶  START TRANSCRIPTION")
        self.start_button.setObjectName("StartButton")
        self.start_button.clicked.connect(self.start_transcription)
        layout.addWidget(self.start_button)

        control_row = QtWidgets.QHBoxLayout()

        self.pause_button = QtWidgets.QPushButton("Pause")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_resume)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_transcription)

        control_row.addWidget(self.pause_button)
        control_row.addWidget(self.cancel_button)

        layout.addLayout(control_row)

        return panel

    def place_select_all_over_header(self):
        self.select_all_checkbox.setParent(self.file_table)

        # Align the Select All checkbox exactly with the row checkboxes.
        # QTableWidget has a vertical row-number header on the left, so the
        # header checkbox must be shifted by that header width first.
        vertical_header_width = self.file_table.verticalHeader().width()
        if vertical_header_width < 20:
            vertical_header_width = 26

        checkbox_box_width = 24
        x = vertical_header_width + int((self.file_table.columnWidth(0) - checkbox_box_width) / 2)
        y = 7

        self.select_all_checkbox.move(x, y)
        self.select_all_checkbox.resize(checkbox_box_width, 24)
        self.select_all_checkbox.setText("")
        self.select_all_checkbox.setStyleSheet("""
            QCheckBox {
                background-color: #172238;
                border: none;
                padding: 0px;
                margin: 0px;
            }

            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border-radius: 5px;
                border: 1px solid #60708a;
                background-color: #172238;
            }

            QCheckBox::indicator:checked {
                background-color: #34d17a;
                border: 1px solid #34d17a;
            }
        """)
        self.select_all_checkbox.show()

    def build_right_panel(self):
        panel = QtWidgets.QFrame()
        panel.setObjectName("Panel")

        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(5)

        title1 = QtWidgets.QLabel("1. Choose Model")
        title1.setObjectName("SectionTitle")
        layout.addWidget(title1)

        card_row = QtWidgets.QHBoxLayout()

        self.small_card = ModelCard("small", "Small", "Fastest", "Quick results")
        self.medium_card = ModelCard("medium", "Medium", "Balanced", "Better accuracy")
        self.large_card = ModelCard("large", "Large", "Best Accuracy", "Highest quality")

        for card in (self.small_card, self.medium_card, self.large_card):
            card.clicked.connect(self.select_model)
            card_row.addWidget(card)

        layout.addLayout(card_row)

        layout.addWidget(self.divider())

        title2 = QtWidgets.QLabel("2. Language")
        title2.setObjectName("SectionTitle")
        layout.addWidget(title2)

        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(list(LANGUAGES.keys()))
        layout.addWidget(self.language_combo)

        layout.addWidget(self.divider())

        title3 = QtWidgets.QLabel("3. Options")
        title3.setObjectName("SectionTitle")
        layout.addWidget(title3)

        self.srt_checkbox = QtWidgets.QCheckBox("Generate Subtitles (SRT)")
        self.srt_checkbox.stateChanged.connect(self.update_translation_options)
        self.vtt_checkbox = QtWidgets.QCheckBox("Generate WebVTT (VTT)")
        self.vtt_checkbox.stateChanged.connect(self.update_translation_options)
        self.translate_checkbox = QtWidgets.QCheckBox("Translate to English")
        self.translate_checkbox.stateChanged.connect(self.update_translation_options)
        self.paragraph_checkbox = QtWidgets.QCheckBox("Paragraph Formatting")
        self.preprocess_checkbox = QtWidgets.QCheckBox("Preprocess Audio (Improve Quality)")
        self.benchmark_checkbox = QtWidgets.QCheckBox("Benchmark (Show Performance)")

        layout.addWidget(self.srt_checkbox)
        layout.addWidget(self.vtt_checkbox)
        layout.addWidget(self.translate_checkbox)

        trans_row = QtWidgets.QHBoxLayout()
        trans_row.addWidget(QtWidgets.QLabel("Translation Language:"))

        
        # Option: Translate without transcription
        self.translate_only_checkbox = QtWidgets.QCheckBox("Translate without transcription")
        self.translate_only_checkbox.setChecked(False)
        self.translate_only_checkbox.stateChanged.connect(self.update_translation_options)
        self.translate_only_checkbox.setChecked(False)
        layout.addWidget(self.translate_only_checkbox)
    

        layout.addWidget(self.paragraph_checkbox)
        layout.addWidget(self.preprocess_checkbox)
        layout.addWidget(self.benchmark_checkbox)

        layout.addWidget(self.divider())

        title4 = QtWidgets.QLabel("4. Advanced (Optional)")
        title4.setObjectName("SectionTitle")
        layout.addWidget(title4)

        self.chunk_combo = QtWidgets.QComboBox()
        self.chunk_combo.addItems(["Default (Auto)", "Short", "Medium", "Long"])

        self.compute_combo = QtWidgets.QComboBox()
        self.compute_combo.addItems(["Auto (Recommended)", "CPU", "CUDA / GPU"])

        self.thread_combo = QtWidgets.QComboBox()
        self.thread_combo.addItems(["Auto", "2", "4", "8"])

        layout.addLayout(self.option_row("Chunk Size", self.chunk_combo))
        layout.addLayout(self.option_row("Compute Type", self.compute_combo))
        layout.addLayout(self.option_row("Thread Count", self.thread_combo))

        config_row = QtWidgets.QHBoxLayout()

        self.save_favorite_button = QtWidgets.QPushButton("Save Favorite Config")
        self.save_favorite_button.clicked.connect(self.save_favorite_config)

        self.reset_default_button = QtWidgets.QPushButton("Reset Default Config")
        self.reset_default_button.clicked.connect(self.reset_default_config)

        config_row.addWidget(self.save_favorite_button)
        config_row.addWidget(self.reset_default_button)

        layout.addLayout(config_row)

        privacy = QtWidgets.QFrame()
        privacy.setStyleSheet("""
            QFrame {
                background-color: #10223a;
                border: 1px solid #1c76b8;
                border-radius: 10px;
            }
        """)

        privacy_layout = QtWidgets.QVBoxLayout(privacy)
        privacy_layout.setSpacing(3)

        privacy_title = QtWidgets.QLabel("🔒  100% Offline")
        privacy_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #4aa3ff;")

        privacy_text = QtWidgets.QLabel("All processing happens on your device.\nYour files never leave your computer.")
        privacy_text.setStyleSheet("color: #c8d4e8;")

        privacy_layout.addWidget(privacy_title)
        privacy_layout.addWidget(privacy_text)

        layout.addWidget(privacy)

        return panel

    def build_footer(self):
        footer = QtWidgets.QFrame()
        footer.setFixedHeight(30)
        footer.setStyleSheet("background-color: #0d1728; border-radius: 10px;")

        layout = QtWidgets.QHBoxLayout(footer)
        layout.setContentsMargins(16, 0, 16, 0)

        version = QtWidgets.QLabel("v1.3.6")

        offline = QtWidgets.QLabel("●  MIT License")
        offline.setStyleSheet("color: #34d17a; font-weight: 700;")

        cpu = QtWidgets.QLabel("CPU: Ready")
        mem = QtWidgets.QLabel("Memory: Ready")
        tip = QtWidgets.QLabel("Tips: Larger models need more RAM  ⓘ")

        for w in (version, cpu, mem, tip):
            w.setStyleSheet("color: #b7c2d6;")

        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(offline)
        layout.addStretch()
        layout.addWidget(cpu)
        layout.addSpacing(28)
        layout.addWidget(mem)
        layout.addStretch()
        layout.addWidget(tip)

        return footer

    def divider(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("background-color: #24344d; max-height: 1px;")
        return line

    def option_row(self, label, widget):
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel(label))
        row.addWidget(widget)
        return row

    def show_settings(self):
        QtWidgets.QMessageBox.information(self, "Settings", "Settings panel will be added later.")

        
    def show_about(self):
        QtWidgets.QMessageBox.information(
            self,
            "About",
            """This Transcriber is an open-source tool for accurate transcription of audio/video recordings into text. It supports a wide range of common formats and can optionally translate transcripts into English.

After the initial installation, all transcription runs fully offline without requiring an internet connection.

This tool is especially useful for:
• Students and academic researchers transcribing interviews
• Journalists handling sensitive recordings
• Professionals working with confidential audio/video data
• Anyone who needs privacy-preserving offline speech-to-text transcription

Developed by Abbas SALAMAT
Abbas.salamat@edu.donau-uni.ac.at
Suggestions, improvements, bug reports, and contributions are welcome.
For more information https://github.com/Salamatabbas/offline-transcriber/"""
        )



    def update_translation_options(self):
        # Disable translate_only_checkbox if translate_checkbox is checked or SRT/VTT is checked
        if self.translate_checkbox.isChecked() or self.srt_checkbox.isChecked() or self.vtt_checkbox.isChecked():
            self.translate_only_checkbox.setEnabled(False)
            self.translate_only_checkbox.setStyleSheet("color: #6b7485")
            if self.translate_only_checkbox.isChecked():
                self.translate_only_checkbox.setChecked(False)
        else:
            self.translate_only_checkbox.setEnabled(True)
            self.translate_only_checkbox.setStyleSheet("color: #f5f7fb")

        # Disable translate_checkbox if translate_only_checkbox is checked
        if self.translate_only_checkbox.isChecked():
            self.translate_checkbox.setEnabled(False)
            self.translate_checkbox.setStyleSheet("color: #6b7485")
        else:
            self.translate_checkbox.setEnabled(True)
            self.translate_checkbox.setStyleSheet("color: #f5f7fb")

        return {
            "model": self.selected_model,
            "language": self.language_combo.currentText(),
            "srt": self.srt_checkbox.isChecked(),
            "vtt": self.vtt_checkbox.isChecked(),
            "translate": self.translate_checkbox.isChecked(),
            "paragraph": self.paragraph_checkbox.isChecked(),
            "preprocess": self.preprocess_checkbox.isChecked(),
            "benchmark": self.benchmark_checkbox.isChecked(),
            "chunk_size": self.chunk_combo.currentText(),
            "compute_type": self.compute_combo.currentText(),
            "thread_count": self.thread_combo.currentText(),
        }

    
    def get_current_config(self):
        return {
            "model": self.selected_model,
            "language": self.language_combo.currentText(),
            "srt": self.srt_checkbox.isChecked(),
            "vtt": self.vtt_checkbox.isChecked(),
            "translate": self.translate_checkbox.isChecked(),
            "translate_only": self.translate_only_checkbox.isChecked(),
            "paragraph": self.paragraph_checkbox.isChecked(),
            "preprocess": self.preprocess_checkbox.isChecked(),
            "benchmark": self.benchmark_checkbox.isChecked(),
            "chunk_size": self.chunk_combo.currentText(),
            "compute_type": self.compute_combo.currentText(),
            "thread_count": self.thread_combo.currentText()
        }


    def apply_config(self, config):
        self.select_model(config.get("model", "large"))

        language = config.get("language", "Auto Detect")
        index = self.language_combo.findText(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        self.srt_checkbox.setChecked(config.get("srt", False))
        self.vtt_checkbox.setChecked(config.get("vtt", False))
        self.translate_checkbox.setChecked(config.get("translate", False))
        self.paragraph_checkbox.setChecked(config.get("paragraph", False))
        self.preprocess_checkbox.setChecked(config.get("preprocess", False))
        self.benchmark_checkbox.setChecked(config.get("benchmark", False))

        chunk = config.get("chunk_size", "Default (Auto)")
        chunk_index = self.chunk_combo.findText(chunk)
        if chunk_index >= 0:
            self.chunk_combo.setCurrentIndex(chunk_index)

        compute = config.get("compute_type", "Auto (Recommended)")
        compute_index = self.compute_combo.findText(compute)
        if compute_index >= 0:
            self.compute_combo.setCurrentIndex(compute_index)

        thread = config.get("thread_count", "Auto")
        thread_index = self.thread_combo.findText(thread)
        if thread_index >= 0:
            self.thread_combo.setCurrentIndex(thread_index)

    def save_favorite_config(self):
        try:
            config_path = FAVORITE_CONFIG_FILE
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config = self.get_current_config()
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.log("Favorite config saved: " + str(FAVORITE_CONFIG_FILE))
        except Exception as e:
            self.log("ERROR saving favorite config: " + str(e))


    def load_favorite_config_if_exists(self):
        if not FAVORITE_CONFIG_FILE.exists():
            return

        try:
            with open(FAVORITE_CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.apply_config(config)
            self.log("Favorite config loaded.")
        except Exception:
            pass

    def reset_default_config(self):
        self.apply_config(DEFAULT_CONFIG)
        self.log("Default config restored.")

    def select_model(self, model):
        self.selected_model = model
        self.small_card.set_selected(model == "small")
        self.medium_card.set_selected(model == "medium")
        self.large_card.set_selected(model == "large")

    def log(self, message):
        self.log_box.append(str(message))

    def get_unique_path(self, path):
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        counter = 2

        while True:
            candidate = path.parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def scan_input(self):
        return sorted(
            f for f in INPUT_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
        )

    def refresh_existing_files(self):
        self.file_table.setRowCount(0)

        files = self.scan_input()

        for f in files:
            self.add_file_to_table(f, checked=True)

        self.update_status_ready()

    def make_table_checkbox(self, checked=True):
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        checkbox = QtWidgets.QCheckBox()
        checkbox.setChecked(checked)
        checkbox.stateChanged.connect(self.update_status_ready)

        layout.addWidget(checkbox)
        wrapper.checkbox = checkbox

        return wrapper

    def add_file_to_table(self, path, checked=True):
        row = self.file_table.rowCount()
        self.file_table.insertRow(row)

        check_widget = self.make_table_checkbox(checked)
        self.file_table.setCellWidget(row, 0, check_widget)

        icon = "🎬 " if path.suffix.lower() in {".mp4", ".mov", ".mkv"} else "🎵 "

        name_item = QtWidgets.QTableWidgetItem(icon + path.stem)
        name_item.setData(QtCore.Qt.UserRole, str(path))

        duration_item = QtWidgets.QTableWidgetItem(self.get_media_duration(path))
        size_item = QtWidgets.QTableWidgetItem(self.format_size(path.stat().st_size))
        type_item = QtWidgets.QTableWidgetItem(path.suffix.lower().replace(".", "").upper())
        status_item = QtWidgets.QTableWidgetItem("✓ Ready")

        status_item.setForeground(QtGui.QColor("#34d17a"))

        self.file_table.setItem(row, 1, name_item)
        self.file_table.setItem(row, 2, duration_item)
        self.file_table.setItem(row, 3, size_item)
        self.file_table.setItem(row, 4, type_item)
        self.file_table.setItem(row, 5, status_item)

    def get_media_duration(self, path):
        ffprobe_path = shutil.which("ffprobe") or r"C:\ffmpeg\bin\ffprobe.exe"

        try:
            result = subprocess.run(
                [
                    ffprobe_path,
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(path)
                ],
                capture_output=True,
                text=True,
                timeout=8
            )

            value = result.stdout.strip()

            if not value:
                return "--:--"

            total_seconds = int(float(value))
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            return f"{minutes}:{seconds:02d}"

        except Exception:
            return "--:--"

    def format_size(self, size):
        mb = size / (1024 * 1024)
        return f"{mb:.1f} MB"

    def toggle_select_all_files(self, state):
        checked = state == QtCore.Qt.Checked

        for row in range(self.file_table.rowCount()):
            widget = self.file_table.cellWidget(row, 0)
            if widget and hasattr(widget, "checkbox"):
                widget.checkbox.blockSignals(True)
                widget.checkbox.setChecked(checked)
                widget.checkbox.blockSignals(False)

        self.update_status_ready()

    def get_selected_files(self):
        selected = []

        for row in range(self.file_table.rowCount()):
            widget = self.file_table.cellWidget(row, 0)

            if not widget or not hasattr(widget, "checkbox"):
                continue

            if not widget.checkbox.isChecked():
                continue

            item = self.file_table.item(row, 1)

            if not item:
                continue

            path = Path(item.data(QtCore.Qt.UserRole))

            if path.exists():
                selected.append(path)

        return selected

    def open_file_dialog(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select audio/video files",
            str(PROJECT_DIR),
            "Audio/Video Files (*.mp3 *.wav *.m4a *.aac *.flac *.ogg *.wma *.mp4 *.m4b *.mov *.mkv)"
        )

        if files:
            self.add_files(files)

    def add_files(self, files):
        added = 0

        for file in files:
            src = Path(file)

            if not src.exists() or not src.is_file():
                continue

            if src.suffix.lower() not in AUDIO_EXTENSIONS:
                self.log(f"Skipped unsupported file: {src.name}")
                continue

            dest = INPUT_DIR / src.name
            dest = self.get_unique_path(dest)

            shutil.copy2(src, dest)
            added += 1

            self.add_file_to_table(dest, checked=True)

        if added:
            self.log(f"{added} file(s) added to Input.")
            self.select_all_checkbox.setChecked(True)
            self.update_status_ready()
        else:
            self.log("No valid audio/video files were added.")

    def update_status_ready(self):
        total_count = self.file_table.rowCount()
        selected_count = len(self.get_selected_files()) if hasattr(self, "file_table") else 0

        if hasattr(self, "select_all_checkbox"):
            self.select_all_checkbox.blockSignals(True)
            self.select_all_checkbox.setChecked(total_count > 0 and selected_count == total_count)
            self.select_all_checkbox.blockSignals(False)

        if total_count:
            self.status_icon.setText("✓")
            self.status_title.setText("Ready to transcribe")
            self.status_detail.setText(f"{selected_count} selected / {total_count} loaded • Click START to begin")
        else:
            self.status_icon.setText("!")
            self.status_title.setText("Waiting for files")
            self.status_detail.setText("Drag & drop files or click Browse Files")

    def change_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Choose Output Folder",
            str(self.output_folder)
        )

        if folder:
            self.output_folder = Path(folder)
            self.output_path_edit.setText(str(self.output_folder))
            self.log(f"Output folder changed to: {self.output_folder}")

    def open_done_folder(self):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(self.output_folder)))

    def start_progress_animation(self):
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFormat("")

    def stop_progress_animation(self, final_value=100, final_text=""):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(final_value)
        self.progress_bar.setFormat(final_text)

    def set_running_ui(self, running):
        self.start_button.setEnabled(not running)
        self.drop_area.setEnabled(not running)
        self.select_all_checkbox.setEnabled(not running)
        self.open_done_button.setEnabled(not running)
        self.save_favorite_button.setEnabled(not running)
        self.reset_default_button.setEnabled(not running)

        self.small_card.setEnabled(not running)
        self.medium_card.setEnabled(not running)
        self.large_card.setEnabled(not running)

        self.language_combo.setEnabled(not running)
        self.srt_checkbox.setEnabled(not running)
        self.vtt_checkbox.setEnabled(not running)
        self.translate_checkbox.setEnabled(not running)
        self.paragraph_checkbox.setEnabled(not running)
        self.preprocess_checkbox.setEnabled(not running)
        self.benchmark_checkbox.setEnabled(not running)
        self.chunk_combo.setEnabled(not running)
        self.compute_combo.setEnabled(not running)
        self.thread_combo.setEnabled(not running)

        for row in range(self.file_table.rowCount()):
            widget = self.file_table.cellWidget(row, 0)
            if widget and hasattr(widget, "checkbox"):
                widget.checkbox.setEnabled(not running)

        self.pause_button.setEnabled(running)
        self.cancel_button.setEnabled(running)

        if not running:
            self.pause_button.setText("Pause")

    def start_transcription(self):
        try:
            if self.process is not None:
                self.log("Transcription is already running.")
                return

            if not TRANSCRIBE_PY.exists():
                self.log(f"ERROR: transcribe.py not found: {TRANSCRIBE_PY}")
                return

            selected_files = self.get_selected_files()

            if not selected_files:
                self.log("No files selected for transcription.")
                return

            self.queue = [f.name for f in selected_files]

            self.cancel_requested = False
            self.start_progress_animation()
            self.set_running_ui(True)

            self.status_icon.setText("…")
            self.status_title.setText("Processing...")
            self.status_detail.setText("Please wait while transcription is running")

            self.log("Starting transcription...")
            self.log(f"Model: {self.selected_model}")
            self.log(f"Language: {self.language_combo.currentText()}")
            self.log(f"SRT: {'enabled' if self.srt_checkbox.isChecked() else 'disabled'}")
            self.log(f"VTT: {'enabled' if self.vtt_checkbox.isChecked() else 'disabled'}")
            self.log(f"Translate: {'enabled' if self.translate_checkbox.isChecked() else 'disabled'}")
            self.log(f"{len(self.queue)} selected file(s) found.")
            self.log("")

            self.run_next_file()

        except Exception as e:
            self.log(f"GUI ERROR while starting transcription: {e}")
            self.finish_error()

    def run_next_file(self):
        if self.cancel_requested:
            self.finish_cancelled()
            return

        if not self.queue:
            self.finish_success()
            return

        filename = self.queue.pop(0)
        self.current_file = filename

        args = [
            str(TRANSCRIBE_PY),
            "-single",
            filename,
            f"-{self.selected_model}",
            "-force"
        ]

        language_code = LANGUAGES.get(self.language_combo.currentText(), "auto")

        if language_code != "auto":
            args.append(f"-{language_code}")

        if self.srt_checkbox.isChecked():
            args.append("-srt")

        if self.vtt_checkbox.isChecked():
            args.append("-vtt")

        
        # Determine translation mode
        if getattr(self, 'translate_only_checkbox', None) and self.translate_only_checkbox.isChecked():
            args.append("-translate_only")
        elif self.translate_checkbox.isChecked():
            args.append("-translate")
    

        if self.preprocess_checkbox.isChecked():
            args.append("-preprocess")

        if self.benchmark_checkbox.isChecked():
            args.append("--benchmark")

        compute = self.compute_combo.currentText()

        if compute == "CPU":
            args.append("-cpu")
        elif compute == "CUDA / GPU":
            args.append("-cuda")

        self.log(f"Processing: {filename}")

        self.process = QtCore.QProcess(self)

        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("KMP_DUPLICATE_LIB_OK", "TRUE")
        env.insert("PATH", r"C:\ffmpeg\bin;" + env.value("PATH"))

        self.process.setProcessEnvironment(env)
        self.process.setWorkingDirectory(str(SCRIPT_DIR))

        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)

        self.process.start(sys.executable, args)

        if not self.process.waitForStarted(3000):
            self.log(f"ERROR: Could not start transcription for {filename}")
            self.process = None
            self.finish_error()

    def read_stdout(self):
        if not self.process:
            return

        text = bytes(self.process.readAllStandardOutput()).decode(errors="replace")

        for line in text.splitlines():
            if line.strip():
                self.log(line)

    def read_stderr(self):
        if not self.process:
            return

        text = bytes(self.process.readAllStandardError()).decode(errors="replace")

        for line in text.splitlines():
            if line.strip():
                self.log("ERROR: " + line)

    def process_finished(self, exit_code, exit_status):
        finished_file = self.current_file

        self.process = None
        self.current_file = None

        if self.cancel_requested:
            self.finish_cancelled()
            return

        if exit_code == 0:
            self.log(f"Finished: {finished_file}")
            self.log("")
            self.run_next_file()
        else:
            self.log(f"ERROR: Transcription failed for {finished_file}")
            self.log(f"Exit code: {exit_code}")
            self.finish_error()

    def pause_resume(self):
        if self.process is None:
            return

        pid = self.process.processId()

        if not pid:
            self.log("Pause/Resume is not available.")
            return

        if self.pause_button.text() == "Pause":
            QtCore.QProcess.execute(
                "powershell",
                ["-NoProfile", "-Command", f"Suspend-Process -Id {pid}"]
            )

            self.pause_button.setText("Resume")
            self.log("Paused.")
        else:
            QtCore.QProcess.execute(
                "powershell",
                ["-NoProfile", "-Command", f"Resume-Process -Id {pid}"]
            )

            self.pause_button.setText("Pause")
            self.log("Resumed.")

    def cancel_transcription(self):
        self.cancel_requested = True

        if self.process is not None:
            self.process.kill()
            self.process = None

        self.finish_cancelled()

    def copy_outputs_if_custom_folder(self):
        if self.output_folder.resolve() == DONE_DIR.resolve():
            return

        self.output_folder.mkdir(parents=True, exist_ok=True)

        for item in DONE_DIR.iterdir():
            if item.is_file():
                try:
                    shutil.copy2(item, self.output_folder / item.name)
                except Exception:
                    pass

    def finish_success(self):
        self.stop_progress_animation(100, "Completed")
        self.copy_outputs_if_custom_folder()
        self.set_running_ui(False)

        self.status_icon.setText("✓")
        self.status_title.setText("Completed")
        self.status_detail.setText("Outputs are ready")

        self.log("Transcription completed successfully.")
        self.log(f"Outputs saved in: {self.output_folder}")

    def finish_cancelled(self):
        self.stop_progress_animation(0, "Cancelled")
        self.set_running_ui(False)
        self.queue.clear()

        self.status_icon.setText("!")
        self.status_title.setText("Cancelled")
        self.status_detail.setText("Transcription was cancelled")

        self.log("Transcription cancelled.")

    def finish_error(self):
        self.stop_progress_animation(0, "Error")
        self.set_running_ui(False)

        self.status_icon.setText("!")
        self.status_title.setText("Error")
        self.status_detail.setText("Transcription stopped because of an error")

        self.log("Transcription stopped because of an error.")


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    font = QtGui.QFont("Segoe UI Variable", 10)
    font.setHintingPreference(QtGui.QFont.PreferFullHinting)
    app.setFont(font)

    window = TranscribeGUI()
    window.show()
    sys.exit(app.exec_())