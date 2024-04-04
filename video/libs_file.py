import os
import shutil

"""转移文件
@param file_path 文件路径
@param target_dir 目标文件夹
@param target_name 目标文件名
@param delete 是否删除源文件
@return 是否转移成功 True: 成功  False: 失败
"""
def transfer_file(file_path, target_dir, target_name:str = None, delete:bool = True)->bool:
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if not target_name:
            target_name = os.path.basename(file_path)
        target_path = os.path.join(target_dir, target_name)
        print("转移文件: %s  to %s" % (file_path, target_path))
        if not delete:
            shutil.copy(file_path, target_path)
        else:
            shutil.move(file_path, target_path)
        return True
    except Exception as e:
        print(e)
        return False


"""过滤文件
@param file_path 文件路径
@param filter 文件过滤 [path1, path2]
@return 是否符合  True: 符合[filter]条件  False: 不符合[filter]条件
"""
def filter_file(file_path,filter:list[str] = None) -> bool:
    if not filter:
        return False
    for f in filter:
        if f in file_path:
            return True
    return False


"""获取文件后缀
@param file_path 文件路径
@return 文件后缀小写 .mp3 | .mp4 | .mkv | None
"""
def get_file_suffix(file_path)->str:
    try:
        return os.path.splitext(file_path)[1].lower()
    except Exception as e:
        print(e)
        return None

"""获取文件后缀
@param file_path 文件路径
@return 文件后缀小写 .mp3 | .mp4 | .mkv | None
"""
def get_file_name_nosuffix(file_path)->str:
    basename = os.path.basename(file_path)
    try:
        return os.path.splitext(basename)[0]
    except Exception as e:
        print(e)
        return basename

"""移动文件
@param file_path 文件路径
@param target_dir 目标文件夹
@param file_name 文件名
"""
def move(file_path, target_dir,file_name:str = None):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not file_name:
        file_name= os.path.basename(file_path)
    shutil.move(file_path, os.path.join(target_dir, file_name))


"""复制文件
@param file_path 文件路径
@param target_dir 目标文件夹
@param file_name 文件名
"""
def copy(file_path, target_dir,file_name:str = None, delete:bool = False):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not file_name:
        file_name= os.path.basename(file_path)
    print("复制文件: %s  to %s/%s" % (file_path, target_dir , file_name))
    target_file_path = os.path.join(target_dir, file_name)
    if target_file_path != file_path:
        shutil.copy(file_path, target_file_path)
        if delete:
            os.remove(file_path)


"""清理空文件夹
@param root_path 根文件夹路径
"""
def clear_empty_folder(root_path):
    print("开始清理空文件夹:%s" % root_path)
    for root, dirs, _ in os.walk(root_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if len(os.listdir(dir_path)) == 0:
                os.rmdir(dir_path)
                print("清理文件夹:", dir_path)


"""获取目标文件夹路径
@param type 文件类型 tv | movie
@param root_path 根文件夹路径
@return 目标文件夹路径 
"""
def get_success_target_dir(type:str,root_path:str)->str:
    key = 'target_dir_tv'
    def_values = 'TV_Output'
    if type == 'movie':
        key = 'target_dir_movie'
        def_values = 'Movie_Output'
    return get_folder_by_env(key=key,def_values=def_values,root_path=root_path)


"""获取目标文件夹路径
@param type 文件类型 tv | movie
@param root_path 根文件夹路径
@return 目标文件夹路径 
"""
def get_fail_target_dir(type:str,root_path:str)->str:
    key = 'fail_dir_tv'
    def_values = 'TV_Fail'
    if type == 'movie':
        key = 'fail_dir_movie'
        def_values = 'Movie_Fail'
    return get_folder_by_env(key=key,def_values=def_values,root_path=root_path)


"""通过环境变量获取目标文件夹路径
@param key : 环境变量名称
@param def_values : 默认值
@param root_path : 根文件夹路径
@return 目标文件夹路径
"""
def get_folder_by_env(key:str,def_values:str,root_path:str)->str:
    target_dir_name = os.getenv(key, def_values)
    target_dir = os.path.join(root_path, target_dir_name)
    if '/' in target_dir_name or '\\' in target_dir_name:
        target_dir = target_dir_name
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir

"""获取文件大小
@param file_path 文件路径
@return 文件大小  bytes
"""
def get_file_size(file_path):
    size = os.path.getsize(file_path)
    return size