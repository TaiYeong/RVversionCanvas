
from __future__ import annotations
from PySide2.QtWidgets import (
                                    QShortcut, QWidget, QPushButton, QSpacerItem, QComboBox, QRadioButton,
                                    QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QSizePolicy, QMainWindow,
                                    QDesktopWidget, QTabWidget, QLabel, QFrame, QAbstractItemView, QGridLayout
                            )
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QColor, QKeySequence
from functools import partial
from os import system

from versionCanvas_supplier import ItemSupplier
import versionCanvas_toolkit as vc_toolkit
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from versionCanvas_items import ProjectItem, SeqItem, ShotItem, TaskItem, VersionItem

from rv.commands import *


def move_2_center(main_view):
    qr = main_view.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    main_view.move(qr.topLeft())

class MessageBox():
    pass


class SignalSetter():
    main_wg         :MainEngine             = None
    entity_wg       :EntityWidget           = None
    collector_wg    :TargetCollectorWidget  = None
    filtering_wg    :FilteringWidget        = None
    btns_wg         :ButtonsGRP             = None
    def set_main_wg(self, _main :MainEngine) -> None:
        self.main_wg = _main
    def set_entity_wg(self, _entity_wg :EntityWidget) -> None:
        self.entity_wg = _entity_wg
    def set_collector_wg(self, _col_wg :TargetCollectorWidget) -> None:
        self.collector_wg = _col_wg
    def set_filtering_wg(self, _filtering_wg :FilteringWidget) -> None:
        self.filtering_wg = _filtering_wg
    def set_btns_wg(self, _btn_wg :ButtonsGRP) -> None:
        self.btns_wg = _btn_wg
    
    def get_main_wg(self) -> MainEngine:
        return self.main_wg
    def get_entity_wg(self) -> EntityWidget:
        return self.entity_wg
    def get_collector_wg(self) -> TargetCollectorWidget:
        return self.collector_wg
    def get_filtering_wg(self) -> FilteringWidget:
        return self.filtering_wg
    def get_btns_wg(self) -> ButtonsGRP:
        return self.btns_wg
    
    def set_signals(self) -> None:
        self.get_main_wg().to_left_btn.clicked.connect(self.set_target_shots)
        self.get_main_wg().to_right_btn.clicked.connect(self.unstage_selected_shot)
        self.get_filtering_wg()._SELECTED_PIPE_STEP_.connect(self.do_filter)
        self.get_btns_wg().load_versions_btn.clicked.connect(self.load_targets)
        self.get_btns_wg().clear_all_btn.clicked.connect(self.clear_targes)
        self.get_btns_wg().open_dir_btn.clicked.connect(self.open_dir)
        self.shortcut_ver_up = QShortcut(QKeySequence(Qt.Key_Up + Qt.AltModifier), self.get_main_wg())
        self.shortcut_ver_up.activated.connect(self.version_up)
        self.shortcut_ver_down = QShortcut(QKeySequence(Qt.Key_Down + Qt.AltModifier), self.get_main_wg())
        self.shortcut_ver_down.activated.connect(self.version_down)
        
        self.shortcut_unstage_shot = QShortcut(QKeySequence(Qt.Key_Delete), self.get_collector_wg())
        self.shortcut_unstage_shot.activated.connect(self.unstage_selected_shot)

    def open_dir(self) -> None:
        version_item = self.get_collector_wg().get_selected_version()
        if version_item == None:
            return
        tar_path = version_item.get_fullpath()
        system(f"nautilus {tar_path}")

    def setup_filtering_ui(self, _status :bool=True) -> None:
        # # Add filtering button in buttons group tabWidget
        # Get Union of shots' pipeline steps
        # Add filtering tabwidget between collector tab and button group tab
        #   - add union of pipeline steps' radiobox 
        #   - set signal of radiobox to slot
        if _status == True:
            self.get_main_wg().add_filtering_ui()
            step_union = self.get_collector_wg().get_union_of_pipestep()
            self.get_filtering_wg().add_radiobuttons(step_union)
            
            
        else:
            self.get_filtering_wg().clear_all_radiobuttons()
            self.get_main_wg().pop_filtering_ui()

    def set_target_shots(self) -> None:
        self.get_collector_wg().clear_shots()
        selected_shots = self.get_entity_wg().get_selected_shots()
        
        self.get_collector_wg().set_target_shots(selected_shots)
        
        self.setup_filtering_ui(True)

    def load_targets(self) -> None:
        all_video_tars = []
        target_shots = self.get_collector_wg().get_target_shots()
        for _shot in target_shots:
            version_item = _shot.get_cur_version()
            all_video_tars.append(version_item.get_fullpath())
        
        clearSession()
        
        for _tar in all_video_tars:
            switch_name = vc_toolkit.get_switch_name_from_path(_tar)
            vc_toolkit.add_new_source(_tar, switch_name, "after")
        
    def clear_targes(self) -> None:
        self.get_collector_wg().clear_shots()
        if self.get_collector_wg().is_empty() == True:
            self.setup_filtering_ui(False)
    
    def version_up(self) -> None:
        print("Version up")
        # cur_vernum_path = vc_toolkit.get_filepath_from_curframe()
        # to_vernum_path = vc_toolkit.get_next_ver_path(cur_vernum_path)
    
    def version_down(self) -> None:
        print("Version down")

    def unstage_selected_shot(self) -> None:
        self.get_collector_wg().delete_custom_item()
        if self.get_collector_wg().is_empty() == True:
            self.setup_filtering_ui(False)
            
    def do_filter(self, selected_step :str) -> None:
        self.get_collector_wg().set_common_pipestep(selected_step)
        

