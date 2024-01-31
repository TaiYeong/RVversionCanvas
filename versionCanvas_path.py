from subprocess import Popen, PIPE
from tempfile import gettempdir
from pathlib import Path
import sys, os, re

def is_windows(platform=None):
    if platform:
        return platform == "win32"
    return sys.platform == "win32"

def is_linux(platform=None):
    if platform:
        return platform.startswith("linux")
    return sys.platform.startswith("linux")

def is_macos(platform=None):
    if platform:
        return platform == "darwin"
    return sys.platform == "darwin"

def check_dir(_path :str) -> None:
    dir_path = ""
    if re.search(r"\.\w+$", _path):
        dir_path = os.path.dirname(_path)
    else:
        dir_path = _path
    if os.path.exists(dir_path) == False:
        os.makedirs(dir_path)

def check_os(func) -> str:
    def wrapper_func(*args) -> str:
        _path = func(args)
        if is_windows() == True:
            convertor = PathConvertorToWin()
            win_path = convertor.do_convert(_path)
            return win_path
        else:
            return _path
    return wrapper_func

def check_os_func(func) -> str:
    def wrapper_func(*args) -> str:
        _path = func(*args)
        if is_windows() == True:
            convertor = PathConvertorToWin()
            win_path = convertor.do_convert(_path)
            return win_path
        else:
            return _path
        
    return wrapper_func
    
def path_separator_adjustment(func) -> str:
    def wrapper_func(_path :str) -> str:
        to_path = func(_path)
        if is_windows() == True:
            if "/" in to_path:
                return to_path.replace("/", "\\")
            else:
                return to_path
        else:
            return to_path
    return wrapper_func



class PathConvertor():
    win_x           = "\\\\vfx.gtserver04.net\\gstepvfx\\projects"
    win_z           = "\\\\vfx.gtserver04.net\\usersetup"
    win_asset       = "\\\\vfx.gtserver04.net\\gstepasset"
    win_x_alphabet  = "X:\\projects"
    win_z_alphabet  = "Z:\\"
    lnx_x           = "/projects"
    lnx_z           = "/usersetup"
    lnx_asset       = "/gstepasset"
    def do_convert(self, from_path :str) -> str:
        raise NotImplementedError
    
class PathConvertorToWin(PathConvertor):
    def do_convert(self, from_path: str) -> str:
        if from_path.startswith(self.lnx_x):
            win_path = from_path.replace(self.lnx_x, self.win_x)
            win_path = win_path.replace("/", "\\")
            return win_path
        elif from_path.startswith(self.lnx_z):
            win_path = from_path.replace(self.lnx_z, self.win_z)
            win_path = win_path.replace("/", "\\")
            return win_path
        elif from_path.startswith(self.lnx_asset):
            win_path = from_path.replace(self.lnx_asset, self.win_asset)
            win_path = win_path.replace("/", "\\")
            return win_path
        else:
            return from_path.replace("/", "\\")
        
class PathConvertorToLnx(PathConvertor):
    def do_convert(self, from_path: str) -> str:
        if from_path.startswith(self.win_x):
            lnx_path = from_path.replace(self.win_x, self.lnx_x)
            lnx_path = lnx_path.replace("\\", "/")
            return lnx_path
        elif from_path.startswith(self.win_z):
            lnx_path = from_path.replace(self.win_z, self.lnx_z)
            lnx_path = lnx_path.replace("\\", "/")
            return lnx_path
        elif from_path.startswith(self.win_x_alphabet):
            lnx_path = from_path.replace(self.win_x_alphabet, self.lnx_x)
            lnx_path = lnx_path.replace("\\", "/")
            return lnx_path
        elif from_path.startswith(self.win_z_alphabet):
            lnx_path = from_path.replace(self.win_z_alphabet, self.lnx_z)
            lnx_path = lnx_path.replace("\\", "/")
            return lnx_path
        elif from_path.startswith(self.win_asset):
            lnx_path = from_path.replace(self.win_asset, self.lnx_asset)
            lnx_path = lnx_path.replace("\\", "/")
            return lnx_path
        else:
            return from_path.replace("\\", "/")
        
class ResourcesPathConvertor(PathConvertor):
    WIN_ICON_POSTFIX = ""
    
    def do_convert(self, from_path: str) -> str:
        if is_linux():
            return f"{self.lnx_z}/{from_path}"
        elif is_windows():
            to_path = f"{self.win_z}/{from_path}"
            return to_path.replace("/", "\\")
    
    def get_win_icon(self) -> str:
        return self.do_convert(self.WIN_ICON_POSTFIX)
    
    

class PathSupplier():
    @staticmethod
    def path_formatting(format_str :str, format_info :dict) -> str:
        _path = format_str.format(**format_info)
        if is_windows() == True:
            convertor = PathConvertorToWin()
            win_path = convertor.do_convert(_path)
            return win_path
        else:
            return _path 
        
    @staticmethod
    def listdir_with_sort(_dir :str, _reverse :bool=True) -> list:
        if os.path.exists(_dir) == False:
            return []
        tars = os.listdir(_dir)
        tars.sort(reverse=_reverse)
        return tars
    
    @staticmethod
    def find_exact_format(_dir :str, _find_tar :str) -> list:
        find_res = []
        for _tar in os.listdir(_dir):
            if _tar.endswith(_find_tar):
                find_res.append(os.path.join(_dir, _tar))
        return find_res

class OSPathSupplier(PathSupplier):
    '''
    This class for providing path invovling 'home' / 'temp' directory
    '''
    @classmethod
    def get_temp_dir(cls) -> str:
        return gettempdir()
    @classmethod
    def get_home_dir(cls) -> str:
        return str(Path.home())
    @classmethod
    def get_pref_path(cls) -> str:
        _path = cls.get_home_dir() + "/" + "PlayerCanvas" + "/" + "pref.yaml"
        check_dir(_path)
        return _path
    



class CmdOperator():
    @classmethod
    def run_cmd(cls, *argv) -> None:
        proc = Popen(*argv, stdout = PIPE)
        out, err = proc.communicate()
    @classmethod    
    def open_folder(cls, _path :str) -> None:
        raise NotImplementedError
    
class WinCmdOperator(CmdOperator):
    @classmethod
    def open_folder(cls, _path :str) -> None:
        cls.run_cmd(["explorer.exe", _path])

class LnxCmdOperator(CmdOperator):
    @classmethod
    def open_folder(cls, _path :str) -> None:
        cls.run_cmd(["nautilus", _path])
        
        
if __name__ == "__main__":
    
    # res = OSPathSupplier.path_formatting("/{root}/aaa/{seq}", {"root":"usersetup", "seq":"bbb"})
    # print(res)
    
    LnxCmdOperator().open_folder()