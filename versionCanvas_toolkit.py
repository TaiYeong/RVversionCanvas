
from rv import commands, extra_commands
from re import search, sub
from os.path import basename, exists, dirname, join, realpath
from os import listdir
from glob import glob
from versionCanvas_path import check_os_func, path_separator_adjustment, is_windows


def set_view_root() -> None:
    commands.setViewNode("defaultSequence")

def group_member_of_type(node, member_type):
    for n in commands.nodesInGroup(node):
        if commands.nodeType(n) == member_type:
            return n
    return None

def get_vernum_from_path(tar_path :str) -> str:
    search_res = search(r"v\d{3}", tar_path)
    if search_res:
        return search_res.group()
    else:
        return ""
    
def get_switch_name_from_path(_fullpath :str) -> str:
    fname = basename(_fullpath)
    name_elements = fname.split("_")
    if len(name_elements) < 3:
        return "_".join(name_elements[0:2])
    else:
        return "_".join(name_elements[0:3])

def create_switch_node(to_name :str="") -> str:
    created_node = commands.newNode("RVSwitchGroup")
    if to_name != "":
        change_node_name(created_node, to_name)
    return created_node

def clear_inputs_of_defaultseq() -> None:
    commands.setNodeInputs("defaultSequence", [])
    commands.setNodeInputs("defaultLayout", [])
    commands.setNodeInputs("defaultStack", [])

def clear_outputs_of_tarnode(tar_node :str) -> None:
    _inputs, _outputs = commands.nodeConnections(tar_node)

    if _outputs == []:
        return
    for _out in _outputs:
        _out_ins, _out_outs = commands.nodeConnections(_out)
        _out_ins.remove(tar_node)
        commands.setNodeInputs(_out, _out_ins)
        
def clear_nodes_except_tarType(tar_node_type :str) -> None:
    new_inputs = []
    _inputs, _outputs = commands.nodeConnections("defaultSequence")
    for _node in _inputs:
        if commands.nodeType(_node) == tar_node_type:
            new_inputs.append(_node)
    commands.setNodeInputs("defaultSequence", new_inputs)
    
def change_node_name(tar_node :str, to_name :str) -> str:
    commands.setStringProperty(f"{tar_node}.ui.name", [to_name])
    return tar_node
    
def add_new_source(_path :str, _new_switch_name :str="",_root_pos :str="after") -> None:
    root_inputs, root_outputs = commands.nodeConnections("defaultSequence")
    
    source_node               = commands.addSourceVerbose([_path])
    clear_inputs_of_defaultseq()
    source_grp_node           = commands.nodeGroup(source_node)
    
    new_switch_node           = create_switch_node(to_name=_new_switch_name)
    
    commands.setNodeInputs(new_switch_node, [source_grp_node])
    cur_rvSwitch = get_RVSwitch_from_groupNode(new_switch_node)
    commands.setStringProperty(f"{cur_rvSwitch}.output.input", [source_grp_node])
    
    if _root_pos == "after":
        root_inputs.append(new_switch_node)
    else:
        root_inputs.insert(0, new_switch_node)
    set_default_seq_inputs(root_inputs)
    
def check_and_get_exists_sourcegrp(check_path :str):
    if is_windows() == True:
        check_path = check_path.replace("\\", "/")
    
    _nodes = commands.viewNodes()
    for _node in _nodes:
        if commands.nodeType(_node) == "RVSourceGroup":
            source = group_member_of_type(_node, "RVFileSource")
            prop_prefix = source+'.media.movie'
            if commands.propertyExists(prop_prefix):
                file_name = commands.getStringProperty(prop_prefix)[0]
                # print(111111, check_path , file_name)
                # print(2222222, check_path == file_name)
                # print(3333333, realpath(check_path), realpath(file_name))
                # print(555555, realpath(check_path)== realpath(file_name))
                if check_path == file_name:
                    return True, _node

    return False, ""                
    
def add_source_to_switch(_path :str, _tar_switch_node :str, _pos :str="after") -> None:
    root_inputs, root_outputs = commands.nodeConnections("defaultSequence")
    
    _exists, _src_grp         = check_and_get_exists_sourcegrp(_path)
    if _exists == True:
        source_grp_node = _src_grp
    else:
        source_node               = commands.addSourceVerbose([_path])
        clear_inputs_of_defaultseq()
        source_grp_node           = commands.nodeGroup(source_node)
    
    inputs, outputs           = commands.nodeConnections(_tar_switch_node)
    if _pos == "prev":
        inputs.insert(0, source_grp_node)
    else:
        inputs.append(source_grp_node)
    
    commands.setNodeInputs(_tar_switch_node, inputs)
    cur_rvSwitch = get_RVSwitch_from_groupNode(_tar_switch_node)
    commands.setStringProperty(f"{cur_rvSwitch}.output.input", [source_grp_node])
    
    set_default_seq_inputs(root_inputs)
    
