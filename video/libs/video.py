import os
from moviepy.editor import VideoFileClip
from .file import filter_file
from .pattern import pattern


VIDEO_EXTENSIONS: list = ['.mp4', '.mkv', '.ts', '.iso',
                          '.rmvb', '.avi', '.mov', '.mpeg',
                          '.mpg', '.wmv', '.3gp', '.asf',
                          '.m4v', '.flv', '.m2ts', '.strm',
                          '.tp']

"""遍历全部的文件
@param folder 文件夹路径
@param filter 文件过滤 [path1, path2]
@return 文件路径列表 ['/Users/xxx/xxx/xxx.mp4', '/Users/xxx/xxx/xxx.mp4']
"""
def traverse_video(folder,filter:list[str] = None):
    file_list = []
    print("filter:",filter)
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            print("file_path:",file_path, "is_video:",is_video(file_path) , "filter_file:",filter_file(file_path,filter))
            if is_video(file_path) and filter_file(file_path,filter) == False:
                file_list.append(file_path)
    if file_list and len(files)>0:
        file_list.sort()
    return file_list




"""判断是否视频
@param file_path 文件路径
@return 是否是视频 True:是 False:不是
"""
def is_video(file_path):
    if not os.path.isfile(file_path):
        return False
    file_extension = os.path.splitext(file_path)[1]
    # print("file_extension:",file_extension)
    if len(file_extension) > 0 and file_extension.lower() in VIDEO_EXTENSIONS:
        return True
    return False

"""提取视频信息
@param file_path 文件路径
@return video_title, year   xxxx, 2020 | None, 0
"""
def get_video_title(file_path):
    try:
        file_name = os.path.basename(file_path)
        title = file_name
        year = pattern(r'\b(19|20)\d{2}\b', file_name, 0)
        if '.' in file_name:
            title = file_name.split('.')[0]
        elif ' (' in file_name:
            title = file_name.split(' (')[0]
        if not year:
            year = 0
        return title, int(year)
    except Exception as e:
        print(e)
        return None, 0

"""获取视频时长
@param video_path 视频路径
@return 视频时长 s
"""
def get_video_duration(video_path):
    video = VideoFileClip(video_path)
    duration = video.duration
    video.close()
    return duration