class ShotItemWidget(QWidget):
    def __init__(self, _parent :QWidget=None) -> None:
        super(ShotItemWidget, self).__init__(_parent)
        
        self.item_supplier = None
        
        self.container = QFrame()
        self.container.setFrameShape(QFrame.Box)
        self.container.setFrameShadow(QFrame.Raised)
        self.container.setFixedHeight(60)
        
        self.shot_name_lb = QLabel()
        self.task_cb = QComboBox()
        self.ver_cb = QComboBox()
        
        self.task_cb.currentIndexChanged.connect(self.set_versions)
        
        self.sub_vl = QVBoxLayout()
        self.sub_vl.addWidget(self.task_cb)
        self.sub_vl.addWidget(self.ver_cb)
        self.sub_vl.setStretch(0, 1)
        self.sub_vl.setStretch(1, 1)
        
        self.main_hl = QHBoxLayout(self.container)
        self.main_hl.addWidget(self.shot_name_lb)
        self.main_hl.addLayout(self.sub_vl)
        self.main_hl.setStretch(0, 1)
        self.main_hl.setStretch(1, 2)
        
        self.root_vl = QVBoxLayout()
        self.root_vl.addWidget(self.container)
        
        self.setLayout(self.root_vl)
        
    def set_supplier(self, _supplier :ItemSupplier) -> None:
        self.item_supplier = _supplier
        
    def get_supplier(self) -> ItemSupplier:
        return self.item_supplier

    def set_name(self, _name) -> None:
        self.shot_name_lb.setText(_name)
        
    def set_tasks(self, _task_items :List[TaskItem]) -> None:
        self.task_cb.clear()
        for _task_item in _task_items:
            self.task_cb.addItem(_task_item.get_name(), userData=_task_item)
            
    def get_cur_task(self, _idx :int=-1) -> TaskItem:
        if _idx == -1:
            return self.task_cb.currentData(Qt.UserRole)
        else:
            return self.task_cb.itemData(_idx, Qt.UserRole)
        
    def get_all_steps(self) -> List[str]:
        all_steps = [(self.task_cb.itemData(_idx, Qt.UserRole)).get_step_name() for _idx in range(self.task_cb.count())]
        return all_steps
        
    def set_versions(self, task_idx :int) -> None:
        self.ver_cb.clear()
        
        task_item = self.get_cur_task(task_idx)
        if task_item == None:
            return None
        
        shot_item = task_item.get_parent()
        seq_item  = shot_item.get_parent()
        prj_item  = seq_item.get_parent()
        ver_items = self.get_supplier().get_versions(prj_item, seq_item, shot_item, task_item)
        
        if ver_items == None or ver_items == []:
            return
        for _item in ver_items:
            self.ver_cb.addItem(_item.get_name(), userData=_item)

    def get_cur_version(self, _idx :int=-1) -> VersionItem:
        return self.ver_cb.currentData(Qt.UserRole)
    
    def set_current_step_by_filtering(self, selected_step :str) -> None:
        tar_idx = 0
        for _idx in range(self.task_cb.count()):
            _check_stepname = (self.task_cb.itemData(_idx, Qt.UserRole)).get_step_name()
            if _check_stepname == selected_step:
                tar_idx = _idx
                break
        self.task_cb.setCurrentIndex(tar_idx)
        
