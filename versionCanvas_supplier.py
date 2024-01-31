from __future__ import annotations
from typing import TYPE_CHECKING, List
from versionCanvas_items import (
                                    Item, ProjectItem, SeqItem, ShotItem,
                                    TaskItem, VersionItem, RVSourceItem
                                )
from versionCanvas_path import PathSupplier, check_os
from versionCanvas_toolkit import (get_RVSwitch_from_groupNode, get_current_source_of_switch,
                                   is_lastest_version, is_oldest_version)
import os, re

# if TYPE_CHECKING:
#     from ..views.MainView import MainView
#     from .preference import DirectoryPreference
class ExceptPreference():
    except_prj_list = ["2100_fxAsset", "2100_01_fxAsset"]
    @classmethod
    def project_list(cls) -> list:
        return cls.except_prj_list
    
class DirectoryPreference():
    default_val ={
                        "ROOT"                   : "/projects",
                        "SEQ"                    : "/projects/{PROJECT}/sequence/", 
                        "SHOT"                   : "/projects/{PROJECT}/sequence/{SEQ}/",
                        "STEP"                   : "/projects/{PROJECT}/sequence/{SEQ}/{SHOT}/",
                        "TASK"                   : "/projects/{PROJECT}/sequence/{SEQ}/{SHOT}/{STEP}/",
                        "VERSION_JPG"            : "/projects/{PROJECT}/sequence/{SEQ}/{SHOT}/{STEP}/{TASK}/dev/images/jpg",
                        "VERSION_MOV"            : "/projects/{PROJECT}/sequence/{SEQ}/{SHOT}/{STEP}/{TASK}/dev/images/mov",
                        "PLAYER_TYPE"            : "/opt/rv-centos7-x86-64-2022.3.1/bin/rv"
                    }
                    
    
    # def set_at_once(self, pref_name :str, pref_val :object) -> None:
    #     if pref_name == "ROOT":
    #         self.set_root_pref(pref_val)
    #     elif pref_name == "SEQ":
    #         self.set_seq_pref(pref_val)
    #     elif pref_name == "SHOT":
    #         self.set_shot_pref(pref_val)
    #     elif pref_name == "STEP":
    #         self.set_step_pref(pref_val)
    #     elif pref_name == "TASK":
    #         self.set_task_pref(pref_val)
    #     elif pref_name == "PLAYER_TYPE":
    #         self.set_player_pref(pref_val)
    @classmethod
    @check_os
    def get_root_pref(cls) -> str:
        return DirectoryPreference.default_val.get("ROOT")
    @classmethod
    def set_root_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["ROOT"] = _path
    @classmethod
    @check_os    
    def get_seq_pref(cls) -> str:
        return DirectoryPreference.default_val.get("SEQ")
    @classmethod
    def set_seq_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["SEQ"] = _path
    @classmethod
    @check_os
    def get_shot_pref(cls) -> str:
        return DirectoryPreference.default_val.get("SHOT")
    @classmethod
    def set_shot_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["SHOT"] = _path
    @classmethod
    @check_os
    def get_step_pref(cls) -> str:
        return DirectoryPreference.default_val.get("STEP")
    @classmethod
    def set_step_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["STEP"] = _path
    @classmethod
    @check_os    
    def get_task_pref(cls) -> str:
        return DirectoryPreference.default_val.get("TASK")
    @classmethod
    def set_task_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["TASK"] = _path
    @classmethod
    @check_os    
    def get_jpg_ver_pref(cls) -> str:
        return DirectoryPreference.default_val.get("VERSION_JPG")
    @classmethod
    def set_jpg_ver_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["VERSION_JPG"] = _path
    @classmethod
    @check_os    
    def get_mov_ver_pref(cls) -> str:
        return DirectoryPreference.default_val.get("VERSION_MOV")
    @classmethod
    def set_mov_ver_pref(cls, _path :str) -> None:
        DirectoryPreference.default_val["VERSION_MOV"] = _path
    @classmethod
    def get_player_pref(cls) -> str:
        return DirectoryPreference.default_val.get("PLAYER_TYPE")
    

