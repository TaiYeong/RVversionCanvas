'''
    #!/Applications/RV64.app/Contents/MacOS/py-interp

    # Import PySide classes
    import sys
    from PySide.QtCore import *
    from PySide.QtGui import *

    # Create a Qt application.
    # IMPORTANT: RV's py-interp contains an instance of QApplication;
    # so always check if an instance already exists.
    app = QApplication.instance()
    if app == None:
        app = QApplication(sys.argv)

    # Display the file path of the app.
    print app.applicationFilePath()

    # Create a Label and show it.
    label = QLabel("Using RV's PySide")
    label.show()

    # Enter Qt application main loop.
    app.exec_()

    sys.exit()
    
'''
from rv.rvtypes import *
from rv.commands import *
from rv.extra_commands import *


import versionCanvas_view
import versionCanvas_toolkit as vc_toolkit
from versionCanvas_items import RVSourceItem
from versionCanvas_supplier import RVSourceSupplier
from versionCanvas_path import is_linux, is_windows, LnxCmdOperator, WinCmdOperator
from version_mode import VersioningMode
from movCon_view import MovConView
from giantCon_toolkit import init_con_mu_command, do_giant_convert
import sys, os
from PySide2.QtWidgets import QApplication

class GiantstepToolkit(MinorMode):

    def __init__(self):
        MinorMode.__init__(self)
        self.init("version-canvas",
                    [ ("key-down--1", self.open_tool, "Open Version Canvas")
                     ],
                    None,
                    [ ("Giantstep",
                        [   ("Open Version Canvas", self.open_tool, "1", None),
                            ("Version Up", self.version_up, "Alt+Up",   None),
                            ("Version Down", self.version_down, "Alt+Down", None),
                            ("Giant Converter..", self.open_converter, "0", None)
                        ] 
                    )] )
        self.view = None
        self.from_dropped = False
        self.clear_tar_nodes = []

    def open_tool(self, event) -> None:
        print("This is Server !!! ")
        self.view = versionCanvas_view.MainEngine(_parent= QApplication.activeWindow())
        self.view.show()
        
        
    def source_setup(self, event):
        #  event.reject() is done to allow other functions bound to
        #  this event to get a chance to modify the state as well. If
        #  its not rejected, the event will be eaten and no other call
        #  backs will occur.
        if self.from_dropped == True:
            return
        if self.view != None and self.view.isVisible() == True:
            return
        event.reject()

        args = event.contents().split(";;")
        
        
        
        source_group = args[0]
        

        file_source  = vc_toolkit.group_member_of_type(source_group, "RVFileSource")
        # image_source = vc_toolkit.group_member_of_type(source_group, "RVImageSource")
        # source       = file_source if image_source == None else image_source
        

        
        _path = vc_toolkit.get_filepath_from_fileSource(file_source)
        
        switch_name = vc_toolkit.get_switch_name_from_path(_path)
        tar_switch = vc_toolkit.create_switch_node(switch_name)
        
        
        self.clear_tar_nodes.append(source_group)
        
        vc_toolkit.connect_source_to_switch(source_group, tar_switch)
        vc_toolkit.connect_node_to_node(tar_switch, "defaultSequence")
        
        vc_toolkit.set_view_root()
        
        self.from_dropped =True
    
   
    
    def clear_sources(self, event) -> None:
        vc_toolkit.clear_nodes_except_tarType("RVSwitchGroup")
            
    
    def version_up(self, event) -> None:
        
        # Get SwitchGroup node from current frame
        cur_switch = vc_toolkit.get_switch_node_from_curframe()
        if cur_switch == "":
            vm_toolkit = VersioningMode()
            vm_toolkit.version_up()
            return
        # Get Source Nodes from SwitchGroup node
        # Get Fullpaths from source node
        # Get version number from fullpath
        # Make a list which is consist of source item(instance)
            # source item :
            #   - _idx      :int
            #   - _fullpath :str
            #   - vernum    :str
        sources = vc_toolkit.get_sources_from_switch(cur_switch)
        
        rv_source_supplier = RVSourceSupplier(cur_switch, sources)
    
        
        if rv_source_supplier.need_to_add_new_upper_source() == True:
            # if there is nowhere to go up, check whether upper version exists
            latest_version_source_item = rv_source_supplier.get_RVSourceItems()[0]
            latest_fullpath = latest_version_source_item.get_fulllpath()
            next_fullpath = vc_toolkit.up_func(latest_fullpath)
            if next_fullpath != None and vc_toolkit.get_filepath_from_curframe() != next_fullpath:
                displayFeedback(f"Current : {next_fullpath}", 3.0)
                vc_toolkit.add_source_to_switch(next_fullpath, cur_switch, "prev")
        else:
            # if there is upper version, add source and connect to switch
            RV_source_item = rv_source_supplier.get_up_version_sourceItem()
            src_grp_name = RV_source_item.get_name()
            displayFeedback(f"Current - index : {RV_source_item.get_fulllpath()}", 3.0)
            vc_toolkit.set_current_source_of_switch(cur_switch, src_grp_name)
            
        vc_toolkit.set_view_root()
           
    def version_down(self, event) -> None:
        # Get SwitchGroup node from current frame
        cur_switch = vc_toolkit.get_switch_node_from_curframe()
        if cur_switch == "":
            vm_toolkit = VersioningMode()
            vm_toolkit.version_down()
            return
        # Get Source Nodes from SwitchGroup node
        # Get Fullpaths from source node
        # Get version number from fullpath
        # Make a list which is consist of source item(instance)
            # source item :
            #   - _idx      :int
            #   - _fullpath :str
            #   - vernum    :str
        sources = vc_toolkit.get_sources_from_switch(cur_switch)
        
        rv_source_supplier = RVSourceSupplier(cur_switch, sources)
    
        
        if rv_source_supplier.need_to_add_new_lower_source() == True:
            # if there is nowhere to go up, check whether upper version exists
            the_last_version_source_item = rv_source_supplier.get_RVSourceItems()[-1]
            last_ver_fullpath = the_last_version_source_item.get_fulllpath()
            prev_fullpath = vc_toolkit.down_func(last_ver_fullpath)
            if prev_fullpath != None and vc_toolkit.get_filepath_from_curframe() != prev_fullpath:
                displayFeedback(f"Current : {prev_fullpath}", 3.0)
                vc_toolkit.add_source_to_switch(prev_fullpath, cur_switch, "after")
        else:
            # if there is upper version, add source and connect to switch
            RV_source_item = rv_source_supplier.get_down_version_sourceItem()
            src_grp_name = RV_source_item.get_name()
            displayFeedback(f"Current - index : {RV_source_item.get_fulllpath()}", 3.0)
            vc_toolkit.set_current_source_of_switch(cur_switch, src_grp_name)
            
        vc_toolkit.set_view_root()
        
       
    def open_converter(self, event) -> None:
        init_con_mu_command()
        do_giant_convert()
 
def createMode():
    return GiantstepToolkit() 
