import sys
import os
import tempfile
import shutil
import json
import zipfile
import stat
import uuid
import re
import subprocess
import patoolib
import ctypes

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from qfluentwidgets import setFont, PrimaryPushButton, PushButton, Action, RoundMenu, LineEdit, setTheme, Theme, EditableComboBox, CheckBox, InfoBar, InfoBarPosition, InfoBarIcon, ProgressRing, CompactSpinBox, ToolButton, TogglePushButton, FlowLayout, TreeView, MessageBoxBase, SubtitleLabel, StateToolTip
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import (QMessageBox, QApplication, QWidget, QLabel, QDialog, QVBoxLayout, QFileDialog, QCompleter, QHBoxLayout, QFileSystemModel, QShortcut)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QEasingCurve, QUrl, QSettings, QTimer, QRegularExpression
from PyQt5.QtGui import QPixmap, QCursor, QDesktopServices, QIcon, QKeySequence, QIntValidator, QRegularExpressionValidator
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from PIL import Image, ImageOps
from concurrent.futures import ThreadPoolExecutor

from utils import (
    resource_path, documents_dir, downloads_dir, DOC_MAIN_DIR,
    suppress_cmd_window, get_optimal_workers, calculate_total_files,
    tooltip_stylesheet, label_stylesheet,
    show_warning, show_success, show_error, show_info
)
from logger_utils import get_logger, set_level
from widgets import (
    ProductLineEdit, TagSelectionDialog, CustomCompactSpinBox, ImageLabel,
    ZipThread, NameEntryDialog, CustomTreeView, FileExplorer
)
from config_utils import load_configurations
from settings import SettingsDialog
from updater import UpdateManager
from version import APP_VERSION

log = get_logger(__name__)
log.info("Application starting...")

settings = QSettings("Syst3mApps", "DIMCreator")

documents_path = documents_dir()
doc_main_dir = DOC_MAIN_DIR
logo_path = resource_path(os.path.join('assets', 'images', 'logo', 'favicon.ico'))

class DIMPackageGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.doc_main_dir = doc_main_dir
        self.storeitems, self.store_prefixes, self.available_tags, self.daz_folders = load_configurations(self.doc_main_dir)
        self.stateTooltip = None
        self.ensure_directory_structure()
        setTheme(Theme.DARK)
        self.initUI()
        self.loadSettings()
        self.updater = UpdateManager(self, settings, current_version=APP_VERSION, interval_hours=24)
        self.updater.schedule_on_startup_if_enabled()
        QTimer.singleShot(0, self.updateSourcePrefixBasedOnStore)
        self._extractionHadError = False


    def loadSettings(self):
        self.prefix_input.setText(settings.value("prefix_input", "", type=str))
        self.product_tags_input.setText(settings.value("product_tags_input", "DAZStudio4_5", type=str))
        self.last_destination_folder = settings.value("last_destination_folder", os.path.expanduser("~"), type=str)
        self.copy_template_files = settings.value("copy_template_files", False, type=bool)
        self.template_destination = settings.value("template_destination", "", type=str)

    def saveSettings(self):
        settings.setValue("prefix_input", self.prefix_input.text())
        settings.setValue("product_tags_input", self.product_tags_input.text())
        settings.setValue("last_destination_folder", self.last_destination_folder)

    def closeEvent(self, event):
        try:
            if self.stateTooltip:
                self.stateTooltip.close()
                self.stateTooltip.deleteLater()
                self.stateTooltip = None
        except Exception:
            pass
    
        self.saveSettings()
        self.cleanDIMBuildFolder()
        self.cleanUpTemporaryImage()
        super().closeEvent(event)

    def ensure_directory_structure(self):
        self.dimbuild_dir = os.path.join(doc_main_dir, "DIMBuild")
        self.content_dir = os.path.join(self.dimbuild_dir, "Content")
        os.makedirs(self.content_dir, exist_ok=True)

    def cleanUpTemporaryImage(self):
        try:
            if getattr(self, 'image_label', None) and self.image_label.imagePath:
                if getattr(self.image_label, "_ownedTemp", False):
                    image_path = self.image_label.imagePath
                    try:
                        os.remove(image_path)
                        log.info(f"Temporary image file deleted: {image_path}")
                    except OSError as e:
                        log.error(f"Error deleting temporary image file '{image_path}': {e}")
                self.image_label.removeImage()
        except Exception as e:
            log.error(f"cleanUpTemporaryImage failed: {e}")

    def openTagSelectionDialog(self):
        selected_tags = self.product_tags_input.text().split(",")

        dialog = TagSelectionDialog(self.available_tags, selected_tags, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_tags = dialog.getSelectedTags()
            self.product_tags_input.setText(",".join(selected_tags))

    def updateTagsInput(self, tag, checked):
        current_tags = self.product_tags_input.text().split(',')
        if checked and tag not in current_tags:
            current_tags.append(tag)
        elif not checked and tag in current_tags:
            current_tags.remove(tag)
        self.product_tags_input.setText(','.join(current_tags))

    def updateSourcePrefixBasedOnStore(self):
        use_store_prefix = self.use_store_prefix_checkbox.isChecked()
        self.prefix_input.setEnabled(not use_store_prefix)
        
        if use_store_prefix:
            selected_store = self.store_input.currentText()
            store_prefix = self.store_prefixes.get(selected_store, "")
            self.prefix_input.setText(store_prefix)

    def initUI(self):
        self.setWindowTitle('DIMCreator')
        self.setFixedSize(780, 690)

        self.setStyleSheet(tooltip_stylesheet + "DIMPackageGUI{background: rgb(32, 32, 32)}")

        store_label = QLabel('Store:', self)
        store_label.setGeometry(20, 20, 100, 30)
        store_label.setStyleSheet(label_stylesheet)
        self.store_input = EditableComboBox(self)
        self.store_input.setGeometry(130, 20, 250, 30)
        self.store_input.addItems(self.storeitems)
        self.store_completer = QCompleter(self.storeitems, self)
        self.store_input.setCompleter(self.store_completer)
        self.store_input.setMaxVisibleItems(10)
        self.store_input.setToolTip("Select the store from which the product was purchased.")
        self.store_input.currentIndexChanged.connect(self.updateSourcePrefixBasedOnStore)

        prefix_label = QLabel('Source Prefix:', self)
        prefix_label.setGeometry(20, 60, 100, 30)
        prefix_label.setStyleSheet(label_stylesheet)
        self.prefix_input = LineEdit(self)
        self.prefix_input.setGeometry(130, 60, 250, 30)
        self.prefix_input.setClearButtonEnabled(True)
        self.prefix_input.setPlaceholderText('IM')
        self.prefix_input.setToolTip("Enter the source prefix, typically the vendor's initials.")

        self.use_store_prefix_checkbox = CheckBox('Auto Prefix', self)
        self.use_store_prefix_checkbox.setGeometry(390, 60, 150, 30)
        self.use_store_prefix_checkbox.stateChanged.connect(self.updateSourcePrefixBasedOnStore)
        self.prefix_input.setEnabled(not self.use_store_prefix_checkbox.isChecked())

        product_name_label = QLabel('Product Name:', self)
        product_name_label.setGeometry(20, 100, 100, 30)
        product_name_label.setStyleSheet(label_stylesheet)
        self.product_name_input = ProductLineEdit(self)
        self.product_name_input.setGeometry(130, 100, 250, 30) 
        self.product_name_input.setClearButtonEnabled(True)
        self.product_name_input.setPlaceholderText('dForce Starter Essentials')
        self.product_name_input.setToolTip("Enter the name of the product.")

        sku_label = QLabel('Package SKU:', self)
        sku_label.setGeometry(20, 140, 100, 30)
        sku_label.setStyleSheet(label_stylesheet)
        self.sku_input = LineEdit(self)
        self.sku_input.setGeometry(130, 140, 175, 30)
        self.sku_input.setClearButtonEnabled(True)
        self.sku_input.setPlaceholderText('47939')
        self.sku_input.setMaxLength(8)
        self.sku_input.setValidator(QIntValidator(0, 99999999, self))
        self.sku_input.setToolTip("Enter the SKU (Stock Keeping Unit) for the package.")

        sku_part_line = QLabel('-', self)
        sku_part_line.setGeometry(310, 140, 10, 30)
        sku_part_line.setStyleSheet(label_stylesheet)

        self.product_part_input = CustomCompactSpinBox(self)
        self.product_part_input.setGeometry(320, 140, 60, 30)
        self.product_part_input.setRange(1, 99)
        self.product_part_input.setValue(1)

        guid_label = QLabel('Package GUID:', self)
        guid_label.setGeometry(20, 180, 100, 30)
        guid_label.setStyleSheet(label_stylesheet)
        self.guid_input = LineEdit(self)
        self.guid_input.setGeometry(130, 180, 210, 30)
        self.guid_input.setClearButtonEnabled(True)
        self.guid_input.setPlaceholderText('a4a82911-662e-4e02-8416-b7b8c0f7d4a4')
        self.guid_input.setToolTip("This is a unique identifier for the package. Click the generate button to create one.")

        self.guid_input.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}"),
                self
            )
        )

        self.generate_guid_button = ToolButton(FIF.ADD, self)
        self.generate_guid_button.setGeometry(350, 180, 30, 30)
        self.generate_guid_button.clicked.connect(self.generateGUID)
        self.generate_guid_button.setToolTip(" Click the generate button to create a random GUID.")

        product_tags_label = QLabel('Product Tags:', self)
        product_tags_label.setGeometry(20, 220, 100, 30)
        product_tags_label.setStyleSheet(label_stylesheet)
        self.product_tags_input = LineEdit(self)
        self.product_tags_input.setGeometry(130, 220, 210, 30)
        self.product_tags_input.setClearButtonEnabled(True)
        self.product_tags_input.setToolTip("Click the Tag button to select product tags that apply.")

        self.tags_button = ToolButton(FIF.TAG, self)
        self.tags_button.setGeometry(350, 220, 30, 30)
        self.tags_button.clicked.connect(self.openTagSelectionDialog)
        self.tags_button.setToolTip("Click to select product tags that apply.")

        self.support_clean_input = CheckBox('Clean Support Directory', self)
        self.support_clean_input.setGeometry(130, 260, 250, 30)
        self.support_clean_input.setChecked(True)

        self.process_button = PrimaryPushButton('Generate', self)
        self.process_button.setGeometry(20, 300, 100, 30)
        self.process_button.clicked.connect(self.process)
        self.process_button.setToolTip("Click to start the DIM package creation process.")

        self.clear_button = ToolButton(FIF.ERASE_TOOL, self)
        self.clear_button.setGeometry(350, 300, 30, 30)
        self.clear_button.clicked.connect(self.clearAll)
        self.clear_button.setToolTip("Clear all input fields and clean the DIMBuild folder.")

        self.extract_button = PushButton('Extract Archive', self)
        self.extract_button.setGeometry(330, 640, 120, 30)
        self.extract_button.clicked.connect(self.extractArchive)
        self.extract_button.setToolTip("Click to extract a Archive file into the Content folder. Supported are .zip .rar .7z")

        self.image_label = ImageLabel(self)
        self.image_label.setGeometry(510, 20, 250, 310)
        self.image_label.setToolTip("Drop an image here or click to select an image file.")

        self.fileExplorer = FileExplorer(self.dimbuild_dir, self, dimbuild_dir=self.dimbuild_dir, main_gui=self)
        self.fileExplorer.setGeometry(15, 350, 750, 280)

        self.update_button = ToolButton(FIF.SYNC, self)
        self.update_button.setGeometry(100, 640, 30, 30)
        self.update_button.setToolTip("Check for Updates")
        self.update_button.clicked.connect(lambda: self.updater.manual_check())

        self.settings_button = ToolButton(FIF.SETTING, self)
        self.settings_button.setGeometry(60, 640, 30, 30)
        self.settings_button.clicked.connect(self.showSettingsDialog)
        self.settings_button.setToolTip("Open Settings Window")

        self.always_on_top_button = ToolButton(FIF.PIN, self)
        self.always_on_top_button.setCheckable(True)
        self.always_on_top_button.setGeometry(20, 640, 30, 30)
        self.always_on_top_button.clicked.connect(self.toggleAlwaysOnTop)
        self.always_on_top_button.setToolTip("Toggle Always on Top")

        self.progress_ring = ProgressRing(self)
        self.progress_ring.setGeometry(410, 260, 70, 70)
        self.progress_ring.setFixedSize(70, 70)
        self.progress_ring.setTextVisible(True)
        self.progress_ring.setValue(0)
        setFont(self.progress_ring, fontSize=13)
        self.progress_ring.hide()

        QShortcut(QKeySequence("Ctrl+G"), self, self.generateGUID)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.process)
        QShortcut(QKeySequence("Ctrl+N"), self, self.clearAll)
        # QShortcut(QKeySequence("F1"), self, self.openFAQ)

    def showSettingsDialog(self):
        dialog = SettingsDialog(self.doc_main_dir, self)

        dialog.copy_templates_checkbox.setChecked(self.copy_template_files)
        dialog.template_destination_field.setText(self.template_destination)
        dialog.auto_update_checkbox.setChecked(settings.value("auto_update_check", True, type=bool))

        if dialog.exec_():
            self.copy_template_files = dialog.copy_templates_checkbox.isChecked()
            self.template_destination = dialog.template_destination_field.text()

            settings.setValue("copy_template_files", self.copy_template_files)
            settings.setValue("template_destination", self.template_destination)

            auto_enabled = dialog.auto_update_checkbox.isChecked()
            settings.setValue("auto_update_check", auto_enabled)
            self.updater.set_auto_enabled(auto_enabled)

            self.storeitems, self.store_prefixes, self.available_tags, self.daz_folders = load_configurations(self.doc_main_dir)
            self.store_input.clear()
            self.store_input.addItems(self.storeitems)
            self.store_completer = QCompleter(self.storeitems, self)
            self.store_input.setCompleter(self.store_completer)

    def toggleAlwaysOnTop(self):
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        self.always_on_top_button.setIcon(FIF.UNPIN if self.always_on_top_button.isChecked() else FIF.PIN)
        self.show()

    def generateGUID(self):
        new_guid = str(uuid.uuid4())
        self.guid_input.setText(new_guid)

    def clearAll(self):
        reply = QMessageBox.question(self, 'Clear Confirmation',
                                     "Are you sure you want to clear all fields and clean the DIMBuild folder?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.clearFields()
            self.cleanDIMBuildFolder()

    def cleanDIMBuildFolder(self):
        log.info("Attempting to clean the DIMBuild folder.")
        for filename in os.listdir(self.dimbuild_dir):
            file_path = os.path.join(self.dimbuild_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, onerror=self.handle_remove_readonly)
            except Exception as e:
                log.error(f"Failed to clean DIMBuild folder: {e}")

        log.info("DIMBuild folder successfully cleared.")
        content_folder_path = os.path.join(self.dimbuild_dir, "Content")
        if not os.path.exists(content_folder_path):
            os.makedirs(content_folder_path, exist_ok=True)

        self.fileExplorer.reinitialize_model(self.dimbuild_dir)

    def handle_remove_readonly(self, func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def clearFields(self):
        log.info("Attempting to clear all data.")
        try:
            self.store_input.setCurrentIndex(0)
            self.product_name_input.clear()
            self.sku_input.clear()
            self.product_part_input.setValue(1)
            self.generateGUID()
            self.support_clean_input.setChecked(True)
            self.image_label.loadPlaceholderImage()
            log.info("All data successfully cleared.")
            show_info(self, "Clearing Successful", "All data successfully cleared.")
        except Exception as e:
            log.error(f"Failed to clear all data: {e}")
            show_error(self, "Error", "Failed to clear all data. Please check the logs for more details.")

    def contentValidation(self, content_dir):
        valid = any(os.path.exists(os.path.join(content_dir, folder)) for folder in self.daz_folders)
        return valid

    def process(self):
        dimbuild_dir = os.path.join(doc_main_dir, "DIMBuild")
        content_dir = os.path.join(dimbuild_dir, "Content")

        store = self.store_input.currentText()
        product_name = self.product_name_input.text()
        prefix = self.prefix_input.text()
        sku = self.sku_input.text()
        product_part = self.product_part_input.text()
        product_tags = self.product_tags_input.text()
        image_path = self.image_label.imagePath
        SupportClean = self.support_clean_input.isChecked()
        guid = self.guid_input.text()
        if not guid:
            guid = str(uuid.uuid4())
            self.guid_input.setText(guid)

        if not all([store, product_name, prefix, sku, product_part]):
            show_info(self, "Missing Required Fields", "Please fill in all required fields to proceed with DIM package creation.", Qt.Vertical)
            return
        
        destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.last_destination_folder)
        if not destination_folder:
            show_info(self, "DIM Creation Canceled", "No destination folder selected. DIM package creation has been canceled.", Qt.Vertical)
            return
        else:
            self.last_destination_folder = destination_folder

        if not self.contentValidation(content_dir):
            reply = QMessageBox.question(self, "Content Validation Failed",
                                         "No recognized DAZ main folders found in the content directory. "
                                         "Do you want to continue anyway?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                show_info(self, "DIM Creation Canceled", "DIM package creation canceled due to content validation failure.", Qt.Vertical)
                return

        def prettify(elem):
            rough = tostring(elem, encoding="utf-8")
            reparsed = minidom.parseString(rough)
            pretty = reparsed.toprettyxml(indent=" ")
            return '\n'.join(pretty.split('\n')[1:])

        def clean_support_directory(content_dir):
            target_dir = os.path.join(content_dir, "Runtime", "Support")
            os.makedirs(target_dir, exist_ok=True)
            log.info("Attempting to clean Support Directory.")

            def handle_remove_readonly(func, path, exc_info):
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception as e:
                    log.error(f"Still failed to delete {path}. Reason: {e}")

            for name in os.listdir(target_dir):
                p = os.path.join(target_dir, name)
                try:
                    if os.path.isfile(p) or os.path.islink(p):
                        os.chmod(p, stat.S_IWRITE)
                        os.unlink(p)
                    elif os.path.isdir(p):
                        shutil.rmtree(p, onerror=handle_remove_readonly)
                except Exception as e:
                    log.error(f"Failed to delete {p}. Reason: {e}")
                    return False

            log.info("Support directory successfully cleaned.")
            return True

        def process_and_paste_image(content_dir, store, sku, product_name, image_path):
            if not image_path:
                return True
            
            log.info("Attempting to generate Product cover.")
            try:
                sanitized_product_name = re.sub(r'[^A-Za-z0-9._-]+', '_', product_name).strip('_')
                store_formatted = re.sub(r'[^A-Za-z0-9._-]+', '_', store).strip('_')
                new_image_name = f"{store_formatted}_{sku}_{sanitized_product_name}.jpg"
                
                target_dir = os.path.join(content_dir, "Runtime", "Support")
                os.makedirs(target_dir, exist_ok=True)
                new_image_path = os.path.join(target_dir, new_image_name)
                with Image.open(image_path) as img:
                    img = ImageOps.exif_transpose(img)
                    if img.mode != 'RGB':
                        img = img.convert("RGB")
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    img.save(new_image_path, "JPEG")
                    log.info("Product cover successfully generated.")
                return True
            except Exception as e:
                log.error(f"An error occurred while processing the image: {str(e)}")
                return False

        def create_manifest(content_dir):
            log.info("Attempting to generate Product Manifest.")
            try:
                root = Element('DAZInstallManifest', VERSION="0.1")
                SubElement(root, 'GlobalID', VALUE=guid)

                for subdir, dirs, files in os.walk(content_dir):
                    dirs.sort()
                    files.sort()
                    for file in files:
                        file_path = os.path.join(subdir, file).replace("\\", "/")
                        rel_path = os.path.relpath(file_path, start=content_dir).replace("\\", "/")
                        SubElement(root, 'File', TARGET="Content", ACTION="Install", VALUE=f"Content/{rel_path}")

                xml_str = prettify(root)
                manifest_path = os.path.join(os.path.dirname(content_dir), "Manifest.dsx")
                with open(manifest_path, "w", encoding="utf-8", newline="\n") as mf:
                    mf.write(xml_str)
                log.info("Product Manifest successfully generated.")
                return True
            except Exception as e:
                log.error(f"An error occurred while creating the manifest: {str(e)}")
                return False

        def create_supplement(content_dir, product_name, product_tags):
            log.info("Attempting to generate Product Supplement.")
            try:
                root = Element('ProductSupplement', VERSION="0.1")
                SubElement(root, 'ProductName', VALUE=product_name)
                SubElement(root, 'InstallTypes', VALUE="Content")
                SubElement(root, 'ProductTags', VALUE=product_tags)
                
                xml_str = prettify(root)
                supplement_path = os.path.join(os.path.dirname(content_dir), "Supplement.dsx")
                with open(supplement_path, "w", encoding="utf-8", newline="\n") as supplement_file:
                    supplement_file.write(xml_str)
                log.info("Product Supplement successfully generated.")
                return True
            except Exception as e:
                log.error(f"An error occurred while creating the supplement: {str(e)}")
                return False

        def sanitize_product_name(name):
            return re.sub(r'\W+', '', name)

        def zip_content_and_manifests(content_dir, prefix, sku, product_part, product_name, destination_folder, report_progress, total_files):
            prefix_clean = re.sub(r'[^A-Za-z0-9]+', '', str(prefix)).upper()
            try:
                sku_formatted = f"{int(str(sku)):08d}"
            except ValueError:
                sku_formatted = str(sku).zfill(8)

            sanitized_name = re.sub(r'[^A-Za-z0-9._-]+', '_', str(product_name)).strip('_')
            zip_name = f"{prefix_clean}{sku_formatted}-{product_part}_{sanitized_name}.zip"
            zip_path = os.path.join(destination_folder, zip_name)

            arc_base = os.path.dirname(content_dir)

            log.info("Attempting to generate the DIM file.")

            files_zipped = 0
            ignore_names = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}

            with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=False) as zipf:
                for root, dirs, files in os.walk(content_dir):
                    dirs.sort()
                    files.sort()

                    for fname in files:
                        if fname in ignore_names:
                            continue
                        file_path = os.path.join(root, fname)
                        arcname = os.path.relpath(file_path, arc_base).replace(os.sep, '/')
                        zipf.write(file_path, arcname)

                        files_zipped += 1
                        if total_files > 0:
                            percent = int((files_zipped / total_files) * 100)
                            report_progress(min(99, max(0, percent)))

                manifest_path = os.path.join(arc_base, "Manifest.dsx")
                supplement_path = os.path.join(arc_base, "Supplement.dsx")
                if os.path.exists(manifest_path):
                    zipf.write(manifest_path, "Manifest.dsx")
                if os.path.exists(supplement_path):
                    zipf.write(supplement_path, "Supplement.dsx")

            report_progress(100)
            log.info(f"DIM file created at: {zip_path}")

        if SupportClean and not clean_support_directory(content_dir):
            log.error("Failed to clean the Support directory. Exiting.")
            return

        if not process_and_paste_image(content_dir, store, sku, product_name, image_path):
            log.warning("Image processing failed. Skipping manifest and supplement creation.")
            show_error(self, "Image Processing Failed", "Failed to process the image. Manifest and supplement creation will be skipped.")
        else:
            manifest_created = create_manifest(content_dir)
            supplement_created = create_supplement(content_dir, product_name, product_tags)
            
            if manifest_created and supplement_created:
                self.progress_ring.setValue(0)
                self.progress_ring.show()
                self.zip_thread = ZipThread(content_dir, prefix, sku, product_part, product_name, destination_folder, zip_content_and_manifests)
                zt = self.zip_thread
                self.process_button.setEnabled(False)
                zt.progressUpdated.connect(self.updateProgress)
                zt.finished.connect(self.DIMProcessCompleted)
                zt.error.connect(self.onZipError)
                zt.finished.connect(lambda *, _zt=zt: _zt.deleteLater())
                zt.error.connect(lambda _m, *, _zt=zt: _zt.deleteLater())
                zt.start()
            else:
                log.warning("Skipping zip creation due to previous errors.")
                show_error(self, "DIM Creation Skipped", "Manifest or supplement creation failed. DIM packaging will be skipped.")
        pass

    def updateProgress(self, percent):
        self.progress_ring.setValue(percent)

    def onZipError(self, message: str):
        log.error(f"ZIP error: {message}")
        show_error(
            self, "ZIP Error",
            f"An error occurred while creating the archive:<br><small>{message}</small>",
            Qt.Horizontal, InfoBarPosition.TOP_RIGHT, True, 5000
        )
        try:
            self.progress_ring.hide()
            self.progress_ring.setValue(0)
        except Exception:
            pass
        self.process_button.setEnabled(True)
        self.zip_thread = None

    def DIMProcessCompleted(self):
        self.DIMSuccessfullCreatedInfoBar()
        self.progress_ring.hide()
        self.cleanUpTemporaryImage()
        self.process_button.setEnabled(True)
        self.zip_thread = None

    def DIMSuccessfullCreatedInfoBar(self):
        InfoBar.success(
            title='Success',
            content="The DIM has been successfully created and saved.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def extractArchive(self):
        self._extractionHadError = False
        archive_file_path, _ = QFileDialog.getOpenFileName(self, "Select Archive File", "", "Archive Files (*.zip *.rar *.7z)")
        if archive_file_path:
            self.showExtractionState(True)
            log.info("Extraction started...")
            self.extractionWorker = ContentExtractionWorker(archive_file_path, set(self.daz_folders), self.content_dir, self.copy_template_files, self.template_destination)
            self.extractionWorker.extractionComplete.connect(self.onExtractionComplete)
            self.extractionWorker.extractionError.connect(self.onExtractionError)
            self.extractionWorker.start()

    def dropExtractArchive(self, archive_file_path):
        self._extractionHadError = False
        self.showExtractionState(True)
        log.info("Extraction started from TreeView...")
        self.extractionWorker = ContentExtractionWorker(archive_file_path, set(self.daz_folders), self.content_dir, self.copy_template_files, self.template_destination)
        self.extractionWorker.extractionComplete.connect(self.onExtractionComplete)
        self.extractionWorker.extractionError.connect(self.onExtractionError)
        self.extractionWorker.start()

    def onExtractionComplete(self):
        if not self._extractionHadError:
            self.showExtractionState(False, "Extraction completed successfully 😆", success=True)
            log.info("Extraction Process completed.")
            self.fileExplorer.refresh_view()

            if self.extractionWorker.copiedTemplates:
                for templateName in self.extractionWorker.copiedTemplates:
                    show_info(self, "Template Copied", f"Template <b>{templateName}</b> copied successfully.",
                              Qt.Vertical, InfoBarPosition.BOTTOM_RIGHT)
        self.extractionWorker = None  
        
    def onExtractionError(self, message):
        self._extractionHadError = True
        log.error(f"Extraction Error: {message}")
        if self.stateTooltip:
            try:
                self.stateTooltip.close()
            except Exception:
                pass
            self.stateTooltip = None
        show_error(self, "Extraction failed", message, Qt.Vertical, InfoBarPosition.BOTTOM_RIGHT, True, 3000)
        self.extractionWorker = None

    def _close_tip(self, tip_attr):
        tip = getattr(self, tip_attr, None)
        if tip:
            try:
                tip.close()
            except Exception:
                pass
            setattr(self, tip_attr, None)

    def showExtractionState(self, isExtracting, message=None, success=True):
        if isExtracting:
            self._close_tip("stateTooltip")
            tip = StateToolTip('Extracting', 'Please wait...', self)
            tip.move(510, 30)
            tip.setAttribute(Qt.WA_DeleteOnClose, True)
            tip.show()
            self.stateTooltip = tip
            return

        self._close_tip("stateTooltip")
        self._close_tip("_finalTip")

        title = 'Extraction completed' if success else 'Extraction canceled'
        final_tip = StateToolTip(title, message or ('Done.' if success else 'An error occurred.'), self)
        final_tip.setState(success)
        final_tip.move(510, 30)
        final_tip.setAttribute(Qt.WA_DeleteOnClose, True)
        final_tip.show()

        self._finalTip = final_tip
        QTimer.singleShot(1800, lambda: (final_tip.close(), setattr(self, "_finalTip", None)))


class ContentExtractionWorker(QThread):
    extractionComplete = pyqtSignal()
    extractionError = pyqtSignal(str)

    def __init__(self, archive_file_path, daz_folders, content_dir, copy_template_files, template_destination):
        super(ContentExtractionWorker, self).__init__()
        self.archive_file_path = archive_file_path
        self.daz_folders = {s.casefold() for s in daz_folders}
        self.content_dir = content_dir
        self.copy_template_files = copy_template_files
        self.template_destination = template_destination or downloads_dir()
        self.copiedTemplates = []

    def run(self):
        with suppress_cmd_window():
            log.info(f"Starting extraction of {self.archive_file_path}")
            success = False
            try:
                temp_dir = tempfile.mkdtemp()
                patoolib.extract_archive(self.archive_file_path, outdir=temp_dir)
                log.info(f"Archive extracted to temporary directory: [{temp_dir}]")

                base_paths, embedded_archive_files = self.scanDirectory(temp_dir)

                template_archives = [file for file in embedded_archive_files if "templ" in os.path.basename(file).lower()]
                remaining_archives = [file for file in embedded_archive_files if file not in template_archives]

                if len(remaining_archives) > 1:
                    self.extractionError.emit("Multiple archive files found, canceling extraction.")
                    shutil.rmtree(temp_dir)
                    return
                elif len(remaining_archives) == 1:
                    if template_archives: 
                        self.copyTemplateArchive(template_archives[0])
                    self.processEmbeddedArchive(remaining_archives[0], base_paths)
                    success = True
                elif base_paths:
                    if template_archives:
                        self.copyTemplateArchive(template_archives[0])
                    self.extractRelevantContent(temp_dir, base_paths)
                    success = True
                else:
                    self.extractionError.emit("No recognized daz main folders found in the archive.")
                    shutil.rmtree(temp_dir)
                    return

                shutil.rmtree(temp_dir)
            except Exception as e:
                msg = str(e)
                if "7z" in msg.lower() or "unrar" in msg.lower():
                    self.extractionError.emit(
                        "No suitable extractor found (7-Zip or UnRAR). "
                        "Please install and try again."
                    )
                else:
                    self.extractionError.emit(msg)
            finally:
                if success:
                    self.extractionComplete.emit()

    def copyTemplateArchive(self, template_archive_path):
        if self.copy_template_files:
            if not os.path.exists(self.template_destination):
                os.makedirs(self.template_destination, exist_ok=True)
            target_path = os.path.join(self.template_destination, os.path.basename(template_archive_path))
            shutil.copy(template_archive_path, target_path)
            template_file = os.path.basename(template_archive_path)
            self.copiedTemplates.append(template_file)
            log.info(f"Copied template archive [{template_archive_path}] to [{self.template_destination}]")
        else:
            log.info(f"Not copying template file as per user setting.")
        try:
            os.remove(template_archive_path)
            log.info(f"Removed template archive from temporary directory: [{template_archive_path}]")
        except Exception as e:
            log.error(f"Failed to remove template archive from temporary directory: [{e}]")

    def scanDirectory(self, directory):
        base_paths = set()
        embedded_archive_files = []

        for root, _, files in os.walk(directory):
            for fname in files:
                fpath = os.path.join(root, fname)
                lower = fname.casefold()

                if lower.endswith(('.zip', '.rar', '.7z')):
                    embedded_archive_files.append(fpath)
                    continue

                rel = os.path.relpath(fpath, start=directory)
                parts = rel.split(os.sep)
                for i, segment in enumerate(parts):
                    if segment.casefold() in self.daz_folders:
                        base_paths.add(os.sep.join(parts[:i]))
                        break

        return base_paths, embedded_archive_files

    def processEmbeddedArchive(self, embedded_archive_path, base_paths):
        with tempfile.TemporaryDirectory() as nested_temp_dir:
            try:
                patoolib.extract_archive(embedded_archive_path, outdir=nested_temp_dir)
                new_base_paths, _ = self.scanDirectory(nested_temp_dir)

                if new_base_paths:
                    self.extractRelevantContent(nested_temp_dir, new_base_paths)
                else:
                    self.extractionError.emit("No recognized DAZ main folders found in the embedded archive.")
                    return

            except Exception as e:
                msg = str(e)
                if "7z" in msg.lower() or "unrar" in msg.lower():
                    self.extractionError.emit(
                        "No suitable extractor found (7-Zip or UnRAR). "
                        "Please install and try again."
                    )
                else:
                    self.extractionError.emit(msg)
                return
            finally:
                log.info("Cleaning up temporary files from embedded archive extraction.")


    def extractRelevantContent(self, directory, base_paths):
        try:
            if base_paths:
                base_abs_candidates = [os.path.normpath(os.path.join(directory, bp)) for bp in base_paths]
                common_base = os.path.commonpath(base_abs_candidates)
            else:
                common_base = os.path.normpath(directory)

            directory_abs = os.path.abspath(directory)
            common_base = os.path.abspath(common_base)
            if os.path.commonpath([directory_abs, common_base]) != directory_abs:
                common_base = directory_abs

            def _safe_join(base, rel):
                rel_norm = os.path.normpath(rel)
                dst = os.path.abspath(os.path.join(base, rel_norm))
                base_abs = os.path.abspath(base)
                if os.path.commonpath([dst, base_abs]) != base_abs:
                    raise ValueError(f"Unsafe path outside content dir: {rel}")
                return dst

            log.info(f"Starting to extract relevant content from [{directory_abs}] with base path [{common_base}]")

            for root, dirs, _ in os.walk(directory_abs):
                if os.path.commonpath([os.path.abspath(root), common_base]) != common_base:
                    continue
                for d in dirs:
                    src_dir = os.path.join(root, d)
                    rel_dir = os.path.relpath(src_dir, common_base)
                    try:
                        dst_dir = _safe_join(self.content_dir, rel_dir)
                        os.makedirs(dst_dir, exist_ok=True)
                    except ValueError as ve:
                        log.error(str(ve))
                        self.extractionError.emit(str(ve))
                        return
                    except Exception as e:
                        log.error(f"Failed to create directory [{rel_dir}]: {e}")

            ignore_names = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}
            files_to_copy = []
            for root, _, files in os.walk(directory_abs):
                if os.path.commonpath([os.path.abspath(root), common_base]) != common_base:
                    continue
                for fname in files:
                    if fname in ignore_names:
                        continue
                    src = os.path.join(root, fname)
                    if os.path.islink(src):
                        log.warning(f"Skipping symlink: {src}")
                        continue
                    rel = os.path.relpath(src, common_base)
                    try:
                        dst = _safe_join(self.content_dir, rel)
                        files_to_copy.append((src, dst))
                    except ValueError as ve:
                        log.error(str(ve))
                        self.extractionError.emit(str(ve))
                        return

            def copy_file(pair):
                src, dst = pair
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    log.info(f"Copied file [{src}] to [{dst}]")
                except Exception as e:
                    log.error(f"Failed to copy file [{src}] to [{dst}]: {e}")

            if files_to_copy:
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=get_optimal_workers()) as executor:
                    list(executor.map(copy_file, files_to_copy))

            log.info("Completed extracting relevant content.")

        except Exception as e:
            log.error(f"Extraction failed: {e}")
            try:
                self.extractionError.emit(str(e))
            except Exception:
                pass


if __name__ == '__main__':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Syst3mApps.DIMCreator")
    except Exception:
        pass

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setOrganizationName("Syst3mApps")
    app.setApplicationName("DIMCreator")
    app.setWindowIcon(QIcon(logo_path))
    ex = DIMPackageGUI()
    ex.show()
    sys.exit(app.exec())

