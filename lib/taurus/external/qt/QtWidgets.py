# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder Developmet Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides widget classes and functions.
.. warning:: Only PyQt4/PySide QtGui classes compatible with PyQt5.QtWidgets
    are exposed here. Therefore, you need to treat/use this package as if it
    were the ``PyQt5.QtWidgets`` module.
"""

from . import PYQT5, PYSIDE2, PYQT4, PYSIDE, PythonQtError
from taurus.core.util import log as __log

if PYQT5:
    from PyQt5.QtWidgets import *
elif PYSIDE2:
    from PySide2.QtWidgets import *
elif PYQT4:
    __log.warning('Using QtWidgets with PyQt4 is not supported and may fail '
                  + 'in many cases. Use at your own risk '
                  + '(or use a Qt5 binding)')
    from PyQt4.QtGui import *
    QStyleOptionViewItem = QStyleOptionViewItemV4
    del QStyleOptionViewItemV4

    # These objects belong to QtGui
    try:
        # Older versions of PyQt4 do not provide these
        del (QGlyphRun,
             QMatrix2x2, QMatrix2x3, QMatrix2x4, QMatrix3x2, QMatrix3x3,
             QMatrix3x4, QMatrix4x2, QMatrix4x3, QMatrix4x4,
             QQuaternion, QRadialGradient, QRawFont, QRegExpValidator,
             QStaticText, QTouchEvent, QVector2D, QVector3D, QVector4D,
             qFuzzyCompare)
    except NameError:
        pass
    del (QAbstractTextDocumentLayout, QActionEvent, QBitmap, QBrush, QClipboard,
         QCloseEvent, QColor, QConicalGradient, QContextMenuEvent, QCursor,
         QDesktopServices, QDoubleValidator, QDrag, QDragEnterEvent,
         QDragLeaveEvent, QDragMoveEvent, QDropEvent, QFileOpenEvent,
         QFocusEvent, QFont, QFontDatabase, QFontInfo, QFontMetrics,
         QFontMetricsF, QGradient, QHelpEvent, QHideEvent,
         QHoverEvent, QIcon, QIconDragEvent, QIconEngine, QImage,
         QImageIOHandler, QImageReader, QImageWriter, QInputEvent,
         QInputMethodEvent, QKeyEvent, QKeySequence, QLinearGradient,
         QMouseEvent, QMoveEvent, QMovie, QPaintDevice, QPaintEngine,
         QPaintEngineState, QPaintEvent, QPainter, QPainterPath,
         QPainterPathStroker, QPalette, QPen, QPicture, QPictureIO, QPixmap,
         QPixmapCache, QPolygon, QPolygonF,
         QRegion, QResizeEvent, QSessionManager, QShortcutEvent, QShowEvent,
         QStandardItem, QStandardItemModel, QStatusTipEvent,
         QSyntaxHighlighter, QTabletEvent, QTextBlock, QTextBlockFormat,
         QTextBlockGroup, QTextBlockUserData, QTextCharFormat, QTextCursor,
         QTextDocument, QTextDocumentFragment, QTextDocumentWriter,
         QTextFormat, QTextFragment, QTextFrame, QTextFrameFormat,
         QTextImageFormat, QTextInlineObject, QTextItem, QTextLayout,
         QTextLength, QTextLine, QTextList, QTextListFormat, QTextObject,
         QTextObjectInterface, QTextOption, QTextTable, QTextTableCell,
         QTextTableCellFormat, QTextTableFormat, QTransform,
         QValidator, QWhatsThisClickedEvent,
         QWheelEvent, QWindowStateChangeEvent, qAlpha, qBlue,
         qGray, qGreen, qIsGray, qRed, qRgb, qRgba, QIntValidator,
         QStringListModel)

    # These objects belong to QtPrintSupport
    del (QAbstractPrintDialog, QPageSetupDialog, QPrintDialog, QPrintEngine,
         QPrintPreviewDialog, QPrintPreviewWidget, QPrinter, QPrinterInfo)

    # These objects belong to QtCore
    del (QItemSelection, QItemSelectionModel, QItemSelectionRange,
         QSortFilterProxyModel)

    # Patch QComboBox to allow Python objects to be passed to userData
    # patch_qcombobox(QComboBox)  # We don't do it to avoid changing behaviour

    # QHeaderView: renamed methods
    QHeaderView.sectionsClickable = QHeaderView.isClickable
    QHeaderView.sectionsMovable = QHeaderView.isMovable
    QHeaderView.sectionResizeMode = QHeaderView.resizeMode
    QHeaderView.setSectionsClickable = QHeaderView.setClickable
    QHeaderView.setSectionsMovable = QHeaderView.setMovable
    QHeaderView.setSectionResizeMode = QHeaderView.setResizeMode

elif PYSIDE:
    __log.warning('Using QtWidgets with PySide is not supported and may fail '
                  + 'in many cases. Use at your own risk '
                  + '(or use a Qt5 binding)')
    from PySide.QtGui import *
    QStyleOptionViewItem = QStyleOptionViewItemV4
    del QStyleOptionViewItemV4

    # These objects belong to QtGui
    del (QAbstractTextDocumentLayout, QActionEvent, QBitmap, QBrush, QClipboard,
         QCloseEvent, QColor, QConicalGradient, QContextMenuEvent, QCursor,
         QDesktopServices, QDoubleValidator, QDrag, QDragEnterEvent,
         QDragLeaveEvent, QDragMoveEvent, QDropEvent, QFileOpenEvent,
         QFocusEvent, QFont, QFontDatabase, QFontInfo, QFontMetrics,
         QFontMetricsF, QGradient, QHelpEvent, QHideEvent,
         QHoverEvent, QIcon, QIconDragEvent, QIconEngine, QImage,
         QImageIOHandler, QImageReader, QImageWriter, QInputEvent,
         QInputMethodEvent, QKeyEvent, QKeySequence, QLinearGradient,
         QMatrix2x2, QMatrix2x3, QMatrix2x4, QMatrix3x2, QMatrix3x3,
         QMatrix3x4, QMatrix4x2, QMatrix4x3, QMatrix4x4, QMouseEvent,
         QMoveEvent, QMovie, QPaintDevice, QPaintEngine, QPaintEngineState,
         QPaintEvent, QPainter, QPainterPath, QPainterPathStroker, QPalette,
         QPen, QPicture, QPictureIO, QPixmap, QPixmapCache, QPolygon,
         QPolygonF, QQuaternion, QRadialGradient, QRegExpValidator,
         QRegion, QResizeEvent, QSessionManager, QShortcutEvent, QShowEvent,
         QStandardItem, QStandardItemModel, QStatusTipEvent,
         QSyntaxHighlighter, QTabletEvent, QTextBlock, QTextBlockFormat,
         QTextBlockGroup, QTextBlockUserData, QTextCharFormat, QTextCursor,
         QTextDocument, QTextDocumentFragment,
         QTextFormat, QTextFragment, QTextFrame, QTextFrameFormat,
         QTextImageFormat, QTextInlineObject, QTextItem, QTextLayout,
         QTextLength, QTextLine, QTextList, QTextListFormat, QTextObject,
         QTextObjectInterface, QTextOption, QTextTable, QTextTableCell,
         QTextTableCellFormat, QTextTableFormat, QTouchEvent, QTransform,
         QValidator, QVector2D, QVector3D, QVector4D, QWhatsThisClickedEvent,
         QWheelEvent, QWindowStateChangeEvent, qAlpha, qBlue, qGray, qGreen,
         qIsGray, qRed, qRgb, qRgba, QIntValidator, QStringListModel)

    # These objects belong to QtPrintSupport
    del (QAbstractPrintDialog, QPageSetupDialog, QPrintDialog, QPrintEngine,
         QPrintPreviewDialog, QPrintPreviewWidget, QPrinter, QPrinterInfo)

    # These objects belong to QtCore
    del (QItemSelection, QItemSelectionModel, QItemSelectionRange,
         QSortFilterProxyModel)

    # Patch QComboBox to allow Python objects to be passed to userData
    # patch_qcombobox(QComboBox)  # We don't do it to avoid changing behaviour

    # QHeaderView: renamed methods
    QHeaderView.sectionsClickable = QHeaderView.isClickable
    QHeaderView.sectionsMovable = QHeaderView.isMovable
    QHeaderView.sectionResizeMode = QHeaderView.resizeMode
    QHeaderView.setSectionsClickable = QHeaderView.setClickable
    QHeaderView.setSectionsMovable = QHeaderView.setMovable
    QHeaderView.setSectionResizeMode = QHeaderView.setResizeMode

else:
    raise PythonQtError('No Qt bindings could be found')
