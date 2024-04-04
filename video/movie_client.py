import os, time
from engine.entry import MediaType
from engine.tmdb_engine import seach, load_details_by_id
from libs.nfo import write_media_info
from libs.video import traverse_video, get_video_title
from libs.image import download_image
from libs.file import *
from libs.subtitle import sync_subtitle

"""影视视频刮削
遍历文件夹内的视频,并且刮削到指定的文件夹中
变量:
target_dir_tv : 目标文件夹 ,默认为  Output
tmdb_token : tmdb的 `Authorization` [获取token-&gt;](`https://www.themoviedb.org/settings/api`)
fail_dir_tv : 失败文件夹，默认为  Fail

完成功能:
1.批量刮削 scraping_batch
2.单个刮削 scraping  
3.通过tmid单个刮削 scraping_by_id
4.同步字幕
TODO: 
- 没有图片时候获取视频截图
- 翻译内容
- 文件名刮削
"""
class movie_client:
    def __init__(self):
        pass

    """批量刮削
    root_path: 刮削的根目录

    """
    def scraping_batch(self, root_path):
        print("开始刮削路径:%s" % root_path)
        # 获取成功的目标文件夹
        success_target_dir = get_success_target_dir('movie',root_path)
        print("获取到刮削成功目标文件夹:%s" % success_target_dir)
        fail_target_dir = get_fail_target_dir('movie',root_path)
        print("获取到刮削失败目标文件夹:%s" % fail_target_dir)
        file_list = traverse_video(folder=root_path,filter=[os.path.basename(success_target_dir)])
        print("获取到待刮削文件列表:%d" % len(file_list) ," => ", file_list)
        # 遍历文件进行刮削
        for file in file_list:
            if self.filter_scraping(file):
                result = self.scraping(file,success_target_dir)
                print("刮削结果:",result)
                if result !=None and result==False:
                    print("刮削失败，保存到:%s" % fail_target_dir)
                    transfer_file(file, fail_target_dir, delete=True)
                # 添加间隔时间
                print("sleep 10s")
                time.sleep(10)
        # 开始清理空文件夹
        clear_empty_folder(root_path)

    """拦截过滤是否允许刮削"""
    def filter_scraping(self, file_path):
        # TODO 视频大小大于 10M
        # size = get_file_size(file_path)
        # if size < 1024*1024*10:
        #     print("视频文件小于 10MB，跳过:%s" % file_path)
        #     return False
        return True
    

    """开始刮削任务
    @param file_path 文件路径 xxx/xxx/xxx.mp4
    @param target_dir 目标文件夹
    """
    def scraping(self, file_path, target_dir):
        print("开始刮削文件:%s" % file_path)
        title, year = get_video_title(file_path)
        print("提取文件信息(%s):" % file_path,"title:%s" % title, "year:%s" % str(year))
        if title is None:
            # TODO 无法提取标题
            print("无法提取标题，跳过")
            return False
        # 1.通过tmdb进行刮削
        result = self.scraping_by_tmdb(title, year, file_path, target_dir)
        if result == False:
            print("tmdb 刮削失败，开始进行文件名刮削")
            result = self.scraping_by_file_name(title, year, file_path, target_dir)

        return result

    """通过tmdb获取详细信息
    @param title 标题 xxx.2023.mp4  => xxx
    @param year 年份 2023
    @param file_path 文件路径 xxx/xxx/xxx.2023.mp4
    @param target_dir 要转移到的目标文件夹
    """
    def scraping_by_tmdb(self, title:str, year:int, file_path:str, target_dir:str) -> bool:
        tmid = seach(type = MediaType.MOVIE, query = title, year = year)
        if tmid is None:
            print("搜索不到信息，跳过")
            return False
        print("搜索到信息:", tmid)
        return self.scraping_by_tmid(tmid, title, file_path, target_dir)

    """通过tmid获取详细信息
    1. 写入nfo
    2. 拷贝视频
    3. 下载图片

    @param tmid tmdb id
    @param file_path 文件路径 xxx/xxx/xxx.mp4
    @param target_dir 目标文件夹
    @return 是否成功
    """
    def scraping_by_tmid(self, tmid, file_name_title, file_path, target_dir) -> bool:
        media_info = load_details_by_id(tmid=tmid, type=MediaType.MOVIE)
        if media_info is None:
            print("tmdb获取详细信息失败，跳过")
            return False
        real_title = media_info.title
        if not real_title:
            real_title = file_name_title
        media_info.title = real_title
        # print("media_info:", media_info)

        # 1.先写入nfo
        parent_dir = os.path.join(target_dir,"%s (%d)" % (real_title, media_info.year))
        nfo_file =os.path.join(parent_dir ,"%s.nfo" % real_title)
        print("写入nfo文件:",nfo_file)
        write_media_info(nfo_file, media_info)
        # 2.再拷贝文件
        print("复制影视文件到目标文件夹:", parent_dir)
        suffix = get_file_suffix(file_path)
        # 复制 或 移动
        target_file_name = real_title + suffix
        transfer_file(file_path, parent_dir, target_name=target_file_name, delete=True)
        # 下载关键图片 poster | fanart | thumb
        if media_info.poster:
            image_file =  os.path.join(parent_dir, "%s-poster.jpg" % real_title)
            result = download_image(media_info.poster, image_file)
            if result:
                copy(image_file, parent_dir,file_name="%s-thumb.jpg" % real_title, delete=False)
                copy(image_file, parent_dir,file_name="%s-fanart.jpg" % real_title, delete=False)
        # 完成 nfo+视频文件转移后,结束本次任务
        target_video_path = os.path.join(parent_dir, target_file_name)
        self.scraping_subtitle(file_path, target_video_path)
        return True


    """同步字幕文件
    @param file_path 文件路径 xxx/xxx/xxx.mp4
    @param target_dir 目标文件夹
    """
    def scraping_subtitle(self, original_video_path:str, target_video_path:str)->int:
        num = sync_subtitle(original_video_path, target_video_path)
        print("同步字幕文件数量:", num)
        base_dir = os.path.dirname(original_video_path)
        # 清理文件夹
        if len(os.listdir(base_dir)) == 0:
                os.rmdir(base_dir)
                print("清理文件夹:", base_dir)
    
    """通过文件名进行刮削"""
    def scraping_by_file_name(self, title:str, year:int, file_path:str, target_dir:str)->bool:
        return False
