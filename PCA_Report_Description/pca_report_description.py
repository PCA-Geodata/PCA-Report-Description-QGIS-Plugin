# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PCAReportDescriptionGenerator
                                 A QGIS plugin
 Thi plugin generates a ...
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-11-14
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Valerio Pinna
        email                : vpinna@pre-contruct.com
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
import re
import win32clipboard
from qgis.core import *
from qgis.utils import iface
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QMessageBox, QToolBar, QLabel
# Initialize Qt resources from file resources.py
from .resources import *


# Import the code for the DockWidget
from .pca_report_description_dockwidget import PCAReportDescriptionGeneratorDockWidget
import os.path


class PCAReportDescriptionGenerator:
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
            'PCAReportDescriptionGenerator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PCA Report Description Generator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PCA Report Description Generator')
        self.toolbar.setObjectName(u'PCA Report Description Generator')

        #print "** INITIALIZING PCAReportDescriptionGenerator"

        self.pluginIsActive = False
        self.dockwidget = None


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
        return QCoreApplication.translate('PCA Report Description Generator', message)


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

        icon_path = ':/plugins/pca_report_description/icons/PCA_report_generator_icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PCA Report Description Generator'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING PCAReportDescriptionGenerator"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD PCAReportDescriptionGenerator"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PCA Report Description Generator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING PCAReportDescriptionGenerator"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PCAReportDescriptionGeneratorDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockwidget)
            
           
            self.DRS_group_numbers_list()
            self.DRS_cut_numbers_list()
            
            self.dockwidget.show()
            
            
            try: 
                feature_layer = QgsProject.instance().mapLayersByName('Features_for_PostEx')[0]
            except:
                return self.dontdonothing()
            else:
                feature_layer.selectionChanged.connect(self.retrieve_group_from_selection)
                
            try: 
                intervention_layer = QgsProject.instance().mapLayersByName('Interventions')[0]
            except:
                return self.dontdonothing()
            else:
                intervention_layer.selectionChanged.connect(self.retrieve_cut_from_selection)

            #tab1 - DRS
            self.dockwidget.copy_to_clipboard_tab1_pushButton.clicked.connect(self.copy_tab1_to_clipboard)
            self.dockwidget.clean_tab1_pushButton.clicked.connect(self.clean_tab1_board)
            self.dockwidget.DRS_descr_from_cut_tab1_pushButton.clicked.connect(self.string_from_DRS_cut_list)
            self.dockwidget.DRS_descr_from_group_tab1_pushButton.clicked.connect(self.string_from_DRS_group_list)
            self.dockwidget.DRS_cut_no_tab1_comboBox.currentTextChanged.connect(self.clean_tab1_board)
            self.dockwidget.DRS_group_tab1_comboBox.currentTextChanged.connect(self.clean_tab1_board)
            # self.dockwidget.DRS_group_tab1_comboBox.currentTextChanged.connect(self.clean_cut_combo)
            # self.dockwidget.DRS_cut_no_tab1_comboBox.currentTextChanged.connect(self.clean_group_combo)
            
            #ex tab 2
            # self.dockwidget.descr_to_all_tab2_pushButton.clicked.connect(self.cut_string_from_all_interventions)
            # self.dockwidget.descr_to_selected_tab2_pushButton.clicked.connect(self.cut_string_from_selected_interventions)

    def natural_sort(self, l): 
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)
        
    
    def DRS_cut_numbers_list(self):
        try:
             int_layer = QgsProject.instance().mapLayersByName("DRS_Table")[0]
        except:     
            QMessageBox.about(
            None,
            'PCA PostExcavation Plugin',
            '''This is not a valid PCA QGIS Site Plan Project''')
            return self.dontdonothing()
        else:        
            list_of_values = []
            list_of_values.clear()
           
            if int_layer is not None:
                for feat in int_layer.getFeatures():
                    if int_layer.getFeatures() != 0:
                        value = feat['Cut']
                        if value != NULL:
                            
                            if value not in list_of_values:
                                list_of_values.append(str(value))  
            
                if len(list_of_values) == 0:
                    self.dockwidget.DRS_cut_no_tab1_comboBox.setEnabled(False)
                    return self.dontdonothing()
                if len(list_of_values) != 0:
                    if list_of_values is not None:
                        sorted_list_of_values = self.natural_sort(list_of_values)
                        self.dockwidget.DRS_cut_no_tab1_comboBox.setEnabled(True)
                        self.dockwidget.DRS_cut_no_tab1_comboBox.addItems(sorted_list_of_values)
                        self.dockwidget.DRS_cut_no_tab1_comboBox.setCurrentText('') 
                        self.dockwidget.DRS_cut_no_tab1_comboBox.setMaxVisibleItems(25)
    
    def DRS_group_numbers_list(self):
        try:
             int_layer = QgsProject.instance().mapLayersByName("DRS_Table")[0]
        except:     
            QMessageBox.about(
            None,
            'PCA PostExcavation Plugin',
            '''This is not a valid PCA QGIS Site Plan Project''')
            return self.dontdonothing()
        else:        
            list_of_values = []
            list_of_values.clear()
           
            if int_layer is not None:
                for feat in int_layer.getFeatures():
                    if int_layer.getFeatures() != 0:
                        value = feat['Group']
                        if value != NULL:
                            
                            if value not in list_of_values:
                                list_of_values.append(str(value))  
            
                if len(list_of_values) == 0:
                    self.dockwidget.DRS_group_tab1_comboBox.setEnabled(False)
                    return self.dontdonothing()
                if len(list_of_values) != 0:
                    if list_of_values is not None:
                        sorted_list_of_values = self.natural_sort(list_of_values)
                        self.dockwidget.DRS_group_tab1_comboBox.setEnabled(True)
                        self.dockwidget.DRS_group_tab1_comboBox.addItems(sorted_list_of_values)
                        self.dockwidget.DRS_group_tab1_comboBox.setCurrentText('') 
                        self.dockwidget.DRS_group_tab1_comboBox.setMaxVisibleItems(25)
    
    def string_from_DRS_cut_list(self):
        try:
             DRS_table_layer = QgsProject.instance().mapLayersByName("DRS_Table")[0]
        except:     
            QMessageBox.about(
            None,
            'PCA PostExcavation Plugin',
            '''This is not a valid PCA QGIS Site Plan Project''')
            return self.dontdonothing()
        else:
            
            value = self.dockwidget.DRS_cut_no_tab1_comboBox.currentText()
            all_feature_description = []

            ###layer
            e = '''"Cut" = '''+"'"+value+"'" +"""and "Type" ilike 'Layer'"""
            DRS_table_layer.selectByExpression(e)
            count = DRS_table_layer.selectedFeatureCount()
            
            if count != 0: 
                layer_descr = []
                for f in DRS_table_layer.selectedFeatures():
                    
                    if f['Compaction'] != NULL:
                        layer_compaction = f['Compaction']
                    if f['Compaction'] == NULL:
                        layer_compaction = 'NULL'
                    
                    if f['Composition'] != NULL:
                        layer_composition = f['Composition']
                    if f['Composition'] == NULL:
                        fill_composition = 'NULL'
                    
                    if f['Tone'] != NULL:
                        layer_tone = f['Tone']
                    if f['Tone'] == NULL:
                        layer_tone= ''   

                    if f['Hue'] != NULL:
                        layer_hue = f['Hue']
                    if f['Hue'] == NULL:
                        layer_hue= ''  
                    
                    if f['Colour'] != NULL:
                        layer_colour = f['Colour']
                    if f['Colour'] == NULL:
                        layer_colour= 'NULL'  
                    
                    if f['Length'] != NULL:
                        layer_length = f['Length']
                        if layer_length[0] == '.':
                            layer_length = '0{}'.format(layer_length)
                    if f['Length'] == NULL:
                        layer_length = 'NULL'
                        
                    if f['Width'] != NULL:
                        layer_width = f['Width']
                        if layer_width[0] == '.':
                            layer_width = '0{}'.format(layer_width)
                    if f['Width'] == NULL:
                        layer_width = 'NULL'
                        
                    if f['Depth'] != NULL:
                        layer_depth = f['Depth']
                        if layer_depth[0] == '.':
                            layer_depth = '0{}'.format(layer_depth)
                    if f['Depth'] == NULL:
                        layer_depth = 'NULL'
                   
                    layer_descr.append(' The layer ({})'.format(f['Context']) )
                    layer_descr.append(' was {} {} in composition and was '.format(layer_compaction.lower(), layer_composition.lower()))
                    layer_descr.append('{} {} {} in colour.'.format(layer_tone.lower(), layer_hue.lower(), layer_colour.lower()))

                    layer_descr.append(' It measured c.{}m long, {}m wide, and {}m deep.'.format(layer_length, layer_width,layer_depth))
                    
                    all_feature_description.extend(layer_descr)

            ###cut 
            e = '''"Cut" = '''+"'"+value+"'" +"""and "Type" ilike 'Cut'"""
            DRS_table_layer.selectByExpression(e)
            count = DRS_table_layer.selectedFeatureCount()

            if count != 0: 
                for f in DRS_table_layer.selectedFeatures():
                    if f['type'] == 'Cut':
                        cut_descr = []
                        
                        if f['Category'] != NULL:
                            cut_category = f['Category']
                        if f['Category'] == NULL:
                            cut_category = 'NULL'
                        
                        if f['Cut'] != NULL:
                            cut_context_no = f['Cut']
                        if f['Cut'] == NULL:
                            cut_context_no = 'NULL'
                        
                        if f['Shape'] != NULL:
                            cut_shape = f['Shape']
                        if f['Shape'] == NULL:
                            cut_shape = 'NULL'
                            
                        if f['Sides'] != NULL:
                            cut_sides = f['Sides']
                            if cut_sides == 'Moderate':
                                cut_sides = 'Moderately'
                        if f['Sides'] == NULL:
                            cut_sides = 'NULL'

                        if f['Base'] != NULL:
                            cut_base = f['Base']
                        if f['Base'] == NULL:
                            cut_base = 'NULL'

                        if f['Length'] != NULL:
                            cut_length = f['Length']
                            if cut_length[0] == '.':
                                cut_length = '0{}'.format(cut_length)
                        if f['Length'] == NULL:
                            cut_length = 'NULL'
                            
                        if f['Width'] != NULL:
                            cut_width = f['Width']
                            if cut_width[0] == '.':
                                cut_width = '0{}'.format(cut_width)
                        if f['Width'] == NULL:
                            cut_width = 'NULL'
                            
                        if f['Depth'] != NULL:
                            cut_depth = f['Depth']
                            if cut_depth[0] == '.':
                                cut_depth = '0{}'.format(cut_depth)
                        if f['Depth'] == NULL:
                            cut_depth = 'NULL'
                        
                        cut_descr.append('The {} [{}] was {} in plan'.format(cut_category.lower(), cut_context_no, cut_shape.lower()))

                        if f['Orientation'] != '-':                           
                            if f['Orientation'] != 'N/A':
                                if f['Orientation'] != NULL:  
                                    cut_descr.append(' and was aligned {}'.format(f['Orientation'].upper().replace('E', 'east').replace('W','west').replace('N','north').replace('S','south')))
                                    cut_descr.append('. ')
                                    cut_descr.append('It had ')
                        if f['Orientation'] == '-' or f['Orientation'] == 'N/A' or f['Orientation'] == NULL:
                            cut_descr.append(', and it had ')
                        
                        
                        
                        string = cut_sides 
                        clean_str = re.sub('[(].*?[)]','',string)
                        
                        if ',' in clean_str:
                            clean_str = clean_str.replace(',', 'and')
                        if ',' not in clean_str:
                            clean_str = clean_str

                        cut_descr.append(clean_str.lower().rstrip().lstrip())
                        cut_descr.append(' sloping sides and a {} base.'.format(cut_base.lower()))
                        cut_descr.append(' It measured c.{}m long, {}m wide, and {}m deep.'.format(cut_length, cut_width,cut_depth))

                        all_feature_description = cut_descr
                        
            ###Fill(s) 
            
            e = '''"Cut" = '''+"'"+value+"'" +"""and "Type" ilike 'Fill'"""
            
            DRS_table_layer.selectByExpression(e)
            
            count = DRS_table_layer.selectedFeatureCount()
            
            if count == 1: 
                  
                for f in DRS_table_layer.selectedFeatures():
                    if f['type'] == 'Fill':
                                                
                        fill_descr = []
                        if f['Compaction'] != NULL:
                            fill_compaction = f['Compaction']
                        if f['Compaction'] == NULL:
                            fill_compaction = 'NULL'
                        
                        if f['Composition'] != NULL:
                            fill_composition = f['Composition']
                        if f['Composition'] == NULL:
                            fill_composition = 'NULL'
                        
                        if f['Tone'] != NULL:
                            fill_tone = f['Tone']
                        if f['Tone'] == NULL:
                            fill_tone= ''   

                        if f['Hue'] != NULL:
                            fill_hue = f['Hue']
                        if f['Hue'] == NULL:
                            fill_hue= ''  
                        
                        if f['Colour'] != NULL:
                            fill_colour = f['Colour']
                        if f['Colour'] == NULL:
                            fill_colour= 'NULL'  
                            
                       
                        fill_descr.append(' The composition of fill ({})'.format(f['Context']) )
                        fill_descr.append(' was {} {} and was '.format(fill_compaction.lower(), fill_composition.lower()))
                        fill_descr.append('{} {} {} in colour.'.format(fill_tone.lower(), fill_hue.lower(), fill_colour.lower()))

                        all_feature_description.extend(fill_descr)
                

            if count == 2 or count > 2: 
                
                
                fills_number = []
                fills_number.append(' It contained {} fills.'.format(count))   
                all_feature_description.extend(fills_number)
                
                for f in DRS_table_layer.selectedFeatures():
             
                    fills_descr = []
                    if f['Compaction'] != NULL:
                        fill_compaction = f['Compaction']
                    if f['Compaction'] == NULL:
                        fill_compaction = 'NULL'
                    
                    if f['Composition'] != NULL:
                        fill_composition = f['Composition']
                    if f['Composition'] == NULL:
                              fill_composition = 'NULL'
                    
                    if f['Tone'] != NULL:
                        fill_tone = f['Tone']
                    if f['Tone'] == NULL:
                        fill_tone= ''   

                    if f['Hue'] != NULL:
                        fill_hue = f['Hue']
                    if f['Hue'] == NULL:
                        fill_hue= ''  
                    
                    if f['Colour'] != NULL:
                        fill_colour = f['Colour']
                    if f['Colour'] == NULL:
                        fill_colour= 'NULL'  
                        
                    if (int(f['Context']) % 2) == 0:
                        fills_descr.append(' Fill ({})'.format(f['Context']) )
                        fills_descr.append(' was {}, with a {} {} {} colour and was composed of {}.'.format(fill_compaction.lower(),fill_tone.lower(), fill_hue.lower(), fill_colour.lower(), fill_composition.lower()))
                    
                    if (int(f['Context']) % 2) != 0:
                        fills_descr.append(' Fill ({})'.format(f['Context']) )
                        fills_descr.append(' was {}, with a {} {} {} colour and {} composition.'.format(fill_compaction.lower(),fill_tone.lower(), fill_hue.lower(), fill_colour.lower(), fill_composition.lower()))
                         
                    all_feature_description.extend(fills_descr)
        
            #DRS_tab_result_text =  (('\n\n').join(map(str,all_feature_description)))
            
            self.dockwidget.DRS_tab1_result_plainTextEdit.setPlainText(('').join(map(str,all_feature_description)))
        
    def string_from_DRS_group_list(self):
        try:
            DRS_table_layer = QgsProject.instance().mapLayersByName("DRS_Table")[0]
        except:     
            QMessageBox.about(
            None,
            'PCA PostExcavation Plugin',
            '''This is not a valid PCA QGIS Site Plan Project''')
            return self.dontdonothing()
        else:
            
            group_value = self.dockwidget.DRS_group_tab1_comboBox.currentText()
            if group_value == '':   
                return self.dontdonothing()
            else:
                all_group_description = []
                           
                e = '''"Group" = '''+"'"+group_value+"'" +"""and "Type" ilike 'Cut'"""
                
                DRS_table_layer.selectByExpression(e)
                
                count = DRS_table_layer.selectedFeatureCount()
                

                if count == 1:
                    for f in DRS_table_layer.selectedFeatures():
                        cut_number = f['Cut']
                    
                    self.dockwidget.DRS_cut_no_tab1_comboBox.setCurrentText(cut_number)
                    
                    return self.string_from_DRS_cut_list()
                
                if  count > 1:
                    self.clean_cut_combo()
                    # Cuts average data
                    group_cuts_list = []
                    cut_shape_list = []
                    cut_sides_list = []
                    cut_base_list = []
                    cut_orientations_list = []
                    cut_width_list = []
                    cut_depth_list = []
                    
                    for f in DRS_table_layer.selectedFeatures():
                        cut_number = f['Cut']
                        if cut_number not in group_cuts_list:
                            group_cuts_list.append('[{}]'.format(str(cut_number)))
                        
                        if f['Shape'] != NULL:
                            cut_shape = f['Shape']
                            if cut_shape.lower() not in cut_shape_list:
                                cut_shape_list.append(cut_shape.lower())

                        if f['Sides'] != NULL:
                            cut_sides = f['Sides']
                            
                            #clean sides 
                            string = cut_sides 
                            clean_str = re.sub('[(].*?[)]','',string)
                            
                            if ',' in clean_str:
                                clean_str = clean_str.replace(',', 'and')
                            if ',' not in clean_str:
                                clean_str = clean_str
                            
                            clean_side_string = clean_str.lower().rstrip().lstrip()
                            if clean_side_string not in cut_sides_list:
                                cut_sides_list.append(clean_side_string)
                                
                        if f['Base'] != NULL:
                            cut_base = f['Base']
                            if cut_base.lower() not in cut_base_list:
                                cut_base_list.append(cut_base.lower())        
                        
                        if f['Orientation'] != '-':                           
                            if f['Orientation'] != 'N/A':
                                if f['Orientation'] != NULL:  
                                    cut_orientation = f['Orientation'].upper()
                                    if cut_orientation not in cut_orientations_list:
                                        cut_orientations_list.append(cut_orientation)   
                                            
                        if f['Width'] != NULL:
                            cut_width = f['Width']
                            
                            if cut_width[0] == '.':
                                cut_width = '0{}'.format(cut_width)
                            cut_width_list.append(cut_width)   

                        if f['Depth'] != NULL:
                            cut_depth = f['Depth']
                            
                            if cut_depth[0] == '.':
                                cut_depth = '0{}'.format(cut_depth)
                            cut_depth_list.append(cut_depth)  
                          
                    
                    # Fills cut by cut
                    all_features_description = []
                    
                    

                    for cut in DRS_table_layer.selectedFeatures():
                        all_cut_description = []
                        
                        cut_no = cut['Cut']
                        all_cut_description.append('\n')                  
                        all_cut_description.append('[{}]'.format(str(cut_no)))
                        
                        all_cut_description.append('\n')

                    
                        
                        #select fills for the cut
                        e = '''"Cut" = '''+"'"+cut_no+"'" +"""and "Type" ilike 'Fill'"""
                
                        DRS_table_layer.selectByExpression(e)
                        cut_fill_count = DRS_table_layer.selectedFeatureCount()

                        
                        
                        fills_number = []
                        if cut_fill_count == 1:
                            fills_number.append(' It contained {} fill.\n'.format(cut_fill_count)) 
                        if cut_fill_count > 1:
                            fills_number.append(' It contained {} fills.\n'.format(cut_fill_count))   
                        all_cut_description.extend(fills_number)
                        
                        for f in DRS_table_layer.selectedFeatures():
                            print (f['Context'])
                            fills_descr = []
                            if f['Compaction'] != NULL:
                                fill_compaction = f['Compaction']
                            if f['Compaction'] == NULL:
                                fill_compaction = 'NULL'
                                                    
                            if f['Composition'] != NULL:
                                fill_composition = f['Composition']
                            if f['Composition'] == NULL:
                                fill_composition = 'NULL'
                            
                            if f['Tone'] != NULL:
                                fill_tone = f['Tone']
                            if f['Tone'] == NULL:
                                fill_tone= ''   

                            if f['Hue'] != NULL:
                                fill_hue = f['Hue']
                            if f['Hue'] == NULL:
                                fill_hue= ''  
                            
                            if f['Colour'] != NULL:
                                fill_colour = f['Colour']
                            if f['Colour'] == NULL:
                                fill_colour= 'NULL'

                            if f['Fill_Sequence'] != NULL:
                                fill_sequence = f['Fill_Sequence'].replace('/',' of ')
                                
                                
                                
                                
                            if (int(f['Context']) % 2) == 0:
                                fills_descr.append(' Fill ({}) - ({}) -'.format(f['Context'], fill_sequence) )
                                fills_descr.append(' was {}, with a {} {} {} colour and was composed of {}.'.format(fill_compaction.lower(),fill_tone.lower(), fill_hue.lower(), fill_colour.lower(), fill_composition.lower()))
                                fills_descr.append('\n')
                                
                            if (int(f['Context']) % 2) != 0:
                                fills_descr.append(' Fill ({}), - ({}) -'.format(f['Context'], fill_sequence) )
                                fills_descr.append(' was {}, with a {} {} {} colour and {} composition.'.format(fill_compaction.lower(),fill_tone.lower(), fill_hue.lower(), fill_colour.lower(), fill_composition.lower()))
                                fills_descr.append('\n')
                        
                            all_cut_description.extend(fills_descr)
                            
            
                        all_features_description.extend(all_cut_description)
                    

                    
                    
                    list_of_cuts = ', ' .join(str(e) for e in self.natural_sort(group_cuts_list))
                    list_of_cut_shapes = ' and ' .join(str(e) for e in cut_shape_list)
                    list_of_cut_sides = ' to ' .join(str(e) for e in cut_sides_list) 
                    list_of_cut_bases = ' to ' .join(str(e) for e in cut_base_list) 
                    list_of_cut_orientations = ' and ' .join(str(e) for e in cut_orientations_list) 
                    

                    # Title
                    all_group_description.append('{} ({})'.format(group_value,list_of_cuts))
                    
                    all_group_description.append('\n')
                    
                    # Text Cut
                    all_group_description.append('{} had a {} shape with {} sloping sides, a {} base, and was aligned {}.'.format(group_value, list_of_cut_shapes, list_of_cut_sides, list_of_cut_bases, list_of_cut_orientations.replace('E', 'east').replace('W','west').replace('N','north').replace('S','south')))
                    all_group_description.append(' It measured c. ?????m long, between {}m and {}m and between {}m and {}m deep.'.format(min(cut_width_list), max(cut_width_list),min(cut_depth_list),max(cut_depth_list)))

                    all_group_description.append('\n\nFills:')
                    all_group_description.append('\n')
                    # Fills text
                    
                    all_group_description.append(('').join(map(str,all_features_description)))
                    
                    
                    self.dockwidget.DRS_tab1_result_plainTextEdit.setPlainText(('').join(map(str,all_group_description)))
                
    def copy_tab1_to_clipboard(self):
        DRS_tab_result_text = self.dockwidget.DRS_tab1_result_plainTextEdit.toPlainText()                
                            
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(DRS_tab_result_text)
        win32clipboard.CloseClipboard()
        
    def clean_tab1_board(self):
        self.dockwidget.DRS_tab1_result_plainTextEdit.setPlainText('')

    def clean_cut_combo(self):
        self.dockwidget.DRS_cut_no_tab1_comboBox.setCurrentText('')
        
    def clean_group_combo(self):
        self.dockwidget.DRS_group_tab1_comboBox.setCurrentText('')   
        

    def retrieve_group_from_selection(self):
        
        try: 
                feature_layer = QgsProject.instance().mapLayersByName('Features_for_PostEx')[0]
        except:
            return self.dontdonothing()
        
        else:
        
            count = feature_layer.selectedFeatureCount()
            if count == 1:
                for f in feature_layer.selectedFeatures():
                    if f['Group'] != NULL:
                        group_value = f['Group']
                    
                        self.dockwidget.DRS_group_tab1_comboBox.setCurrentText(group_value) 
            if count > 1:
                self.dockwidget.DRS_group_tab1_comboBox.setCurrentText('') 
            if count == 0:
                self.dockwidget.DRS_group_tab1_comboBox.setCurrentText('') 


    def retrieve_cut_from_selection(self):
        try: 
                intervention_layer = QgsProject.instance().mapLayersByName('Interventions')[0]
        except:
            return self.dontdonothing()
        
        else:
        
            count = intervention_layer.selectedFeatureCount()
            if count == 1:
                for f in intervention_layer.selectedFeatures():
                    if f['context_no'] != NULL:
                        cut_value = f['context_no']
                    
                        self.dockwidget.DRS_cut_no_tab1_comboBox.setCurrentText(str(cut_value)) 
            if count > 1:
                self.dockwidget.DRS_cut_no_tab1_comboBox.setCurrentText('') 
            if count == 0:
                self.dockwidget.DRS_cut_no_tab1_comboBox.setCurrentText('') 
    def dontdonothing(self):
            pass
        
        
        


