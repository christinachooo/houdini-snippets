import logging
import sys

from PySide6 import QtWidgets

from houdini_snippets.app import (
    SaveNodesWidget,
    LoadNodesWidget,
    PreferencesWidget,
    SnippetWidget,
)

logging.basicConfig(level=logging.DEBUG)


def test_save_nodes_gui():
    app = QtWidgets.QApplication()

    save_nodes_gui = SaveNodesWidget()
    save_nodes_gui.show()
    sys.exit(app.exec())


def test_load_nodes_gui():
    app = QtWidgets.QApplication()

    load_nodes_gui = LoadNodesWidget()
    load_nodes_gui.show()
    sys.exit(app.exec())


def test_preferences_gui():
    app = QtWidgets.QApplication()

    preferences_gui = PreferencesWidget()
    preferences_gui.show()
    sys.exit(app.exec())


def test_snippets_gui():
    app = QtWidgets.QApplication()

    snippets_gui = SnippetWidget()
    snippets_gui.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test_save_nodes_gui()
    # test_load_nodes_gui()
    # test_preferences_gui()
    # test_snippets_gui()
