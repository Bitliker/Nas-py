import os
from libs_file import *
from libs_pattern import pattern
# 支持的字幕文件后缀格式
SUBEXT_EXTENSIONS: list = ['.srt', '.ass', '.ssa', '.sup']


"""同步字幕
@param original_video_path: 原始的视频路径
@param target_video_path: 目标的视频路径
@return: 移动多少个字幕文件
"""
def sync_subtitle(original_video_path:str, target_video_path:str)->int:
    source_dir = os.path.dirname(original_video_path)
    title = get_file_name_nosuffix(os.path.basename(target_video_path))
    original_video_name = os.path.basename(original_video_path)
    target_dir = os.path.dirname(target_video_path)
    print("开始同步字幕")
    subtitle_list = get_subtitle_file(source_dir)
    num = 0
    for subtitle in subtitle_list:
        if filter_subtitle(title=title, original_video_name = original_video_name, subtitle_path=subtitle) == False:
            continue
        print("移动字幕文件(%s)到目标文件夹(%s)" % (subtitle, target_dir))
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        suffix = get_file_suffix(subtitle)
        tag = get_subtitle_tag(subtitle) # .chs .cht
        target_file = title + tag + suffix
        transfer_file(file_path=subtitle, target_dir=target_dir, target_name=target_file)
        num+=1
    return num


"""获取字幕的标识
@param subtitle_name: 字幕文件名称
"""
def get_subtitle_tag(subtitle_name)->str:
    # 字幕正则式
    _zhcn_sub_re = r"([.\[(](((zh[-_])?(cn|ch[si]|sg|sc))|zho?" \
                    r"|chinese|(cn|ch[si]|sg|zho?|eng)[-_&](cn|ch[si]|sg|zho?|eng)" \
                    r"|简[体中]?)[.\])])" \
                    r"|([\u4e00-\u9fa5]{0,3}[中双][\u4e00-\u9fa5]{0,2}[字文语][\u4e00-\u9fa5]{0,3})" \
                    r"|简体|简中|JPSC" \
                    r"|(?<![a-z0-9])gb(?![a-z0-9])"
    _zhtw_sub_re = r"([.\[(](((zh[-_])?(hk|tw|cht|tc))" \
                    r"|繁[体中]?)[.\])])" \
                    r"|繁体中[文字]|中[文字]繁体|繁体|JPTC" \
                    r"|(?<![a-z0-9])big5(?![a-z0-9])"
    _eng_sub_re = r"[.\[(]eng[.\])]"
    tag =""
    if pattern(_zhcn_sub_re, subtitle_name, 0):
        tag = ".chs"
    elif pattern(_zhtw_sub_re, subtitle_name, 0):
        tag = ".cht"
    elif pattern(_eng_sub_re, subtitle_name, 0):
        tag = ".eng"
    print("字幕标识:%s(%s)" % (subtitle_name,tag))
    return tag

"""判断字幕文件是否符合规则
@param title: 视频标题修改后的名字  e.g:   xxx.mp4
@param original_video_name: 视频原名称 e.g:  xxx.mp4
@param subtitle_path: 字幕文件路径 e.g:  a/b/xxx.srt
@return: 是否符合
"""
def filter_subtitle(title, original_video_name, subtitle_path)->bool:
    print("过滤字幕文件(%s) (%s)  (%s)" % (title, original_video_name, subtitle_path))
    if not os.path.exists(subtitle_path):
        return False
    basename = os.path.basename(subtitle_path).lower()
    title = get_file_name_nosuffix(title)
    if title in basename:
        return True
    num_tag = pattern(r's(\d+)e(\d+)', title.lower(), 0)
    if num_tag:
        if num_tag in basename:
            return True
    original_video_name = get_file_name_nosuffix(original_video_name).lower()
    if original_video_name in basename:
        return True
    return False

"""获取文件夹下面的所有字幕文件"""
def get_subtitle_file(parent_path)->list[str]:
    
    subtitle_list = []
    if not os.path.isdir(parent_path):
        return subtitle_list
    for file_name in os.listdir(parent_path):
        file_extension = get_file_suffix(file_name)
        if file_extension and  file_extension.lower() in SUBEXT_EXTENSIONS:
            subtitle_list.append(os.path.join(parent_path, file_name))
    return subtitle_list