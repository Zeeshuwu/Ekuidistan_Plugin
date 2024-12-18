# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Ekuidistan
                                 A QGIS plugin
 Penentuan Garis Ekuidistan dengan Pembobotan Pulau Kecil Untuk Delimitasi Batas Maritim Internasional
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-10-19
        git sha              : $Format:%H$
        copyright            : (C) 2024 by PRGG_8_2024
        email                : krishnaduta12345@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QPushButton
from qgis.core import QgsProject, Qgis, QgsGeometry, QgsMessageLog  

# Initialize Qt resources from file resources.py
# import resources_rc
# Import the code for the dlg
from .ekuidistan_dialog import EkuidistanDialog
from .library import(
    interpolate_line_segment,
    apply_effect,
    interpolate_line,
    line_to_point_layer_new,
    # line_to_point_layer,
    combine_geometries,
    line_feature_list_to_layer,
    merge_point_layers,
    create_voronoi,
    create_delaunay_triangulation,
    valid_delaunay_triangulation,
    create_median_line_opposite,
    create_median_line_adjacent,
    create_equidistant_point,
    create_construction_line,
    generate_final_boundary,
    merge_layer_with_small_island,
    merge_line_layers)
import os.path


class Ekuidistan:
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
        self.dlg = EkuidistanDialog()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Ekuidistan_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Ekuidistan')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.processing_flag = False

        self.list_valid_layers = []
        self.list_invalid_layers = []
        self.layerA = ""
        self.layerB = ""
        self.median_layer_opp = ""
        self.layermedian = ""
        self.line_layer = ""
        self.pulaukeciladj = ""
        self.layer_to_merge = ""
        self.merged_layer = ""
        self.list_feature_a = ""
        self.list_feature_b = ""
        self.crs = ""
        self.input_mode = ""
        self.save_location = ""

        self.dt_layer = ""
        self.valid_dt = ""
        self.merged_pt_layer = ""
        self.p_layer_a = ""
        self.p_layer_b = ""

        self.rb_layer_a = ""
        self.rb_layer_b = ""

        self.msg_widget = ""

        self.process_flag = False
        self.pluginIsActive = False
        self.dlg = None

        self.intermediary_group = ""

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
        return QCoreApplication.translate('Ekuidistan', message)


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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = self.plugin_dir + '/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Ekuidstan'),
            callback=self.run,
            parent=self.iface.mainWindow(),)

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # print "** CLOSING EqDistant"

        # disconnects
        self.dlg.closingPlugin.disconnect(self.onClosePlugin)
        try:
            self.iface.mapCanvas().layersChanged.disconnect()
        except Exception:
            pass
        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        self.dlg = None

        self.pluginIsActive = False
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Ekuidistan'),
                action)
            self.iface.removeToolBarIcon(action)
    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            
            # print "** STARTING EqDistant"

            # dialog may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dlg is None:
                # Create the dialog (after translation) and keep reference
                self.dlg = EkuidistanDialog()
                self.cek_layer_input()
                self.dlg.opp_btnRun.pressed.connect(
                    self.oppositeline
                )
                self.dlg.half_opp.pressed.connect(self.halfoppositeline)
                self.populate_layer_comboboxes() 
                self.dlg.inputlayerA.currentIndexChanged.connect(self.cek_layer_input)  
                self.dlg.adj_btnRun.pressed.connect(self.adjacentline)
                    # Show the dialog
            self.dlg.show()  # Ensure the dialog is displayed

                # self.dlg.pushButton.pressed.connect(self.customMapTool)

            # connect to provide cleanup on closing of dialog
            self.dlg.closingPlugin.connect(self.onClosePlugin)
    def populate_layer_comboboxes(self):
        layers = self.iface.mapCanvas().layers()

        for layer in layers:
            self.layerA = self.dlg.inputlayerA.addItem(layer.name(), layer)
            self.layerB = self.dlg.inputlayerB.addItem(layer.name(), layer)
            self.layermedian = self.dlg.input_medianlayer.addItem(layer.name(), layer)
            try:
                self.layerA.selectionChanged.connect(
                    self.feature_selection_a
                )
                self.layerB.selectionChanged.connect(
                    self.feature_selection_b
                )
                self.cek_layer_input()
            except AttributeError:
                pass
        self.atribut()
            
    def cek_layer_input(self):
        self.layerAcheck = self.dlg.inputlayerA.currentData()
        self.layerBcheck = self.dlg.inputlayerB.currentData()
        self.feature_selection_a
        self.feature_selection_b
            # pendefinisian layer input
        if  self.layerAcheck == self.layerBcheck :
            self.dlg.opp_btnRun.setEnabled(False)
            self.dlg.adj_btnRun.setEnabled(False)
            self.dlg.labelTitikA.setText("Layer A and Layer B must not same")
            self.dlg.labelTitikB.setText("Layer A and Layer B must not same")
        else:
            self.dlg.opp_btnRun.setEnabled(True)
            self.dlg.adj_btnRun.setEnabled(True)
            self.dlg.labelTitikA.setText("")
            self.dlg.labelTitikB.setText("")
        
        if not hasattr(self.layerA, "getFeatures") or not hasattr(self.layerB, "getFeatures"):
            self.iface.messageBar().pushMessage(
                "Error:",
                "Invalid layer selection.",
                Qgis.Critical,
                duration=3,
            )
        return

        if self.dlg.checkBoxA.isChecked():
            self.list_feature_a = [
                feat for feat in self.layerA.selectedFeatures()
            ]
        else:
            self.list_feature_a = [
                feat for feat in self.layerA.getFeatures()
            ]
        if self.dlg.checkBoxB.isChecked():
            self.list_feature_b = [
                feat for feat in self.layerB.selectedFeatures()
            ]
        else:
            self.list_feature_b = [
                feat for feat in self.layerB.getFeatures()
            ]
        # check input CRS
        crs_a = self.layerA.crs().authid()
        crs_b = self.layerB.crs().authid()
        if crs_a == crs_b:
            self.crs = crs_a
        else:
            self.iface.messageBar().pushMessage(
                "Warning:",
                "Input files should be in the same coordinate system.",
                Qgis.Critical,
                duration=3,
            )
            self.process_flag = False
    # Bersihkan isi combobox sebelum mengisi ulang
    def atribut(self):
        self.layerA = self.dlg.inputlayerA.currentData()
        self.layerB = self.dlg.inputlayerB.currentData()
        
        # Clear previous selections
        self.list_feature_a = []
        self.list_feature_b = []
        

    def on_layer_selection_changed(self):
        """Handle the change in selected layer."""
        # Mendapatkan data dari kedua opsi
        selected_layer_opppemilik = self.dlg.opppemilikpulaukecil.currentData()
        selected_layer_adjepmilik = self.dlg.adjepmilikpulaukecil.currentData()

        if selected_layer_opppemilik == self.layerA:
            # Jika Layer A dipilih melalui opppemilik
            print("Layer A selected via opppemilik")
            # Logika untuk menonaktifkan Layer B jika diperlukan
        elif selected_layer_opppemilik == self.layerB:
            # Jika Layer B dipilih melalui opppemilik
            print("Layer B selected via opppemilik")
            # Logika untuk menonaktifkan Layer A jika diperlukan

        if selected_layer_adjepmilik == self.layerA:
            # Jika Layer A dipilih melalui adjepmilik
            print("Layer A selected via adjepmilik")
            # Logika untuk menonaktifkan Layer B jika diperlukan
        elif selected_layer_adjepmilik == self.layerB:
            # Jika Layer B dipilih melalui adjepmilik
            print("Layer B selected via adjepmilik")
            # Logika untuk menonaktifkan Layer A jika diperlukan

        # Jika diperlukan, tambahkan logika untuk menangani konflik antara kedua pilihan
        if selected_layer_opppemilik == self.layerA and selected_layer_adjepmilik == self.layerB:
            print("Conflict: opppemilik selected Layer A, adjepmilik selected Layer B")
            # Tangani konflik, misalnya dengan memberikan peringatan atau mengembalikan pilihan default
    def feature_selection_a(self):
        """Feature selection slot for Layer A."""
        if not self.layerA:
            return  # No layer A available

        if hasattr(self.layerA, "selectedFeatureCount"):
            if self.layerA.selectedFeatureCount() > 0:
                self.dlg.checkBoxA.setEnabled(True)
            else:
                self.dlg.checkBoxA.setEnabled(False)

    def feature_selection_b(self):
        """Feature selection slot for Layer B."""
        if not self.layerB:
            return  # No layer B available

        if hasattr(self.layerB, "selectedFeatureCount"):
            if self.layerB.selectedFeatureCount() > 0:
                self.dlg.checkBoxB.setEnabled(True)
            else:
                self.dlg.checkBoxB.setEnabled(False)

    def push_message(self):
        """Custom message."""
        msg_title = "Select Area"
        msg_text = "Select an area where median line is going to be generated."
        msg_widget = self.iface.messageBar().createMessage(msg_title, msg_text)
        msg_button = QPushButton(msg_widget)
        btn_text = "Select Feature"
        msg_button.setText(btn_text)
        msg_button.pressed.connect(self.iface.actionSelect().trigger)
        msg_widget.layout().addWidget(msg_button)
        return msg_widget
    def valid_area_selection(self):
        """Check if valid area is selected or not."""
        if self.processing_flag:
            if self.valid_dt.selectedFeatureCount() == 1:
                self.dlg.btn_process.setEnabled(True)
                self.dockwidget.outputGroup.setEnabled(True)
                try:
                    self.iface.messageBar().popWidget(self.msg_widget)
                    self.iface.messageBar().pushMessage(
                        "Info:",
                        "Area selection success.",
                        Qgis.Success,
                        duration=3
                    )
                except RuntimeError:
                    self.iface.messageBar().pushMessage(
                        "Info:",
                        "Area selection success.",
                        Qgis.Success,
                        duration=3
                    )
            else:
                self.dockwidget.btn_process.setEnabled(False)
                self.dockwidget.outputGroup.setEnabled(False)
                self.msg_widget = self.push_message()
                self.iface.messageBar().pushWidget(self.msg_widget, Qgis.Info)

    def oppositeline(self):
        self.layerA = self.dlg.inputlayerA.currentData()
        self.layerB = self.dlg.inputlayerB.currentData()
        interpolate_interval_a = 10
        interpolate_interval_b = 10

            # Assuming 'layer_ttk' is some relevant parameter for the line_to_point_layer_new function
        layer_name_a = "Layer A Points"  # Nama untuk layer A hasil konversi
        layer_name_b = "Layer B Points"  # Nama untuk layer B hasil konversi
        

        crs_a = self.layerA.crs().authid() if self.layerA else "EPSG:4326"  # Pastikan CRS diambil dari layer A
        crs_b = self.layerB.crs().authid() if self.layerB else "EPSG:4326"  # Pastikan CRS diambil dari layer B

            # Buat layer titik dari layer garis
        self.layerttkA = line_to_point_layer_new(self.layerA, layer_name_a, crs_a)
        if self.layerttkA is not None:
                # Ambil fitur dari layer titik A
            self.list_feat_ttk_a = [feat for feat in self.layerttkA.getFeatures()]
            jml_ttk_a = len(self.list_feat_ttk_a)
            self.dlg.labelTitikA.setText(f"{jml_ttk_a} points")
        else:
            self.dlg.labelTitikA.setText("Failed to create points from Layer A")

        self.layerttkB = line_to_point_layer_new(self.layerB, layer_name_b, crs_b)
        if self.layerttkB is not None:
            # Ambil fitur dari layer titik B
            self.list_feat_ttk_b = [feat for feat in self.layerttkB.getFeatures()]
            jml_ttk_b = len(self.list_feat_ttk_b)
            self.dlg.labelTitikB.setText(f"{jml_ttk_b} points")
        else:
            self.dlg.labelTitikB.setText("Failed to create points from Layer B")
            # Merge point layers
        self.merged_pt_layer = merge_point_layers(self.layerttkA, self.layerttkB)

            # Create Voronoi diagram and Delaunay triangulation layer
        self.dt_layer = create_delaunay_triangulation(self.merged_pt_layer)

            # Perform valid Delaunay triangulation check
        self.valid_dt = valid_delaunay_triangulation(self.dt_layer, self.list_feature_a, self.list_feature_b)
        self.msg_widget = self.push_message()
        self.iface.messageBar().pushWidget(self.msg_widget, Qgis.Info)
        self.processing_flag = True

            # Grouping layers
        group_name = "Intermediary Layer"
        root = QgsProject.instance().layerTreeRoot()
        self.intermediary_group = root.addGroup(group_name)
        QgsProject.instance().addMapLayer(self.valid_dt, False)
        self.intermediary_group.addLayer(self.valid_dt)
        self.iface.setActiveLayer(self.valid_dt)

        QgsProject.instance().addMapLayer(self.layerttkA, False)
        self.intermediary_group.addLayer(self.layerttkA)
        self.iface.setActiveLayer(self.layerttkA)

        QgsProject.instance().addMapLayer(self.layerttkB, False)
        self.intermediary_group.addLayer(self.layerttkB)
        self.iface.setActiveLayer(self.layerttkB)        

            # Create Voronoi diagram layer
        self.vd_layer = create_voronoi(self.merged_pt_layer)
        QgsProject.instance().addMapLayer(self.vd_layer, False)
        self.intermediary_group.addLayer(self.vd_layer)
        self.iface.setActiveLayer(self.vd_layer)

            # Create median line for opposite layers
        median_layer_opp_result = create_median_line_opposite(self.vd_layer, self.layerA, self.layerB, self.crs)

        # Check if median_layer_opp_result is a QgsGeometry and convert it to QgsVectorLayer if needed
        if isinstance(median_layer_opp_result, QgsGeometry):
                # Create a new vector layer from the geometry
            median_layer_opp_vector = QgsVectorLayer(median_layer_opp_result.asWkt(), "Median Line Opposite", "memory")
            if not median_layer_opp_vector.isValid():
                raise Exception("Failed to create vector layer from geometry.")
            median_layer_opp = median_layer_opp_vector
        else:
            median_layer_opp = median_layer_opp_result
        input_layer_a_preprocessed = line_feature_list_to_layer(self.list_feature_a, self.crs, "Input layer A")
        input_layer_b_preprocessed = line_feature_list_to_layer(self.list_feature_b, self.crs, "Input layer B")

        list_result_layer = []
        valid_geom = self.valid_dt
        valid_geometries = [feat.geometry() for feat in valid_geom.getFeatures()]

        for feat in median_layer_opp.getFeatures():
            for valid_geom in valid_geometries:  # Iterate over each geometry
                if feat.geometry().crosses(valid_geom):
                   median_layer_opp.select(feat.id())

        if self.dlg.checkBox_titikEq.isChecked():
            eq_pt_layer = create_equidistant_point(median_layer_opp)
            list_result_layer.append(eq_pt_layer)
            

        median_layer_opp.startEditing()
        median_layer_opp.invertSelection()
        median_layer_opp.deleteSelectedFeatures()
        median_layer_opp.commitChanges()
        list_result_layer.append(median_layer_opp)

        boundary_distance = 100
        final_boundary_layer = generate_final_boundary(
            self.list_feat_ttk_a,
            self.list_feat_ttk_b,
            boundary_distance,
            median_layer_opp,
            self.crs,
            )
        list_result_layer.append(final_boundary_layer)    
        group_name = "Result Layer"
        root = QgsProject.instance().layerTreeRoot()
        result_group = root.addGroup(group_name)
        for layer in list_result_layer:
            QgsProject.instance().addMapLayer(layer, False)
            result_group.addLayer(layer)

    def halfoppositeline(self):
        self.layerA = self.dlg.inputlayerA.currentData()
        self.layerB = self.dlg.inputlayerB.currentData()
        self.layermedian = self.dlg.input_medianlayer.currentData()
        interpolate_interval_a = 10
        interpolate_interval_b = 10

            # Assuming 'layer_ttk' is some relevant parameter for the line_to_point_layer_new function
        layer_name_a = "Layer A Points"  # Nama untuk layer A hasil konversi
        layer_name_b = "Layer B Points"  # Nama untuk layer B hasil konversi
        

        crs_a = self.layerA.crs().authid() if self.layerA else "EPSG:4326"  # Pastikan CRS diambil dari layer A
        crs_b = self.layerB.crs().authid() if self.layerB else "EPSG:4326"  # Pastikan CRS diambil dari layer B

            # Buat layer titik dari layer garis
        self.layerttkA = line_to_point_layer_new(self.layerA, layer_name_a, crs_a)
        if self.layerttkA is not None:
                # Ambil fitur dari layer titik A
            self.list_feat_ttk_a = [feat for feat in self.layerttkA.getFeatures()]
            jml_ttk_a = len(self.list_feat_ttk_a)
            self.dlg.labelTitikA.setText(f"{jml_ttk_a} points")
        else:
            self.dlg.labelTitikA.setText("Failed to create points from Layer A")

        self.layerttkB = line_to_point_layer_new(self.layerB, layer_name_b, crs_b)
        if self.layerttkB is not None:
            # Ambil fitur dari layer titik B
            self.list_feat_ttk_b = [feat for feat in self.layerttkB.getFeatures()]
            jml_ttk_b = len(self.list_feat_ttk_b)
            self.dlg.labelTitikB.setText(f"{jml_ttk_b} points")
        else:
            self.dlg.labelTitikB.setText("Failed to create points from Layer B")
            # Merge point layers
        self.merged_pt_layer = merge_point_layers(self.layerttkA, self.layerttkB)

            # Create Voronoi diagram and Delaunay triangulation layer
        self.dt_layer = create_delaunay_triangulation(self.merged_pt_layer)

            # Perform valid Delaunay triangulation check
        self.valid_dt = valid_delaunay_triangulation(self.dt_layer, self.list_feature_a, self.list_feature_b)
        self.msg_widget = self.push_message()
        self.iface.messageBar().pushWidget(self.msg_widget, Qgis.Info)
        self.processing_flag = True
        self.vd_layer = create_voronoi(self.merged_pt_layer)
            # Create median line for opposite layers
        median_layer_opp_result = create_median_line_opposite(self.vd_layer, self.layerA, self.layerB, self.crs)

        # Check if median_layer_opp_result is a QgsGeometry and convert it to QgsVectorLayer if needed
        if isinstance(median_layer_opp_result, QgsGeometry):
                # Create a new vector layer from the geometry
            median_layer_opp_vector = QgsVectorLayer(median_layer_opp_result.asWkt(), "Median Line Opposite", "memory")
            if not median_layer_opp_vector.isValid():
                raise Exception("Failed to create vector layer from geometry.")
            median_layer_opp = median_layer_opp_vector
        else:
            median_layer_opp = median_layer_opp_result
        input_layer_a_preprocessed = line_feature_list_to_layer(self.list_feature_a, self.crs, "Input layer A")
        input_layer_b_preprocessed = line_feature_list_to_layer(self.list_feature_b, self.crs, "Input layer B")

        
        layer_name_a = "Layer A Points"  # Nama untuk layer A hasil konversi
        layer_name_b = "Layer B Points"  # Nama untuk layer B hasil konversi
        

        crs_a = self.layerA.crs().authid() if median_layer_opp_result else "EPSG:4326"  # Pastikan CRS diambil dari layer A
        crs_b = self.layerB.crs().authid() if self.layermedian else "EPSG:4326"  # Pastikan CRS diambil dari layer B

            # Buat layer titik dari layer garis
        self.layerttkA = line_to_point_layer_new(median_layer_opp_result, layer_name_a, crs_a)
        if self.layerttkA is not None:
                # Ambil fitur dari layer titik A
            self.list_feat_ttk_a = [feat for feat in self.layerttkA.getFeatures()]
            jml_ttk_a = len(self.list_feat_ttk_a)
            self.dlg.labelTitikA.setText(f"{jml_ttk_a} points")
        else:
            self.dlg.labelTitikA.setText("Failed to create points from Layer A")

        self.layerttkB = line_to_point_layer_new(self.layermedian, layer_name_b, crs_b)
        if self.layerttkB is not None:
            # Ambil fitur dari layer titik B
            self.list_feat_ttk_b = [feat for feat in self.layerttkB.getFeatures()]
            jml_ttk_b = len(self.list_feat_ttk_b)
            self.dlg.labelTitikB.setText(f"{jml_ttk_b} points")
        else:
            self.dlg.labelTitikB.setText("Failed to create points from Layer B")
            # Merge point layers
        self.merged_pt_layer = merge_point_layers(self.layerttkA, self.layerttkB)

            # Create Voronoi diagram and Delaunay triangulation layer
        self.dt_layer = create_delaunay_triangulation(self.merged_pt_layer)

            # Perform valid Delaunay triangulation check
        self.valid_dt = valid_delaunay_triangulation(self.dt_layer, self.list_feature_a, self.list_feature_b)
        self.msg_widget = self.push_message()
        self.iface.messageBar().pushWidget(self.msg_widget, Qgis.Info)
        self.processing_flag = True

            # Grouping layers
        group_name = "Intermediary Layer"
        root = QgsProject.instance().layerTreeRoot()
        self.intermediary_group = root.addGroup(group_name)
        QgsProject.instance().addMapLayer(self.valid_dt, False)
        self.intermediary_group.addLayer(self.valid_dt)
        self.iface.setActiveLayer(self.valid_dt)

        QgsProject.instance().addMapLayer(self.layerttkA, False)
        self.intermediary_group.addLayer(self.layerttkA)
        self.iface.setActiveLayer(self.layerttkA)

        QgsProject.instance().addMapLayer(self.layerttkB, False)
        self.intermediary_group.addLayer(self.layerttkB)
        self.iface.setActiveLayer(self.layerttkB)        

            # Create Voronoi diagram layer
        self.vd_layer = create_voronoi(self.merged_pt_layer)
        QgsProject.instance().addMapLayer(self.vd_layer, False)
        self.intermediary_group.addLayer(self.vd_layer)
        self.iface.setActiveLayer(self.vd_layer)

            # Create median line for opposite layers
        median_layer_opp_result2 = create_median_line_opposite(self.vd_layer, median_layer_opp_result, self.layermedian, self.crs)

        # Check if median_layer_opp_result is a QgsGeometry and convert it to QgsVectorLayer if needed
        if isinstance(median_layer_opp_result2, QgsGeometry):
                # Create a new vector layer from the geometry
            median_layer_opp_vector = QgsVectorLayer(median_layer_opp_result2.asWkt(), "Median Line Opposite", "memory")
            if not median_layer_opp_vector.isValid():
                raise Exception("Failed to create vector layer from geometry.")
            median_layer_opp2 = median_layer_opp_vector
        else:
            median_layer_opp2 = median_layer_opp_result2
        input_layer_a_preprocessed = line_feature_list_to_layer(self.list_feature_a, self.crs, "Input layer A")
        input_layer_b_preprocessed = line_feature_list_to_layer(self.list_feature_b, self.crs, "Input layer B")

        list_result_layer = []
        valid_geom = self.valid_dt
        valid_geometries = [feat.geometry() for feat in valid_geom.getFeatures()]

        for feat in median_layer_opp.getFeatures():
            for valid_geom in valid_geometries:  # Iterate over each geometry
                if feat.geometry().crosses(valid_geom):
                   median_layer_opp.select(feat.id())

        if self.dlg.checkBox_titikEq.isChecked():
            eq_pt_layer = create_equidistant_point(median_layer_opp2)
            list_result_layer.append(eq_pt_layer)

        median_layer_opp.startEditing()
        median_layer_opp.invertSelection()
        median_layer_opp.deleteSelectedFeatures()
        median_layer_opp.commitChanges()
        list_result_layer.append(median_layer_opp2)

        boundary_distance = 100
        final_boundary_layer = generate_final_boundary(
            self.list_feat_ttk_a,
            self.list_feat_ttk_b,
            boundary_distance,
            median_layer_opp,
            self.crs,
            )
        
        list_result_layer.append(final_boundary_layer)    
        group_name = "Result Layer"
        root = QgsProject.instance().layerTreeRoot()
        result_group = root.addGroup(group_name)
        for layer in list_result_layer:
            QgsProject.instance().addMapLayer(layer, False)
            result_group.addLayer(layer)
        else:
            self.iface.messageBar().pushMessage(
                "Warning:",
                "Please ensure one valid area is selected.",
                Qgis.Warning,
                duration=3,
            )
    def adjacentline(self):
        self.layerA = self.dlg.inputlayerA.currentData()
        self.layerB = self.dlg.inputlayerB.currentData()
        interpolate_interval_a = 10
        interpolate_interval_b = 10

            # Assuming 'layer_ttk' is some relevant parameter for the line_to_point_layer_new function
        layer_name_a = "Layer A Points"  # Nama untuk layer A hasil konversi
        layer_name_b = "Layer B Points"  # Nama untuk layer B hasil konversi
        

        crs_a = self.layerA.crs().authid() if self.layerA else "EPSG:4326"  # Pastikan CRS diambil dari layer A
        crs_b = self.layerB.crs().authid() if self.layerB else "EPSG:4326"  # Pastikan CRS diambil dari layer B

            # Buat layer titik dari layer garis
        self.layerttkA = line_to_point_layer_new(self.layerA, layer_name_a, crs_a)
        if self.layerttkA is not None:
                # Ambil fitur dari layer titik A
            self.list_feat_ttk_a = [feat for feat in self.layerttkA.getFeatures()]
            jml_ttk_a = len(self.list_feat_ttk_a)
            self.dlg.labelTitikA.setText(f"{jml_ttk_a} points")
        else:
            self.dlg.labelTitikA.setText("Failed to create points from Layer A")

        self.layerttkB = line_to_point_layer_new(self.layerB, layer_name_b, crs_b)
        if self.layerttkB is not None:
            # Ambil fitur dari layer titik B
            self.list_feat_ttk_b = [feat for feat in self.layerttkB.getFeatures()]
            jml_ttk_b = len(self.list_feat_ttk_b)
            self.dlg.labelTitikB.setText(f"{jml_ttk_b} points")
        else:
            self.dlg.labelTitikB.setText("Failed to create points from Layer B")
            # Merge point layers
        self.merged_pt_layer = merge_point_layers(self.layerttkA, self.layerttkB)

            # Create Voronoi diagram and Delaunay triangulation layer
        self.dt_layer = create_delaunay_triangulation(self.merged_pt_layer)

            # Perform valid Delaunay triangulation check
        self.valid_dt = valid_delaunay_triangulation(self.dt_layer, self.list_feature_a, self.list_feature_b)
        self.msg_widget = self.push_message()
        self.iface.messageBar().pushWidget(self.msg_widget, Qgis.Info)
        self.processing_flag = True

            # Grouping layers
        group_name = "Intermediary Layer"
        root = QgsProject.instance().layerTreeRoot()
        self.intermediary_group = root.addGroup(group_name)
        QgsProject.instance().addMapLayer(self.valid_dt, False)
        self.intermediary_group.addLayer(self.valid_dt)
        self.iface.setActiveLayer(self.valid_dt)

        QgsProject.instance().addMapLayer(self.layerttkA, False)
        self.intermediary_group.addLayer(self.layerttkA)
        self.iface.setActiveLayer(self.layerttkA)

        QgsProject.instance().addMapLayer(self.layerttkB, False)
        self.intermediary_group.addLayer(self.layerttkB)
        self.iface.setActiveLayer(self.layerttkB)        

            # Create Voronoi diagram layer
        self.vd_layer = create_voronoi(self.merged_pt_layer)
        QgsProject.instance().addMapLayer(self.vd_layer, False)
        self.intermediary_group.addLayer(self.vd_layer)
        self.iface.setActiveLayer(self.vd_layer)

        median_layer_adj = create_median_line_adjacent(self.layerA,  self.layerB, self.crs)
        input_layer_a_preprocessed = line_feature_list_to_layer(
            self.list_feature_a, self.crs, "Input layer A"
        )
        input_layer_b_preprocessed = line_feature_list_to_layer(
            self.list_feature_b, self.crs, "Input layer B"
        )
        list_result_layer = []

        valid_geom = self.valid_dt
        valid_geometries = [feat.geometry() for feat in valid_geom.getFeatures()]

        for feat in median_layer_adj.getFeatures():
            for valid_geom in valid_geometries:  # Iterate over each geometry
                if feat.geometry().crosses(valid_geom):
                    median_layer_adj.select(feat.id())

        if self.dlg.checkBox_titikEq.isChecked():
            eq_pt_layer = create_equidistant_point(median_layer_adj)
            list_result_layer.append(eq_pt_layer)      

        median_layer_adj.startEditing()
        median_layer_adj.invertSelection()
        median_layer_adj.deleteSelectedFeatures()
        median_layer_adj.commitChanges()
        list_result_layer.append(median_layer_adj)

        boundary_distance = 100
        final_boundary_layer = generate_final_boundary(
            self.list_feat_ttk_a,
            self.list_feat_ttk_b,
            boundary_distance,
            median_layer_adj,
            self.crs,
            )
        list_result_layer.append(final_boundary_layer)    
        group_name = "Result Layer"
        root = QgsProject.instance().layerTreeRoot()
        result_group = root.addGroup(group_name)
        for layer in list_result_layer:
            QgsProject.instance().addMapLayer(layer, False)
            result_group.addLayer(layer)
        else:
            self.iface.messageBar().pushMessage(
                "Warning:",
                "Please ensure one valid area is selected.",
                Qgis.Warning,
                duration=3,
            )
            


# def side_buffer_rubberbands(line_rubberband, buffer_distance, buffer_segment, buffer_side):
#     geom = QgsGeometry()
#     buffer_geom = geom.singleSidedBuffer(buffer_distance, buffer_segment, buffer_side)
