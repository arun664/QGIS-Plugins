# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ShapefileCreator
                                 A QGIS plugin
 Create new shapefile from existing shapefile
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-08-09
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Arun Kumar M
        email                : marunkumar664@gmail.com
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
#importing QgsProject
from qgis.core import QgsProject , Qgis , QgsExpression, QgsVectorFileWriter, QgsFeatureRequest


from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction , QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .create_shapefile_dialog import ShapefileCreatorDialog
import os.path


class ShapefileCreator:
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
            'ShapefileCreator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Create Shapefile')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('ShapefileCreator', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/create_shapefile/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Save Shapefile'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Create Shapefile'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select output file ","", '*.shp')
        self.dlg.lineEdit_2.setText(filename)
        
        
    def select(self):
        query = self.dlg.textEdit.toPlainText()                                 #Takes-in input condition via textEdit
        
        layers = QgsProject.instance().layerTreeRoot().children()    
        selectedLayerIndex = self.dlg.comboBox.currentIndex()
        selectedLayer = layers[selectedLayerIndex].layer()
        fieldnames = selectedLayer.getFeatures()
        selectedLayer.selectByExpression(query)                          #executes the test condition
        selectedLayer.selectedFeatures()
        #selection = selectedLayer.getFeatures(QgsFeatureRequest().setFilterExpression(query))
        #selectedLayer.selectByIds([k.id() for k in selection])
        
                
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ShapefileCreatorDialog()
            
            
        self.dlg.pushButton.clicked.connect(self.select_output_file)   
        
        self.dlg.comboBox.clear()
        self.dlg.comboBox_2.clear()
        
        layers = QgsProject.instance().layerTreeRoot().children()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)
        
        def attribute_type():                                   #To extract attributes of the selected layer with its datatype shown in comboBox_2 and lineEdit
            self.dlg.lineEdit.clear()
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex].layer()
            fieldtype = [field.typeName() for field in selectedLayer.fields()]
            attr = self.dlg.comboBox_2.currentIndex()
            attr_type = str(fieldtype[attr])
            self.dlg.lineEdit.setText(attr_type)
                
        def field_select():                                     #To display all the attributes of the layer using comboBox
            self.dlg.comboBox_2.clear()
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex].layer()
            fields = [field.name() for field in selectedLayer.fields()]
            self.dlg.comboBox_2.addItems(fields)
            #To display the datatype of attribute, so that it helps in passing commands to retrieve essential data
            self.dlg.comboBox_2.currentIndexChanged.connect(attribute_type)
        
        #count = self.dlg.comboBox.count()
        #if count==1:
        field_select()
        # This connects the function to the layer combobox when changed
        self.dlg.comboBox.currentIndexChanged.connect(field_select)
        
        self.dlg.pushButton_2.clicked.connect(self.select)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            filename = self.dlg.lineEdit_2.text()
                    
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayer = layers[selectedLayerIndex].layer()
            QgsVectorFileWriter.writeAsVectorFormat( selectedLayer, filename, "utf-8", selectedLayer.crs(), "ESRI Shapefile", 1)
                
                
            self.iface.messageBar().pushMessage(
                "Success", "Output file written at " + filename,
                level=Qgis.Success, duration=3)
            self.dlg.textEdit.clear()