class ItemSupplier():
    
    def iterate_parents(self, _item :Item) -> List[Item]:
        if _item == None:
            return []
        else:
            return [_item] + self.iterate_parents(_item.get_parent())
        
    
    # @Initializer.init_template_module
    def get_projects(self) -> List[ProjectItem]:
        prj_item_list   = []
        prefix_path = PathSupplier.path_formatting(DirectoryPreference().get_root_pref(), {})
        if os.path.exists(prefix_path) == False:
            return []
        prj_str_list    = PathSupplier.listdir_with_sort(prefix_path)
        for prj_name in prj_str_list:
            if not re.search(r"^\d+\_\d+\_\w+", prj_name):
                continue
            if prj_name in ExceptPreference.project_list():
                continue
            prj_item_list.append(ProjectItem(prj_name))
        return prj_item_list
    
    # @Initializer.init_template_module
    def get_seqs(self, prj_item :ProjectItem) -> List[SeqItem]:
        seq_item_list   = []
        prefix_path     = PathSupplier.path_formatting(DirectoryPreference().get_seq_pref(), {"PROJECT":prj_item.get_name()})
        if os.path.exists(prefix_path) == False:
            return []
        seq_str_list    = PathSupplier.listdir_with_sort(prefix_path)
        for seq_name in seq_str_list:
            if not re.search(r"^\w{3}", seq_name):
                continue
            seq_item_list.append(SeqItem(seq_name, _parent=prj_item))
        return seq_item_list
    
    # @Initializer.init_template_module
    def get_shots(self, prj_item :ProjectItem, seq_item :SeqItem) -> List[ShotItem]:
        shot_item_list  = []
        prefix_path     = PathSupplier.path_formatting(DirectoryPreference().get_shot_pref(), {"PROJECT":prj_item.get_name(), "SEQ":seq_item.get_name()})
        if os.path.exists(prefix_path) == False:
            return []
        shot_str_list   = PathSupplier.listdir_with_sort(prefix_path, False)
        for shot_name in shot_str_list:
            if not re.search(r"^\w+\_\d{4}", shot_name):
                continue
            _shot_item = ShotItem(shot_name, _parent=seq_item)
            search_res = self.get_tasks(prj_item, seq_item, _shot_item)
            if search_res == [] or search_res == None:
                _shot_item.set_exists(False)
            shot_item_list.append(_shot_item)
        return shot_item_list
    
    # @Initializer.init_template_module
    def get_tasks(self, prj_item :ProjectItem, seq_item :SeqItem, shot_item :ShotItem) -> List[TaskItem]:
        
        task_item_list  = []
        prefix_path     = PathSupplier.path_formatting(DirectoryPreference().get_step_pref(),
                                                       {"PROJECT":prj_item.get_name(), "SEQ":seq_item.get_name(), "SHOT":shot_item.get_name()})
        if os.path.exists(prefix_path) == False:
            return
        
        step_list       = PathSupplier.listdir_with_sort(prefix_path)
        for _step in step_list:
            if os.path.isfile(os.path.join(prefix_path, _step)) == True:
                continue
            task_prefix = PathSupplier.path_formatting(DirectoryPreference().get_task_pref(),
                                                       {"PROJECT":prj_item.get_name(), "SEQ":seq_item.get_name(), "SHOT":shot_item.get_name(), "STEP":_step})
            if os.path.exists(task_prefix) == False:
                continue
            task_list   = PathSupplier.listdir_with_sort(task_prefix)
            for _task in task_list:
                _item_name = f"{_step}-{_task}"
                _task_item = TaskItem(_item_name, shot_item, _step, _task)
                search_res = self.get_versions(prj_item, seq_item, shot_item, _task_item)
                if search_res == [] or search_res == None:
                    continue
                task_item_list.append(_task_item)
        return task_item_list
    
    def get_versions(self, prj_item :ProjectItem, seq_item :SeqItem, shot_item :ShotItem, task_item :TaskItem) -> List[VersionItem]:
        def find_exact_versions(prefix_path :str, _parent :TaskItem) -> List[VersionItem]:
            version_item_list = []
            vernum_list       = PathSupplier.listdir_with_sort(prefix_path)
            for _vernum in vernum_list:
                tar_path = os.path.join(prefix_path, _vernum)
                if os.path.isdir(tar_path):
                    find_res = PathSupplier.find_exact_format(os.path.join(prefix_path, _vernum), ".mov")
                    if find_res == []:
                        continue
                    version_item_list.append(VersionItem(_vernum, _parent, find_res[0], _vernum))
                elif os.path.isfile(tar_path) == True and tar_path.endswith(".mov"):
                    search_res = re.search(r"\_v\d+\w+\.mov$", tar_path)
                    if search_res:
                        vernum_from_fname = ((search_res.group()).replace("_", "")).replace(".mov", "")
                        version_item_list.append(VersionItem(vernum_from_fname, _parent, tar_path, vernum_from_fname))
            return version_item_list
        
        
        if task_item.get_step_name().lower() in ["animation", "matchmove", "cloth", "hair"]:
            mov_prefix_path = PathSupplier.path_formatting(DirectoryPreference().get_mov_ver_pref(),
                                                    {"PROJECT":prj_item.get_name(), "SEQ":seq_item.get_name(), "SHOT":shot_item.get_name(),
                                                     "STEP":task_item.get_step_name(), "TASK":task_item.get_task_name()})
            if os.path.exists(mov_prefix_path) == False:
                return []
            mov_res = find_exact_versions(mov_prefix_path, task_item)
            if mov_res != []:
                return mov_res
            
        else:
            jpg_prefix_path = PathSupplier.path_formatting(DirectoryPreference().get_jpg_ver_pref(),
                                                    {"PROJECT":prj_item.get_name(), "SEQ":seq_item.get_name(), "SHOT":shot_item.get_name(),
                                                     "STEP":task_item.get_step_name(), "TASK":task_item.get_task_name()})
            if os.path.exists(jpg_prefix_path) == False:
                return []
        
            jpg_res = find_exact_versions(jpg_prefix_path, task_item)
            if jpg_res != []:
                return jpg_res
        
        
        