def connect_source_to_switch(from_source :str, to_switch :str) -> None:
    # root_inputs, root_outputs = commands.nodeConnections("defaultSequence")
            
    inputs, outputs           = commands.nodeConnections(to_switch)
    inputs.append(from_source)
    commands.setNodeInputs(to_switch, inputs)
    cur_rvSwitch = get_RVSwitch_from_groupNode(to_switch)
    commands.setStringProperty(f"{cur_rvSwitch}.output.input", [from_source])
    
    # set_default_seq_inputs(root_inputs)
    
def connect_node_to_node(from_node :str, to_node :str) -> None:
    _inputs, _outputs = commands.nodeConnections(to_node)
    _inputs.append(from_node)
    commands.setNodeInputs(to_node, _inputs)
    
def set_default_seq_inputs(switch_nodes :list) -> None:
    commands.setNodeInputs("defaultSequence", switch_nodes)
    
def get_source_node_from_curframe() -> str:
    source_of_frame = commands.sourcesAtFrame(commands.frame())
    grp_node        = commands.nodeGroup(source_of_frame[0])
    return grp_node
    
def get_switch_node_from_curframe() -> str:
    tar_switch      = ""
    grp_node        = get_source_node_from_curframe()
    inputs, outputs = commands.nodeConnections(grp_node)
    
    for o in outputs:
        if commands.nodeType(o) == "RVSwitchGroup":
            tar_switch = o
            break
    return tar_switch

def get_sources_from_switch(tar_switch :str) -> list:
    source_list         = []
    cur_switch          = get_switch_node_from_curframe()
    _inputs, _outputs   = commands.nodeConnections(cur_switch)
    for _idx, _i in enumerate(_inputs):
        if commands.nodeType(_i) == "RVSourceGroup":
            source_list.append(_i)
    return source_list
    
def get_filepath_from_curframe() -> str:
    source_of_frame = commands.sourcesAtFrame(commands.frame())
    info            = commands.sourceMediaInfo(source_of_frame[0])
    return info["file"]

@check_os_func
def get_filepath_from_sourceGroup(rv_source_group :str) -> None:
    source_attrs = commands.sourceAttributes(rv_source_group)
    if source_attrs == None:
        rv_file_node = commands.closestNodesOfType("RVFileSource", rv_source_group)[0]
        info         = commands.sourceMediaInfo(rv_file_node)
        return info["file"]
    else:
        return dict(source_attrs)["File"]
    
@check_os_func
def get_filepath_from_fileSource(rv_file_source :str) -> None:
    info         = commands.sourceMediaInfo(rv_file_source)
    return info["file"]
    
    
def get_next_ver_path_with_repalcing(cur_path :str) -> str:
    def up_ver(cur_ver :str) -> str:
        temp = cur_ver.replace("v", "")
        next_ver = str(int(temp) + 1)
        return "v" + next_ver.zfill(3)
    search_res = search(r"v\d{3}", cur_path)
    if search_res:
        cur_ver = search_res[0]
        next_ver = up_ver(cur_ver)
        next_ver_path = cur_path.replace(cur_ver, next_ver)
        if exists(next_ver_path) == False:
            extra_commands.displayFeedback(f"Not Exists : {next_ver_path}", 3.0)
            return None
        return next_ver_path
    else:
        return None
    
def get_prev_ver_path_with_repalcing(cur_path :str) -> str:
    def down_ver(cur_ver :str) -> str:
        temp = cur_ver.replace("v", "")
        if int(temp) == 0:
            return "v001"
        next_ver = str(int(temp) - 1)
        return "v" + next_ver.zfill(3)
    search_res = search(r"v\d{3}", cur_path)
    if search_res:
        cur_ver = search_res[0]
        prev_ver = down_ver(cur_ver)
        prev_ver_path = cur_path.replace(cur_ver, prev_ver)
        if exists(prev_ver_path) == False:
            extra_commands.displayFeedback(f"Not Exists : {prev_ver_path}", 3.0)
            return None
        return prev_ver_path
    else:
        return None


def is_lastest_version(cur_path :str) -> bool:
    if up_func(cur_path) == cur_path:
        return True
    else:
        return False
    
def is_oldest_version(cur_path :str) -> bool:
    if down_func(cur_path) == cur_path:
        return True
    else:
        return False
    
        