class ButtonsGRP(QWidget):
    def __init__(self, _parent :QWidget=None) -> None:
        super(ButtonsGRP, self).__init__(_parent)
        self.item_supplier = None
        self.setupUi()
        
    def setupUi(self) -> None:
        # self.filtering_btn = QPushButton("Filtering - pipe step")
        self.load_versions_btn = QPushButton("Load versions")
        self.clear_all_btn = QPushButton("Clear All")
        self.open_dir_btn = QPushButton("경로 열기")
        # self.check_sg_info = QPushButton("샷건 정보 확인")
        
        self.main_vl = QVBoxLayout()
        # self.main_vl.addWidget(self.filtering_btn)
        self.main_vl.addWidget(self.load_versions_btn)
        self.main_vl.addWidget(self.open_dir_btn)
        self.main_vl.addWidget(self.clear_all_btn)
        self.main_vl.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # self.main_vl.addWidget(self.)
        
        self.setLayout(self.main_vl)
        
        
        
    def set_supplier(self, _supplier :ItemSupplier) -> None:
        self.item_supplier = _supplier
        
    def get_supplier(self) -> ItemSupplier:
        return self.item_supplier
    
    def add_filtering_btn(self) -> None:
        self.filtering_btn.setVisible(True)
        
    def pop_filtering_btn(self) -> None:
        self.filtering_btn.setVisible(False)
        
class FilteringWidget(QWidget):
    _SELECTED_PIPE_STEP_ = Signal(str)
    def __init__(self, _parent :QWidget=None) -> None:
        super(FilteringWidget, self).__init__(_parent)
        self.item_supplier = None
        self.setupUi()
        
        self.MAX_COL_COUNT = 3
        
    def setupUi(self) -> None:
        self.main_gl = QGridLayout()
        self.setLayout(self.main_gl)
        
    def set_supplier(self, _supplier :ItemSupplier) -> None:
        self.item_supplier = _supplier
        
    def get_supplier(self) -> ItemSupplier:
        return self.item_supplier
    
    def add_radiobuttons(self, pipesteps :List[str]) -> None:
        cur_row = 0
        cur_col = 0
        for _pipe_step in pipesteps:
            _pipe_rb = QRadioButton()
            _pipe_rb.setText(_pipe_step)
            _pipe_rb.toggled.connect(partial(self.send_selected_pipestep, _pipe_step))
            self.main_gl.addWidget(_pipe_rb, cur_row, cur_col)
            
            if cur_col == (self.MAX_COL_COUNT-1):
                cur_row += 1
                cur_col = 0
            else:
                cur_col += 1
    
    def clear_all_radiobuttons(self) -> None:
        pass
    
    def send_selected_pipestep(self, _cur_pipestep :str, _status :bool) -> None:
        if _status == True:
            self._SELECTED_PIPE_STEP_.emit(_cur_pipestep)
        
class TargetCollectorWidget(QWidget):
    def __init__(self, _parent :QWidget=None) -> None:
        super(TargetCollectorWidget, self).__init__(_parent)
        self.item_supplier = None
        self.setupUi()
        
    def setupUi(self) -> None:
        
        self.collector_lw = QListWidget()
        
        self.main_vl = QVBoxLayout()
        self.main_vl.addWidget(self.collector_lw)
        
        self.setLayout(self.main_vl)
        
    def set_supplier(self, _supplier :ItemSupplier) -> None:
        self.item_supplier = _supplier
        
    def get_supplier(self) -> ItemSupplier:
        return self.item_supplier

    def set_target_shots(self, _items :List[QListWidgetItem]) -> None:
        _stopped = False
        for _item in _items:
            _shot_item = _item.data(Qt.UserRole)
            if _shot_item.version_exists() == False:
                _stopped = True
                continue
            _shot_name = _item.text()
            _seq_item = _shot_item.get_parent()
            _prj_item = _seq_item.get_parent()
            
            _task_items = self.get_supplier().get_tasks(_prj_item, _seq_item, _shot_item)
        
            widget_item = ShotItemWidget()
            widget_item.set_supplier(self.get_supplier())
            widget_item.set_name(_shot_name)
            widget_item.set_tasks(_task_items)
            
            list_item = QListWidgetItem(self.collector_lw)
            list_item.setData(Qt.UserRole, _shot_item)
            list_item.setSizeHint(widget_item.sizeHint())
            self.collector_lw.addItem(list_item)
            self.collector_lw.setItemWidget(list_item, widget_item)
        if _stopped == True:
            pass
                   
    def get_target_shots(self) -> List[ShotItemWidget]:
        tars = []
        for _idx in range(self.collector_lw.count()):
            shot_listwidgetitem = self.collector_lw.item(_idx)
            shot_item_wg = self.collector_lw.itemWidget(shot_listwidgetitem)
            tars.append(shot_item_wg)
        return tars
    
    def get_selected_shot(self) -> ShotItemWidget:
        selected_items = self.collector_lw.selectedItems()
        if selected_items:
            listwidgetitem = selected_items[0]
            return self.collector_lw.itemWidget(listwidgetitem)
        
    def get_selected_version(self) -> VersionItem:
        sel_tar = self.get_selected_shot()
        if sel_tar == None:
            return None
        return sel_tar.get_cur_version()
                
    def clear_shots(self) -> None:
        self.collector_lw.clear()
        
    def delete_custom_item(self):        
        items = self.collector_lw.selectedItems()
        if items:
            item = items[0]
            pop_widget = self.collector_lw.itemWidget(item)
            idx  = self.collector_lw.indexFromItem(item).row()
            pop_item = self.collector_lw.takeItem(idx)
            
    def is_empty(self) -> bool:
        if self.collector_lw.count() == 0:
            return True
        else:
            return False
    
    def get_union_of_pipestep(self) -> List[str]:
        step_union = []
        for _shot_item_wg in self.get_target_shots():
            _steps_of_shot = _shot_item_wg.get_all_steps()
            step_union.extend(_steps_of_shot)
        return list(set(step_union))
    
    def set_common_pipestep(self, common_step :str) -> None:
        for _shot_item_wg in self.get_target_shots():
            _shot_item_wg.set_current_step_by_filtering(common_step)
            
        
