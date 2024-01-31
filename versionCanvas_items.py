from os.path import basename, dirname
from re import search
from versionCanvas_toolkit import get_filepath_from_sourceGroup, get_vernum_from_path

class Item():
    name    :str    =""
    parent          =None
    def __init__(self, _name :str, _parent=None) -> None:
        self.name   = _name
        self.parent = _parent
        
    def get_name(self) -> str:
        return self.name
    
    def get_parent(self) -> str:
        return self.parent
    
    
class ProjectItem(Item):
    def __init__(self, _name: str, _parent: Item=None) -> None:
        super().__init__(_name, _parent)
        
class SeqItem(Item):
    def __init__(self, _name: str, _parent: Item=None) -> None:
        super().__init__(_name, _parent)
        
class ShotItem(Item):
    def __init__(self, _name: str, _parent: Item=None, does_ver_exists=True) -> None:
        super().__init__(_name, _parent)
        self.ver_exists = does_ver_exists
        
    def version_exists(self) -> bool:
        return self.ver_exists
    
    def set_exists(self, _status :bool) -> None:
        self.ver_exists = _status
        
class TaskItem(Item):
    step    :str    = ""
    task    :str    = ""
    def __init__(self, _name: str, _parent: Item=None, _step_name: str="", _task_name: str="") -> None:
        super().__init__(_name, _parent)
        self.step = _step_name
        self.task = _task_name
        
    def get_step_name(self) -> str:
        return self.step
    
    def get_task_name(self) -> str:
        return self.task
        
class VersionItem(Item):
    def __init__(self, _name: str, _parent: Item=None, _full_path: str="", _vernum: str="v001") -> None:
        super().__init__(_name, _parent)
        self.dir        :str=dirname(_full_path)
        self.fname      :str=basename(_full_path)
        self.full_path  :str=_full_path
        self.ver_type   :str=""
        self.vernum     :str=_vernum
        
    def get_dirname(self) -> str:
        return self.dir
    
    def get_basename(self) -> str:
        return self.fname
    
    def get_ver_type(self) -> str:
        return self.ver_type
    
    def get_vernum(self) -> str:
        return self.vernum
    
    def get_fullpath(self) -> str:
        return self.full_path
    
    def set_ver_type(self) -> None:
        if search(r"\/jpg\/", self.get_dirname()):
            self.ver_type = "jpg"
        elif search(r"\/mov\/", self.get_dirname()):
            self.ver_type = "mov"
    
class RVSourceItem():
    def __init__(self, _name :str, _idx :int) -> None:
        self.idx        :int=_idx
        self.name       :str=_name
        self.fullpath   :str=""
        self.vernum     :str=""
        
        self.set_fullpath()
        self.set_vernum()
        
        
    def set_fullpath(self) -> None:
        self.fullpath = get_filepath_from_sourceGroup(self.name)
    
    def get_fulllpath(self) -> str:
        return self.fullpath    
    
    def set_vernum(self) -> None:
        self.vernum = get_vernum_from_path(self.get_fulllpath())
        
    def get_vernum(self) -> str:
        return self.vernum
    
    def get_name(self) -> str:
        return self.name
    
    def get_index(self) -> int:
        return self.idx