@path_separator_adjustment
def up_func(cur_path :str) -> None:
    def is_jpg_of_images(_path :str) -> bool:
        if "/images/jpg" in _path or "\\images\\jpg" in _path:
            return True
        else:
            return False
    try:
        dir_path = dirname(cur_path)
        base_name = basename(cur_path)
        if is_jpg_of_images(cur_path) == True:
            if is_windows() == True:
                modf = sub(r'\\v[0-9]+', '\*', dir_path)
            else:
                modf = sub(r'\/v[0-9]+', '/*', dir_path)
            current_ver_dir_list = sorted(glob(join(dir_path, modf)))
            cur_idx = current_ver_dir_list.index(dir_path)
            res = current_ver_dir_list[cur_idx+1]

            
            return glob(res + "/*.mov")[0]
            
        else:
            modf = sub(r'[0-9]+', '*', base_name)
            current_mov_list = sorted(glob(join(dir_path, modf)))
            cur_idx = current_mov_list.index(cur_path)
            # if cur_idx+1 >= len(current_mov_list):
            #     res = current_mov_list[cur_idx]
            # else:
            #     res = current_mov_list[cur_idx+1]
            res = current_mov_list[cur_idx+1]
            return res
    except:
        return cur_path

@path_separator_adjustment 
def down_func(cur_path :str) -> None:
    def is_jpg_of_images(_path :str) -> bool:
        if "/images/jpg" in _path or "\\images\\jpg" in _path:
            return True
        else:
            return False
    try:
        dir_path = dirname(cur_path)
        base_name = basename(cur_path)
        if is_jpg_of_images(cur_path) == True:
            if is_windows() == True:
                modf = sub(r'\\v[0-9]+', '\*', dir_path)
            else:
                modf = sub(r'\/v[0-9]+', '/*', dir_path)
            current_ver_dir_list = sorted(glob(join(dir_path, modf)))
            
            cur_idx = current_ver_dir_list.index(dir_path)
            if cur_idx-1 < 0:
                next_idx = 0
            else:
                next_idx = cur_idx-1
            res = current_ver_dir_list[next_idx]
            
            return glob(res + "/*.mov")[0]
        else:
            modf = sub(r'[0-9]+', '*', base_name)
            current_mov_list = sorted(glob(join(dir_path, modf)))
            cur_idx = current_mov_list.index(cur_path)
            if cur_idx-1 < 0:
                next_idx = 0
            else:
                next_idx = cur_idx-1
            res = current_mov_list[next_idx]
        
            return res
    except Exception as e:
        return cur_path
        




def get_RVSwitch_from_groupNode(tar_switch :str) -> str:
    search_res = commands.closestNodesOfType("RVSwitch", tar_switch)
    if search_res:
        return search_res[0]
    else:
        return ""
    
def get_current_source_of_switch(switch_grp_node :str) -> str:
    switch_node = get_RVSwitch_from_groupNode(switch_grp_node)
    return commands.getStringProperty(f"{switch_node}.output.input")[0]

def set_current_source_of_switch(switch_grp_node :str, src_grp :str) -> None:
    switch_node = get_RVSwitch_from_groupNode(switch_grp_node)
    return commands.setStringProperty(f"{switch_node}.output.input", [src_grp])

    
    
if __name__== "__main__":
    _path_other = '/projects/2023_02_theAlien/sequence/SRH/SRH_0020/lighting/lgt01/dev/images/jpg/v010/SRH_0020_lgt01_v010.mov'
    _path_v009 = '/projects/2023_02_theAlien/sequence/SRH/SRH_0030/lighting/lgt01/dev/images/jpg/v009/SRH_0030_lgt01_v009.mov'
    _path_v008 = '/projects/2023_02_theAlien/sequence/SRH/SRH_0030/lighting/lgt01/dev/images/jpg/v008/SRH_0030_lgt01_v008.mov'
    _path_v001 = '/projects/2023_02_theAlien/sequence/SRH/SRH_0030/lighting/lgt01/dev/images/jpg/v001/SRH_0030_lgt01_v001.mov'

    get_vernum_from_path(_path_other)


    # add_new_source(_path_other)
    # add_new_source(_path_v009)

    # #set_default_seq_inputs([other_switch_node, v009_switch_node])

    # commands.setViewNode("defaultSequence")


    # cur_switch = get_switch_node_from_curframe()
    # print(cur_switch)
    # print(commands.nodeType(cur_switch))

    # add_source_to_switch(_path_v008, cur_switch) 

    # cur_file = get_filepath_from_curframe()
    # print(cur_file)
    # v010 = get_next_ver_path(cur_file)

    # add_source_to_switch(_path_v001, cur_switch)




    # cur_grp = get_source_node_from_curframe()
    # print(cur_grp)


    # tar = "switchGroup000002_switch"
    # from pprint import pprint
    # pprint(commands.properties(tar))


    # commands.setStringProperty("switchGroup000002_switch.output.input", ["sourceGroup000001"])


