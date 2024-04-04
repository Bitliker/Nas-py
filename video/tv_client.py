import os
from engine.tmdb_engine import *
from engine.entry import MediaType
from libs.nfo import *
from libs.file import *
from libs.subtitle import sync_subtitle
from libs.video import traverse_video, is_video, get_video_title
from libs.image import download_image, frame_video_image
from libs.pattern import pattern
"""剧集刮削

"""
class tv_client:
    def __init__(self):
        pass

    """批量刮削
    root_path: 刮削的根目录, 目录结构 root_path/{title_dir}/{file_name}
            title_dir 格式：{title}.xxx   {title} (year)
    """
    def scraping_batch(self, root_path):
        print("开始刮削路径:%s" % root_path)
        # 获取成功的目标文件夹
        success_target_dir = get_success_target_dir('tv',root_path)
        print("获取到刮削成功目标文件夹:%s" % success_target_dir)
        fail_target_dir = get_fail_target_dir('tv',root_path)
        print("获取到刮削失败目标文件夹:%s" % fail_target_dir)
        parent_dir_list = os.listdir(root_path)
        print("获取到待刮削文件列表:%d" % len(parent_dir_list) ," => ", parent_dir_list)

        for parent_dir in parent_dir_list:
            print("parent_dir:",parent_dir)
            source_dir = os.path.join(root_path, parent_dir)
            if self.filter_scraping(source_dir):
                self.scraping(source_dir, success_target_dir)
            else:
                print("文件夹(%s)不满足刮削条件，跳过" % source_dir)
        clear_empty_folder(root_path)
        
            
    """判断是否需要刮削"""
    def filter_scraping(self, parent_dir)->bool:
        for file in os.listdir(parent_dir):
            if is_video(os.path.join(parent_dir, file)):
                return True
        return False
    
    """刮削单个文件夹
    @param file_path: 文件夹路径
    @param target_dir: 目标文件夹
    """
    def scraping(self, file_path, target_dir):
        print("开始刮削文件夹:%s" % file_path)
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
            # TODO 通过文件名刮削
            result = self.scraping_by_file_name(title, year, file_path, target_dir)

        return result
    
    """通过tmdb获取详细信息
    @param title 标题 xxx.2023.mp4  => xxx
    @param year 年份 2023
    @param file_path 文件路径 xxx/xxx/xxx.2023.mp4
    @param target_dir 要转移到的目标文件夹
    """
    def scraping_by_tmdb(self, title:str, year:int, file_path:str, target_dir:str) -> bool:
        tmid = seach(type = MediaType.TV, query = title, year = year)
        if tmid is None:
            print("搜索不到信息，跳过")
            return False
        print("搜索到信息:", tmid)
        return self.scraping_by_tmid(tmid, title, file_path, target_dir)   

    """通过tmid刮削文件夹"""
    def scraping_by_tmid(self, tmid, file_name_title, file_path, target_dir):
        tv_show = load_details_by_id(tmid=tmid, type=MediaType.TV)
        if not tv_show:
            print("tmdb获取详细信息失败，跳过")
            return False
        """获取真实标题"""
        real_title = tv_show.title
        if not real_title:
            real_title = file_name_title
        tv_show.title = real_title
        tv_dir_name = real_title
        if tv_show.year and tv_show.year > 1900:
            tv_dir_name+=" (%d)" % tv_show.year
        # 获取目标文件夹
        target_tv_dir = os.path.join(target_dir,tv_dir_name)
        # 写入nfo
        nfo_file_path =os.path.join(target_tv_dir ,"tvshow.nfo")
        print("写入nfo文件:",nfo_file_path)
        write_media_info(nfo_file_path, tv_show,"tvshow")
        # 下载封面 
        if tv_show.poster:
            image_file =  os.path.join(target_tv_dir, "poster.jpg" )
            result = download_image(tv_show.poster, image_file)
            if result:
                copy(image_file, target_tv_dir,file_name="thumb.jpg", delete=False)
                copy(image_file, target_tv_dir,file_name="fanart.jpg", delete=False)
        # 提取season
        # 文件夹的 季 数
        dir_season_number = self.get_season_by_file_name(file_path)
        video_list = traverse_video(folder=file_path)
        # season信息, 格式：{str(season_number): season_info} ; e.g: {"S01": season_info, "S10": season_info}
        season_info_list = {}
        # episode信息, 格式：{str(season_number)+str(episode_number): episode_info} ; e.g: {"S01E001": episode_info, "S10E010": episode_info}
        episode_info_list = {}
        for video_item in video_list:
            season_number = self.get_season_by_file_name(video_item)
            if season_number<0 and dir_season_number >=0:
                season_number = dir_season_number
            if season_number<0:
                print("无法提取季数，跳过")
                continue
            season_key = self.get_season_title(season_number)
            episode_number = self.get_episode_by_file_name(video_item)
            if episode_number < 0:
                episode_number = 1
            episode_key = self.get_season_episode(season_number, episode_number) 
            if season_key not in season_info_list:
                """如果不存在,就网络获取"""
                print("该季(%d)没有获取过, 通过网络获取 " % season_number)
                result, seasons, episode_list = get_season(tmid=tmid,show_title=real_title, season_number=season_number)
                if result:
                    print("获取季信息:", seasons)
                    print("获取剧集信息:", episode_list)
                    season_info_list[season_key] = seasons
                    for e_item in episode_list:
                        episode_info_list[self.get_season_episode(e_item.season_number, e_item.episode_number)] = e_item
                else:
                    print("获取季信息失败")
                    continue
            # 判断 season.nfo 是否存在
            season_dir_name =   "Season %d" % season_number
            season_dir_path = os.path.join(target_tv_dir, season_dir_name)
            season_nfo_file = os.path.join(season_dir_path, "season.nfo")
            if not os.path.exists(season_nfo_file):
                print("season.nfo 不存在， 写入....")
                if season_key in season_info_list:
                    season_nfo = season_info_list[season_key]
                    print("写入%s  => season.nfo" % season_nfo)
                    write_season_info(season_nfo_file, season_nfo)
            # 写入 episode.nfo
            episode_info:EpisodeInfo = None
            target_video_name = episode_key
            if episode_key in episode_info_list:
                episode_info = episode_info_list[episode_key]
            if episode_info:
                target_video_name = episode_info.show_title + " - " + episode_key + " - " + episode_info.title
                episode_nfo_file = os.path.join(season_dir_path, target_video_name + ".nfo")     
                if not os.path.exists(episode_nfo_file):
                    print("episode.nfo 不存在， 写入....")
                    write_episode_info(episode_nfo_file, episode_info)
                if episode_info.poster:
                    poster_file = os.path.join(season_dir_path, target_video_name + "-poster.jpg")
                    download_image(episode_info.poster, poster_file)
                    # copy(poster_file,season_dir_path , target_video_name + "-fanart.jpg")
                    # copy(poster_file,season_dir_path , target_video_name + "-thumb.jpg")
            # 转移视频
            target_video_name = target_video_name + get_file_suffix(video_item)
            transfer_file(video_item, season_dir_path, target_video_name)
            # 同步字幕
            sync_subtitle(original_video_path=video_item, target_video_path=os.path.join(season_dir_path, target_video_name))
        return True


    """获取季数标题
    @param number: 季数
    @return: 季数标题 | NONE ; e.g: "S01"
    """
    def get_season_title(self, number:int)->str:
        return "S%02d" % number

    """获取季数标题
    @param number: 集数
    @return: 集数标题 | NONE ; e.g: "E01"
    """
    def get_episode_title(self, number:int)->str:
        return "E%03d" % number
    """获取完整的标题
    @param season_number: 季数
    @param episode_number: 集数
    @return: 集数标题 | NONE ; e.g: "S01E001"
    """
    def get_season_episode(self, season_number, episode_number):
        return "S%02dE%03d" % (season_number, episode_number)
  

    """通过文件名称获取season
    格式: 1. S01E01 - xxx.mp4
    格式: 2. S01 - xxx.mp4
    @param file_path: 文件路径
    @return: season_number | -1
    """
    def get_season_by_file_name(self,file_path):
        try:
            basename = os.path.basename(file_path)
            return int(pattern(r's(\d+)', basename.lower(), 1))
        except Exception as e:
            print("get_season_by_file_name error:", e)
            return 1
    """通过文件名称获取episode
    格式: 1. S01E01 - xxx.mp4
    格式: 2. E01 - xxx.mp4
    @param file_path: 文件路径
    @return: episode_number | -1
    """
    def get_episode_by_file_name(self,file_path):
        try:
            basename = os.path.basename(file_path)
            eposide_number = pattern(r'e(\d+)', basename.lower(), 1)
            if eposide_number:
                return int(eposide_number)
            eposide_number = pattern(r'第(\d+)', basename.lower(), 1)
            if eposide_number:
                return int(eposide_number)
            raise Exception("get_episode_by_file_name error: 未匹配到集数")
        except Exception as e:
            print("get_episode_by_file_name error:", e)
            return -1

    """通过文件名提取 tvshow/season/episode 信息
    """
    def scraping_by_file_name(self, file_name_title:str, year:int, file_path:str, target_dir:str)->bool:
        tv_dir_name = file_name_title
        if not year:
            year = 2019
        if year > 1900:
            tv_dir_name += " (%d)" %  year
        tv_target_dir_path = os.path.join(target_dir, tv_dir_name)
        video_list = traverse_video(folder=file_path)
        # 创建 tv_show
        # title / plot / date / year / tag
        media = MediaInfo()
        media.title = file_name_title
        media.original_title = file_name_title
        if year > 1900:
            media.year = year
            media.released = "%d-01-01" % year
        else:
            media.year = 0
            media.released = "2019-01-01"
        basename = os.path.basename(file_path)
        media.plot = "%s : %s"  % (file_name_title, basename)
        if file_name_title==basename:
            media.plot = file_name_title + "....."
        print("开始写入tvshow.nfo : ", str(media))
        write_media_info(os.path.join(tv_target_dir_path,"tvshow.nfo" ), media, "tvshow")
        for video_item in video_list:
            season_number = self.get_season_by_file_name(video_item)
            episode_number = self.get_episode_by_file_name(video_item)
            video_title = get_file_name_nosuffix(video_item)
            if episode_number <=0:
                print("无法提取到season_number/episode_number : %d/%d" % (season_number, episode_number))
                continue
            num_title = self.get_season_episode(season_number=season_number,episode_number=episode_number)
            
            season_folder = os.path.join(tv_target_dir_path, "Season %d" % season_number)
            season_file_path = os.path.join(season_folder, "season.nfo")
            if not os.path.exists(season_file_path):
                season_media = SeasonInfo()
                season_media.show_title = media.title
                season_media.title = "第 %d 季" % season_number
                season_media.plot = media.title +" : " + season_media.title
                season_media.released = media.released
                season_media.year = media.year
                season_media.season_number = season_number
                print("开始写入season.nfo : ", str(season_media))
                write_season_info(season_file_path, season_media)
            episode_nfo_file_name = file_name_title+ " - " + num_title + ".nfo"
            episode_nfo_file_path = os.path.join(season_folder, episode_nfo_file_name)
            if not os.path.exists(episode_nfo_file_path):
                episode_media = EpisodeInfo()
                episode_media.show_title = media.title
                episode_media.season_number = season_number
                episode_media.title = "第 %d 集" % episode_number
                episode_media.plot = media.title +" " + episode_media.title + " " + video_title
                episode_media.released = media.released
                episode_media.year = media.year
                episode_media.episode_number = episode_number
                episode_media.season_number = season_number
                print("开始写入episode.nfo : ", str(episode_media))
                write_episode_info(episode_nfo_file_path, episode_media)
            video_file_name = file_name_title+ " - " + num_title + get_file_suffix(video_item)
            # 提取视频帧
            poster_path = os.path.join(season_folder, file_name_title+ " - " + num_title +"-poster.jpg")
            if not os.path.exists(poster_path):
                frame_video_image(video_item, poster_path)
            # 标题的图片
            media_poster_path = os.path.join(tv_target_dir_path, "poster.jpg")
            if not os.path.exists(media_poster_path) and os.path.exists(poster_path):
                copy(poster_path, tv_target_dir_path,"poster.jpg", False)
                copy(poster_path, tv_target_dir_path,"fanart.jpg", False)
                copy(poster_path, tv_target_dir_path,"thumb.jpg", False)
            # 判断是否已经存在
            video_file_path = os.path.join(season_folder, video_file_name)
            if not os.path.exists(video_file_path):
                print("开始转移video : ", video_item)
                transfer_file(video_item,season_folder,video_file_name)

        return False
