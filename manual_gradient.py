# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
/***************************************************************************
 ManualGradient
                                 A QGIS plugin
 Manual Gradient Tools
                              -------------------
        begin                : 2016-06-24
        git sha              : $Format:%H$
        copyright            : (C) 2016 by mugwort_rc
        email                : mugwort.rc@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import pyqtSlot, QPyNullVariant
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QColor

from qgis.core import QgsVectorGradientColorRampV2, QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2, QgsStyleV2
from qgis.gui import QgsMapLayerProxyModel

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from manual_gradient_dialog import ManualGradientDialog
import os.path
import math


class ManualGradient:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ManualGradient_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ManualGradientDialog()
        self.dlg.comboBoxLayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.comboBoxLayer.layerChanged.connect(self.dlg.comboBoxField.setLayer)
        self.dlg.comboBoxField.fieldChanged.connect(self.on_fieldChanged)
        layer = self.dlg.comboBoxLayer.currentLayer()
        if layer:
            self.dlg.comboBoxField.setLayer(layer)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Manual Gradient Tools')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ManualGradient')
        self.toolbar.setObjectName(u'ManualGradient')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ManualGradient', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ManualGradient/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Manual Gradient Tools'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Manual Gradient Tools'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            layer = self.dlg.comboBoxField.layer()
            field = self.dlg.comboBoxField.currentField()
            altName = None
            if self.dlg.checkBoxAltName.isChecked():
                altName = self.dlg.lineEditAltName.text()
            start = self.dlg.doubleSpinBoxStart.value()
            step = self.dlg.doubleSpinBoxStep.value()
            count = self.dlg.spinBoxCount.value()
            suffix = self.dlg.lineEditSuffix.text()
            self.graduate(layer, field, altName, start, step, count, suffix)

    def graduate(self, layer, fieldName, altName, start, step, count, suffix):
        if not layer or not fieldName:
            return
        uniqueValues = layer.uniqueValues(layer.fieldNameIndex(fieldName))
        uniqueValues = [x for x in uniqueValues if not isinstance(x, QPyNullVariant)]
        minimum = min(uniqueValues)
        maximum = max(uniqueValues)
        ramp = QgsStyleV2.defaultStyle().colorRamp("Blues")
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        ranges = []
        previous = minimum
        current = start
        for i in range(count):
            new_symbol = symbol.clone()
            new_symbol.setColor(ramp.color(float(i) / max(count-1, 1)))
            if i == count - 1:
                current = maximum
            ranges.append(QgsRendererRangeV2(previous, current, new_symbol, "{} - {}{}".format(math.ceil(previous), math.ceil(current), suffix)))
            previous = current
            current += step
        layer.setRendererV2(QgsGraduatedSymbolRendererV2(fieldName, ranges))
        layer.triggerRepaint()
        if altName:
            layer.setLayerName(altName)

    @pyqtSlot(str)
    def on_fieldChanged(self, fieldName):
        self.dlg.lineEditAltName.setText(fieldName)
        layer = self.dlg.comboBoxField.layer()
        minimum = min(layer.uniqueValues(layer.fieldNameIndex(fieldName)))
        self.dlg.doubleSpinBoxStart.setValue(minimum)
