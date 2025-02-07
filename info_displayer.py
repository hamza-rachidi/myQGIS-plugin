# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfoDisplayer
                                 A QGIS plugin
 This plugin aims to showcase relevant informations about your open project
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-02-06
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Hamza widgets Inc.
        email                : hamza.rachidi@ensg.eu
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
from qgis.PyQt.QtWidgets import QAction

# imports to add errors handling 
from qgis.core import Qgis

# imports for the first user story 
from qgis.core import QgsProject, QgsMapLayerType, QgsWkbTypes

# imports for the second user story 
from qgis.core import QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.gui import QgsMapToolEmitPoint

# imports for the third user story 
import requests

# imports for the forth user story 
from qgis.core import QgsGeometry, QgsFeatureRequest

# imports for the fifth user story 
from qgis.core import QgsVectorLayer, QgsFeature, QgsField, QgsFields, QgsSymbol, QgsSimpleLineSymbolLayer, QgsSingleSymbolRenderer
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor 

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .info_displayer_dialog import InfoDisplayerDialog
import os.path


class InfoDisplayer:
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
            'InfoDisplayer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Info Displayer')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # add the class for the first user story
        self.dlg = InfoDisplayerDialog()

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
        return QCoreApplication.translate('InfoDisplayer', message)


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

        icon_path = ':/plugins/info_displayer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'My plugin created'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Info Displayer'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        self.last_clicked_point_native = None
        self.last_clicked_point_wgs84 = None
        self.reset_fields() 
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = InfoDisplayerDialog()

        # call the function for the first user story
        self.populate_point_layers()

        # Set up the map tool to capture clicked points and then call the 2nd user story function
        self.map_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.map_tool.canvasClicked.connect(self.capture_clicked_point)
        self.iface.mapCanvas().setMapTool(self.map_tool)
        
        # Connect the button "Rechercher" to the defined method handle_search
        self.dlg.searchButton.clicked.connect(self.handle_search)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.reset_fields()

    def populate_point_layers(self):
        """Populate the combo box with point layers from the current project."""

        # Iterate through all layers in the project
        for couche in QgsProject.instance().mapLayers().values():
            # Check if the layer is a vector layer and has point geometry before displaying, otherwise linear and polygon vector as well as rasters won't be displayed
            if couche.type() == QgsMapLayerType.VectorLayer and couche.geometryType() == QgsWkbTypes.PointGeometry:
                self.dlg.listeCouchesPonctuelles.addItem(couche.name())

    def transform_coordinates(self, point, source_crs, target_crs):
        """Transforme un point d'un CRS source vers un CRS cible"""
        transform = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
        return transform.transform(point)

    def capture_clicked_point(self, point):
        """Capture the clicked point on the map and display its coordinates in WGS 84 (EPSG:4326)."""
        
        # Define the source and target coordinate reference systems
        crs_source = self.iface.mapCanvas().mapSettings().destinationCrs()  # get the current CRS of the map
        crs_cible = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84

        self.last_clicked_point_native = QgsPointXY(point.x(), point.y())

        self.last_clicked_point_wgs84 = self.transform_coordinates(point, crs_source, crs_cible)

        # Round the coordinates to 5 decimals
        latitude = round(self.last_clicked_point_wgs84.x(), 5)
        longitude = round(self.last_clicked_point_wgs84.y(), 5)

        # Update the labels with the coordinates
        self.dlg.labelvaleur_Longitude.setText(str(longitude))
        self.dlg.labelvaleur_Latitude.setText(str(latitude))

        # Address retrieval and display
        adresse = self.get_nearest_address(latitude, longitude)
        self.dlg.labelAdresse_Displayed.setText(adresse)  
        self.dlg.labelAdresse_Displayed.setReadOnly(True) # so that the user doesn't have access to change
        self.last_clicked_point_source_crs = point

    def get_nearest_address(self, latitude, longitude):
        """Make a request to the GeoPlatform API to obtain the nearest address."""
        # build the url format, to get only the nearest BAN address we specify limit parameter equal to 1 and for the moment the type to housenumber
        url = f"https://data.geopf.fr/geocodage/reverse?lat={longitude}&lon={latitude}&limit=1&type=housenumber"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Checks whether the request was successful
            data = response.json()

            if "features" in data and len(data["features"]) > 0:
                properties = data["features"][0]["properties"]
                voie = properties.get("name", "N/A")
                code_insee = properties.get("citycode", "N/A")
                commune = properties.get("city", "N/A")

                return f"{voie}\n{code_insee}\n{commune}"
            else:
                return "Aucune adresse trouvée."
        
        except requests.RequestException as e:
            return f"Erreur lors de la requête: {e}"

    def reset_fields(self):
        """Réinitialise les champs des coordonnées et de l'adresse."""
        self.dlg.listeCouchesPonctuelles.clear()
        self.dlg.labelvaleur_Longitude.setText("")
        self.dlg.labelvaleur_Latitude.setText("")
        self.dlg.labelAdresse_Displayed.setText("") 
        self.dlg.resultDisplay.setText("")
        self.dlg.distanceInput.setText("")

    def create_buffer(self, clicked_point, distance_in_meters):
        """Creates a buffer zone around the clicked point.
        :return: a QgsGeometry object representing the buffer zone"""
        point_geometry = QgsGeometry.fromPointXY(clicked_point)
        buffer_geometry = point_geometry.buffer(distance_in_meters, 10)  # 10 was chosen as the number of segments for the circle
        
        return buffer_geometry
    
    def count_objects_in_buffer(self, buffer_geometry, layer):
        """Counts the layer objects present in the buffer zone.

        :return: Le nombre d'objets dans la zone tampon."""
        # Retrieve the bounding box of the buffer zone
        bbox = buffer_geometry.boundingBox()
        
        # Create a query to filter objects within the bounding box
        request = QgsFeatureRequest().setFilterRect(bbox)
        
        # Count objects that intersect the bounding box
        count = 0
        for feature in layer.getFeatures(request):
            if buffer_geometry.intersects(feature.geometry()):
                count += 1
        
        return count
    
    def handle_search(self):
        """The  function that implements the 4th user story and handles the user counting request"""
        # Captures the distance entered by the user
        distance_text = self.dlg.distanceInput.text()
        try:
            distance_meter = float(distance_text)  # Convertir en nombre
        except ValueError:
            self.iface.messageBar().pushMessage("Error", "Distance invalide, réecris une valeur numérique", level=Qgis.Critical)
            self.dlg.resultDisplay.setText("Distance invalide")
            return

        # Retrieve the clicked point that is from now on stored
        if not hasattr(self, 'last_clicked_point_native'):
            self.dlg.resultDisplay.setText("Aucun point cliqué")
            return
        point = self.last_clicked_point_native

        # Retrieve the layer selected from the drop-down menu of the 1st user story
        layer_name = self.dlg.listeCouchesPonctuelles.currentText()
        layers = QgsProject.instance().mapLayersByName(layer_name)
        print (layers)
        if len(layers) > 1:
            self.iface.messageBar().pushMessage("Warning", "Attention ! plusieurs couches portent ce nom, pense à renommer les noms de tes couches ", level=Qgis.Critical)
        layer = layers[0] # in case there are many layers with the same name 

        buffer_geometry = self.create_buffer(point, distance_meter)
        layer_crs = layer.crs()
        map_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        buffer_geometry.transform(QgsCoordinateTransform(map_crs, layer_crs, QgsProject.instance()))

        # Comptage des objets dans la zone tampon
        count = self.count_objects_in_buffer(buffer_geometry, layer)

        self.dlg.resultDisplay.setText(str(count))

        # Remove the old buffer zone if it exists
        self.remove_old_buffer_layer()

        # Create a new temporary layer for the buffer zone
        buffer_layer = self.create_temporary_buffer_layer()

        # Add the buffer zone to the layer
        self.add_buffer_to_layer(buffer_layer, buffer_geometry)

        # Add the temporary layer to the project
        QgsProject.instance().addMapLayer(buffer_layer)

    def create_temporary_buffer_layer(self):
        """
        Creates a temporary layer to display the buffer zone.
        """
        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Zone tampon", "memory")
        
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()
        
        # Configure the style of the buffer zone
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_layer = QgsSimpleLineSymbolLayer(color=QColor(0, 0, 0), width=0.5)
        symbol.changeSymbolLayer(0, symbol_layer)
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        
        return layer

    def add_buffer_to_layer(self, layer, buffer_geometry):
        """Adds the buffer zone to the temporary layer.  """
        feature = QgsFeature()
        feature.setGeometry(buffer_geometry)
        feature.setAttributes([1]) 

        layer.dataProvider().addFeatures([feature])
        layer.updateExtents()

    def remove_old_buffer_layer(self):
        """ Deletes exisiting layers if there are ones"""
        # Récupérer la couche temporaire existante
        old_layer = QgsProject.instance().mapLayersByName("Zone tampon")
        if old_layer:
            QgsProject.instance().removeMapLayer(old_layer[0].id())
            
