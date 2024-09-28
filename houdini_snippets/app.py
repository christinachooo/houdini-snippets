import copy
import logging

import hou

try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore

from houdini_snippets import files, nodes, settings

logger = logging.getLogger(__name__)


class SaveNodesWidget(QtWidgets.QGroupBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()
        self._connect_ui()

    def _init_ui(self):
        self.setTitle("Save")
        layout = QtWidgets.QVBoxLayout()

        file_name_layout = QtWidgets.QHBoxLayout()
        file_name_label = QtWidgets.QLabel("File Name")
        self.file_lineedit = QtWidgets.QLineEdit()
        file_name_layout.addWidget(file_name_label)
        file_name_layout.addWidget(self.file_lineedit)

        self.error_message = QtWidgets.QLabel("No nodes selected.")
        self.error_message.setStyleSheet("color: red;")
        self.error_message.setHidden(True)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setEnabled(False)

        layout.addLayout(file_name_layout)
        layout.addWidget(self.error_message)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def _connect_ui(self):
        self.file_lineedit.textChanged.connect(self._save_file_lineedit)
        self.save_button.clicked.connect(self.save)

    def _save_file_lineedit(self, text: str) -> None:
        if not text:
            self.save_button.setEnabled(False)
        else:
            self.save_button.setEnabled(True)

    def save(self) -> None:
        selected_nodes = nodes.node_selection()
        logger.debug(f"{selected_nodes = }")

        if not selected_nodes:
            self.error_message.setHidden(False)
            return

        pref_data = settings.load_settings()
        file_name = self.file_lineedit.text()
        logger.info(f"Saved Snippet: {file_name}.hip")
        nodes.save_selected_nodes(pref_data.snippet_path, file_name)
        self.file_lineedit.clear()


class LoadNodesWidget(QtWidgets.QGroupBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._data = {}
        self.path = ""

        self._init_ui()
        self._connect_ui()
        self.refresh_data()

    def _init_ui(self):
        self.setTitle("Load")
        layout = QtWidgets.QVBoxLayout()

        self.snippet_tree = QtWidgets.QTreeWidget()
        self.snippet_tree.setHeaderHidden(True)
        completer = QtWidgets.QCompleter(None)

        filter_layout = QtWidgets.QHBoxLayout()
        filter_label = QtWidgets.QLabel("Filter")
        filter_label.setFixedWidth(30)
        self.filter_combobox = QtWidgets.QComboBox()
        self.filter_combobox.addItem("Clear Filter")
        self.filter_combobox.setEditable(True)
        self.filter_combobox.setCurrentIndex(-1)
        self.filter_combobox.setCompleter(completer)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combobox)

        self.load_button = QtWidgets.QPushButton("Load")
        self.load_button.setEnabled(False)

        layout.addWidget(self.snippet_tree)
        layout.addLayout(filter_layout)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def _connect_ui(self):
        self.snippet_tree.selectionModel().selectionChanged.connect(self._selection_changed)
        self.filter_combobox.currentTextChanged.connect(self._filter_changed)
        self.filter_combobox.currentIndexChanged.connect(self._clear_filter)
        self.load_button.clicked.connect(self.load)

    def _clear_filter(self) -> None:
        self.filter_combobox.setCurrentIndex(-1)

    def _selection_changed(self) -> None:
        current_selection = self.snippet_tree.currentItem()

        if self.snippet_tree.selectedItems() and current_selection.parent():
            self.load_button.setEnabled(True)
        else:
            self.load_button.setEnabled(False)

    def _filter_changed(self, text: str) -> None:
        self.refresh_data()

        if not text:
            self.update_snippets(self._data)
            return

        filtered_data = copy.deepcopy(self._data)
        for category, snippets in list(filtered_data.items()):
            for snippet_name, snippet_path in list(snippets.items()):
                if text not in snippet_name and text not in snippet_path:
                    del snippets[snippet_name]
            if not snippets:
                del filtered_data[category]

        self.update_snippets(filtered_data)

    def load(self) -> None:
        pref_data = settings.load_settings()
        selected_item = self.snippet_tree.currentItem()
        logger.info(f"Loaded snippet: {selected_item}")
        item = selected_item.text(0)
        category = selected_item.parent().text(0)
        nodes.load_nodes_from_file(
            self._data[category][item],
            pref_data.add_network_box,
            pref_data.randomize_network_box_colors
        )

    def update_snippets(self, data: dict) -> None:
        self.snippet_tree.clear()

        sorted_data = {key: value for key, value in sorted(data.items())}

        for category, snippets in sorted_data.items():
            category_name = QtWidgets.QTreeWidgetItem(self.snippet_tree, [category])
            for snippet_name, snippet_path in snippets.items():
                QtWidgets.QTreeWidgetItem(category_name, [snippet_name])

        self.snippet_tree.expandAll()

    def refresh_data(self) -> None:
        pref_data = settings.load_settings()
        self._data = files.get_directories(pref_data.snippet_path)
        self.update_snippets(self._data)


class PreferencesWidget(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()
        self._connect_ui()

    def _init_ui(self):
        self.setWindowTitle("Preferences")

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        self.setMaximumHeight(252)

        library_path_layout = QtWidgets.QHBoxLayout()
        library_label = QtWidgets.QLabel("Library Path")
        self.library_lineedit = QtWidgets.QLineEdit()
        self.directory_button = QtWidgets.QToolButton()
        self.directory_button.setIcon(hou.qt.Icon("BUTTONS_chooser_folder"))
        library_path_layout.addWidget(library_label)
        library_path_layout.addWidget(self.library_lineedit)
        library_path_layout.addWidget(self.directory_button)

        general_groupbox = QtWidgets.QGroupBox("General")
        general_groupbox.setLayout(library_path_layout)

        layout_layout = QtWidgets.QVBoxLayout()
        self.add_network_box_check = QtWidgets.QCheckBox("Add Network Box")
        self.randomize_network_box_colors_check = QtWidgets.QCheckBox("Randomize Network Box Colors")
        self.randomize_network_box_colors_check.setDisabled(True)

        layout_layout.addWidget(self.add_network_box_check)
        layout_layout.addWidget(self.randomize_network_box_colors_check)

        layout_groupbox = QtWidgets.QGroupBox("Layout")
        layout_groupbox.setLayout(layout_layout)

        self.dialog_button_box = QtWidgets.QDialogButtonBox()
        self.apply_button = self.dialog_button_box.addButton("Apply", QtWidgets.QDialogButtonBox.ApplyRole)
        self.dialog_button_box.addButton("Accept", QtWidgets.QDialogButtonBox.AcceptRole)
        self.dialog_button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        main_layout.addWidget(general_groupbox)
        main_layout.addSpacing(10)
        main_layout.addWidget(layout_groupbox)
        main_layout.addWidget(self.dialog_button_box)

    def _connect_ui(self) -> None:
        self.add_network_box_check.toggled.connect(self.randomize_network_box_colors_check.setEnabled)
        self.dialog_button_box.clicked.connect(self.button_clicked)
        self.directory_button.clicked.connect(self.open_file_dialog)

    def button_clicked(self, button) -> None:
        role = self.dialog_button_box.buttonRole(button)
        logger.debug(f"{role = }")

        if role == QtWidgets.QDialogButtonBox.RejectRole:
            self.reject()
        else:
            pref_data = settings.Settings(
                snippet_path=self.library_lineedit.text(),
                add_network_box=self.add_network_box_check.isChecked(),
                randomize_network_box_colors=self.randomize_network_box_colors_check.isChecked(),
            )
            settings.save_settings(pref_data)
            logger.info(f"Saved {pref_data}")
            if role == QtWidgets.QDialogButtonBox.AcceptRole:
                self.accept()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        pref_data = settings.load_settings()
        logger.debug(pref_data)

        self.library_lineedit.setText(pref_data.snippet_path)
        self.add_network_box_check.setChecked(pref_data.add_network_box)
        self.randomize_network_box_colors_check.setChecked(
            pref_data.randomize_network_box_colors)

        super().showEvent(event)

    def open_file_dialog(self) -> None:
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        library_path = dialog.getExistingDirectory()
        logger.debug(f"User selected library path: {library_path}")

        if library_path:
            self.library_lineedit.setText(library_path)


class SnippetWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()
        self._connect_ui()

    def _init_ui(self):
        self.setWindowTitle("Snippets")
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        self.load_nodes_widget = LoadNodesWidget(self)
        self.save_nodes_widget = SaveNodesWidget(self)

        cancel_button_layout = QtWidgets.QHBoxLayout()
        self.preferences_button = QtWidgets.QToolButton()
        self.preferences_button.setIcon(hou.qt.Icon("BUTTONS_gear"))
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button_layout.addWidget(self.preferences_button)
        cancel_button_layout.addStretch()
        cancel_button_layout.addWidget(self.cancel_button)

        main_layout.addWidget(self.load_nodes_widget)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.save_nodes_widget)
        main_layout.addLayout(cancel_button_layout)

        self.installEventFilter(self)

    def _connect_ui(self) -> None:
        self.cancel_button.clicked.connect(self.close)
        self.preferences_button.clicked.connect(self.show_preferences)
        self.save_nodes_widget.save_button.clicked.connect(self.refresh_tree)

    def show_preferences(self) -> None:
        preferences_window = PreferencesWidget(self)
        result = preferences_window.exec()
        logger.debug(f"{result = }")

        if result == 0:
            return

        self.load_nodes_widget.refresh_data()

    def refresh_tree(self) -> None:
        self.load_nodes_widget.refresh_data()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.WindowDeactivate:
            self.save_nodes_widget.error_message.setHidden(True)

        return super().eventFilter(obj, event)