class EntityWidget(QWidget):
    def __init__(self, _parent=None) -> None:
        super(EntityWidget, self).__init__(_parent)
        self.item_supplier = None
        
        self.setupUi()
        
    def setupUi(self) -> None:
        self.prj_cb = QComboBox()
        self.seq_cb = QComboBox()
        self.shot_lw = QListWidget()
        self.shot_lw.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.main_vl = QVBoxLayout()
        self.main_vl.addWidget(self.prj_cb)
        self.main_vl.addWidget(self.seq_cb)
        self.main_vl.addWidget(self.shot_lw)
        
        self.setLayout(self.main_vl)
        
        self.prj_cb.currentIndexChanged.connect(self.set_seqs)
        self.seq_cb.currentIndexChanged.connect(self.set_shots)
        
    def set_projects(self, prj_items :List[ProjectItem]) -> None:
        for _item in prj_items:
            self.prj_cb.addItem(_item.get_name(), userData=_item)
        # self.prj_cb.model().sort(0, Qt.DescendingOrder)
        
    
    def get_cur_prj(self, _idx :int=-1) -> ProjectItem:
        if _idx == -1:
            return self.prj_cb.currentData(Qt.UserRole)
        else:
            return self.prj_cb.itemData(_idx, Qt.UserRole)
    
    def set_seqs(self, prj_idx :int) -> None:
        self.clear_seq()
        self.clear_shot()
        # self.clear_task()
        # self.clear_versions()
        
        prj_item = self.get_cur_prj(prj_idx)
        if prj_item == None:
            return None
        seq_items = self.get_supplier().get_seqs(prj_item)
        for _item in seq_items:
            self.seq_cb.addItem(_item.get_name(), userData=_item)
            
        self.seq_cb.model().sort(0, Qt.AscendingOrder)
        self.seq_cb.setCurrentIndex(0)
            
    def get_cur_seq(self, _idx :int=-1) -> SeqItem:
        if _idx == -1:
            cur_idx = self.seq_cb.currentIndex()
            return self.seq_cb.itemData(cur_idx, Qt.UserRole)
        else:
            return self.seq_cb.itemData(_idx, Qt.UserRole)
    
    def set_shots(self, seq_idx :int) -> None:
        def add_shot(_shot_lw :QListWidget, _item :ShotItem) -> None:
            list_item = QListWidgetItem(_item.get_name())
            list_item.setData(Qt.UserRole, _item)
            if _item.version_exists() == False:
                list_item.setTextColor(QColor(105, 105, 105))
            _shot_lw.addItem(list_item)
        
        self.clear_shot()

        prj_item = self.get_cur_prj()
        seq_item = self.get_cur_seq(seq_idx)
        if prj_item == None or seq_item == None:
            return None
        shot_items = self.get_supplier().get_shots(prj_item, seq_item)
        for _item in shot_items:
            add_shot(self.shot_lw, _item)
        
    def get_cur_shot(self) -> ShotItem:
        widget_item = self.entity_wg.get_shot_lw().currentItem()
        return widget_item.data(Qt.UserRole)
    
    def clear_seq(self) -> None:
        self.seq_cb.clear()
        
    def clear_shot(self) -> None:
        self.shot_lw.clear()
        
    def set_supplier(self, _supplier :ItemSupplier) -> None:
        self.item_supplier = _supplier
        
    def get_supplier(self) -> ItemSupplier:
        return self.item_supplier

    def get_selected_shots(self) -> List[QListWidgetItem]:
        return self.shot_lw.selectedItems()