class RVSourceSupplier():
    def __init__(self, _switch_grp_node :str, _source_groups :List[str]):
        self.cur_switch         :str=_switch_grp_node
        self.switch_node        :str=get_RVSwitch_from_groupNode(_switch_grp_node)
        self.rv_src_group_list  :List[str]=_source_groups
        self.rv_items           :List[RVSourceItem]=[]
        self.cur_idx            :int=0
        
        self.convert_to_RVSourceItem()
        self.find_index_from_sourcename()
    
    # ====================================================================
    #                       Get and Set Methods
    # ====================================================================
    def get_current_index(self) -> int:
        return self.cur_idx
    def set_curent_index(self, _idx :int) -> None:
        self.cur_idx = _idx
    
    def get_current_switchgrp(self) -> str:
        return self.cur_switch
    
    def get_RVSourceItems(self) -> List[RVSourceItem]:
        return self.rv_items
    
    def get_current_RVSourceItem(self) -> RVSourceItem:
        return self.rv_items[self.get_current_index()]
    
    def get_source_groups(self) -> List[str]:
        return self.rv_src_group_list
    # ====================================================================
    #                       Utility Methods
    # ====================================================================
    def convert_to_RVSourceItem(self) -> None:
        for _idx, _src_group in enumerate(self.rv_src_group_list):
            _item = RVSourceItem(_src_group, _idx)
            self.rv_items.append(_item)
            
    def find_index_from_sourcename(self, src_name :str="") -> int:
        if src_name == "":
           src_name = get_current_source_of_switch(self.get_current_switchgrp()) 
        for _idx, _item in enumerate(self.get_RVSourceItems()):
            if _item.get_name() == src_name:
                self.set_curent_index(_idx)
                break
    
    def need_to_add_new_upper_source(self) -> bool:
        if is_lastest_version(self.get_current_RVSourceItem().get_fulllpath()) == True:
            return False
        if self.get_current_index() <= 0 or self.get_current_index() >= len(self.get_RVSourceItems()):
            return True
        else:
            return False
        
    def need_to_add_new_lower_source(self) -> bool:
        if is_oldest_version(self.get_current_RVSourceItem().get_fulllpath()) == True:
            return False
        if self.get_current_index() < 0 or self.get_current_index() >= (len(self.get_RVSourceItems())-1):
            return True
        else:
            return False
        
    def get_down_version_sourceItem(self) -> RVSourceItem:
        if self.get_current_index() == len(self.get_RVSourceItems())-1:
            _idx = len(self.get_RVSourceItems())-1
        else:
            _idx = self.get_current_index() + 1
        return self.rv_items[_idx]
    
    def get_up_version_sourceItem(self) -> RVSourceItem:
        if self.get_current_index() == 0:
            _idx = 0
        else:
            _idx = self.get_current_index() - 1
        return self.rv_items[_idx]
        
        
            
if __name__ == "__main__":
    res = DirectoryPreference().get_root_pref()
    print(res)
    
    supplier = ItemSupplier()
    results = supplier.get_projects()
    for i in results:
        print(i.get_name())