class MainEngine(QMainWindow):
    def __init__(self, _parent :QWidget=None) -> None:
        super(MainEngine, self).__init__(_parent)
        self.item_supplier = ItemSupplier()
        self.signal_setter = SignalSetter()
        
        self.init_view()
        
        self.pop_filtering_ui()
        
    
    def init_view(self) -> None:
        self.entity_wg = EntityWidget(self)
        self.entity_wg.set_supplier(self.item_supplier)

        self.entity_tw = QTabWidget(self)
        self.entity_tw.setTabBarAutoHide(True)
        self.entity_tw.addTab(self.entity_wg, "Entity")
        
        self.stretch_item_01 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.to_left_btn = QPushButton(">")
        self.to_right_btn = QPushButton("<")
        self.to_left_btn.setFixedWidth(20)
        self.to_right_btn.setFixedWidth(20)
        self.to_right_btn.setToolTip("click \"Del\"")
        self.stretch_item_02 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.move_btn_vl = QVBoxLayout()
        self.move_btn_vl.addItem(self.stretch_item_01)
        self.move_btn_vl.addWidget(self.to_left_btn)
        self.move_btn_vl.addWidget(self.to_right_btn)
        self.move_btn_vl.addItem(self.stretch_item_02)
        
        self.collectors_wg = TargetCollectorWidget(self)
        self.collectors_wg.set_supplier(self.item_supplier)
        
        self.collector_tw = QTabWidget(self)
        self.collector_tw.setTabBarAutoHide(True)
        self.collector_tw.addTab(self.collectors_wg, "Targets")
        
        self.filtering_wg = FilteringWidget(self)
        self.filtering_wg.set_supplier(self.item_supplier)
        
        self.filtering_tw = QTabWidget(self)
        self.filtering_tw.setTabBarAutoHide(True)
        self.filtering_tw.addTab(self.filtering_wg, "Filtering")
        
        self.btns_wg = ButtonsGRP(self)
        self.btns_wg.set_supplier(self.item_supplier)
        
        self.btns_tw = QTabWidget(self)
        self.btns_tw.setTabBarAutoHide(True)
        self.btns_tw.addTab(self.btns_wg, "Utility")
        
        self.utility_vl = QVBoxLayout()
        self.utility_vl.addWidget(self.collector_tw)
        self.utility_vl.addWidget(self.filtering_tw)
        self.utility_vl.addWidget(self.btns_tw)
        self.utility_vl.setStretch(0, 8)
        self.utility_vl.setStretch(1, 1)
        self.utility_vl.setStretch(2, 2)
        
        self.body_hl = QHBoxLayout()
        self.body_hl.addWidget(self.entity_tw)
        self.body_hl.addLayout(self.move_btn_vl)
        self.body_hl.addLayout(self.utility_vl)
        self.body_hl.setStretch(0, 5)
        self.body_hl.setStretch(1, 1)
        self.body_hl.setStretch(2, 8)
        
        # self.main_vl = QVBoxLayout()
        # self.main_vl.addLayout(self.body_hl)
        
        self.main_wg = QWidget()
        self.main_wg.setLayout(self.body_hl)
        
        self.setCentralWidget(self.main_wg)
        self.setWindowTitle("Giantstep - Version Canvas")
        self.resize(600, 750)
        
        
        self.entity_wg.set_projects(self.item_supplier.get_projects())
        
        
        self.signal_setter.set_main_wg(self)
        self.signal_setter.set_entity_wg(self.entity_wg)
        self.signal_setter.set_collector_wg(self.collectors_wg)
        self.signal_setter.set_filtering_wg(self.filtering_wg)
        self.signal_setter.set_btns_wg(self.btns_wg)
        self.signal_setter.set_signals()
        
        
        
    def add_filtering_ui(self) -> None:
        self.filtering_tw.setVisible(True)
        
    def pop_filtering_ui(self) -> None:
        self.filtering_tw.setVisible(False)
        
        
        
        
        
    
            
    
        
    
        
    
        
        
        
    def add_source(self) -> None:
        _path = "/projects/2023_02_theAlien/sequence/BAT/BAT_0500/composite/cmp01/dev/images/jpg/v003/BAT_0500_cmp01_v003.mov"
        
        addSource(_path)
        