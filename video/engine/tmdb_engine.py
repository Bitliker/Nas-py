import os
import requests
from .entry import MediaInfo , MediaType, Actors, SeasonInfo, EpisodeInfo



image_base_url = "https://image.tmdb.org/t/p/original"
image_thumb_url = "https://image.tmdb.org/t/p/w500"
person_base_url = "https://www.themoviedb.org/person/"
language = "zh"
adult ="false"

'''
搜索内容
type: 类型 movie, tv, person 
    movie: 电影
    tv: 剧集
    person: 人物
返回: tmid, 对应的id 
'''
def seach(type: MediaType, query, year=None):
    year_param = ""
    if year and year > 1900:
        year_param = "&year="+str(year)
    # 通过接口查找数据
    action = "search/%s?query=%s&include_adult=%s&language=%s&page=1%s" % (type.value, query, adult, language, year_param)
    result, data_json = get_request(action=action)
    # 排除错误返回
    if result == False or data_json == None or 'total_results' not in data_json or data_json['total_results'] == 0:
        return None
    results = data_json['results']
    tmid = results[0]['id']
    # 提取最符合的内容
    for item in results:
        if 'original_name' in item:
            if query in item['original_name']:
                tmid = item['id']
                break
        if 'name' in item:
            if query in item['name']:
                tmid = item['id']
                break
        if item['original_title'] == query:
            tmid = item['id']
            break
        if item['title'] == query:
            tmid = item['id']
            break
    return tmid

'''
通过tmid获取详细信息
type: 类型 movie, tv, person
tmid: 对应的id
season_number: 剧集的第几季 ,仅仅支持剧集 tv
返回: MediaInfo
'''
def load_details_by_id(tmid, type:MediaType , season_number=None):
    action = type.value +"/"+str(tmid)
    if type == MediaType.TV and season_number:
        action += "/season/"+str(season_number)
    action+="?language="+language
    result, data_json = get_request(action=action)
    if result == False or data_json == None:
        return None
    '''开始封装实体类''' 
    media_info = MediaInfo()
    media_info.tmid = tmid
    # num & title
    if 'title' in data_json:
        media_info.title = data_json['title']
    if 'name' in data_json:
        media_info.title = data_json['name']
    media_info.num = media_info.title
    # original_title
    if 'original_name' in data_json:
        media_info.original_title = data_json['original_name']
    if 'original_title' in data_json:
        media_info.original_title = data_json['original_title']
    # type
    media_info.type=type
    # plot
    if 'overview' in data_json:
        media_info.plot = data_json['overview']
    # released
    if 'release_date' in data_json:
        media_info.released = data_json['release_date']
    if 'first_air_date' in data_json:
        media_info.released = data_json['first_air_date']
    # year
    if media_info.released and len(media_info.released)>4:
        media_info.year=int(media_info.released[0:4])
    # mpaa
    if 'adult' in data_json:
        if data_json['adult'] == True:
            media_info.mpaa = "NC-17"
        else:
            media_info.mpaa = "PG-13"
    # poster
    if 'poster_path' in data_json:
        media_info.poster = get_image_path(data_json['poster_path'])
    # votes
    if 'vote_count' in data_json:
        media_info.votes = data_json['vote_count']
    # website
    if 'homepage' in data_json:
        media_info.website = data_json['homepage']
    # rating
    if 'vote_average' in data_json:
        media_info.rating = data_json['vote_average']
    # runtime
    if 'runtime' in data_json:
        media_info.runtime = data_json['runtime']
    # # actors
    # if 'cast' in data_json:
    #     media_info.actors = data_json['cast']
    # tag
    if 'genres' in data_json:
        genres = data_json['genres']
        for item in genres:
            media_info.tag.append(item['name'])
    # actors
    media_info.actors = get_credits(type, tmid) 
    # TODO series, studio, trailer
    '''封装实体类结束'''

    return media_info
'''
获取演员列表
type: 类型 movie, tv, person
tmid: 对应的id
返回: 演员列表 @see Actors
'''
def get_credits( type:MediaType, tmid):
    action ="%s/%s/credits?language=%s" % (type.value, str(tmid),language)
    result, data_json = get_request(action=action)
    if result == False or data_json == None:
        return None
    casts = data_json['cast']
    if casts == None or len(casts) == 0:
        return None
    credits:list = []
    for item in casts:
        name = item['name']
        role = item['character']
        id = item['id']
        image = item['profile_path']
        original_name = item['original_name']
        profile = person_base_url + str(id)
        credits.append(Actors(name=name, role=role, id=id, image=get_image_path(image), original_name=original_name, profile=profile))
    return credits

'''
获取剧集类型下的详细列表
tmid: 对应的id
season_number: 第几季
返回: True, SeasonInfo, EpisodeInfo:list | False, None, None
'''
def get_season(tmid,show_title, season_number):
    action = "tv/%s/season/%d?language=%s" % (str(tmid), season_number, language)
    result, data_json = get_request(action=action)
    if result == False or data_json == None:
        return False, None, None
    ''' season info '''
    season = SeasonInfo()
    season.tmid = tmid
    if 'id' in data_json:
        season.tmid = data_json['id']
    if 'air_date' in data_json:
        season.released = data_json['air_date']
    if 'name' in data_json:
        season.title = data_json['name']
    if 'original_name' in data_json:
        season.original_title = data_json['original_name']
    if 'overview' in data_json:
        season.plot = data_json['overview']
    if 'poster_path' in data_json:
        season.poster = get_image_path(data_json['poster_path'])
    if 'season_number' in data_json:
        season.season_number = data_json['season_number']
    if 'vote_average' in data_json:
        season.rating = data_json['vote_average']
    if season.released and len(season.released) > 4:
        season.year = int(season.released[0:4])
    season.show_title = show_title
    '''episodes info'''
    episodes = data_json['episodes']
    if episodes == None or len(episodes) == 0:
        return True, season, None
    episode_list:list = []
    for item in episodes:
        episode = EpisodeInfo()
        if 'id' in item:
            episode.tmid = item['id']
        episode.show_tmid = tmid
        if 'air_date' in item:
            episode.released = item['air_date']
        if 'name' in item:
            episode.title = item['name']
        if 'original_name' in item:
            episode.original_title = item['original_name']
        else:
            episode.original_title = episode.title
        if 'overview' in item:
            episode.plot = item['overview']
        if 'still_path' in item:
            episode.poster = get_image_path(item['still_path'])
        if 'season_number' in item:
            episode.season_number = item['season_number']
        if 'episode_number' in item:
            episode.episode_number = item['episode_number']
        if 'vote_average' in item:
            episode.rating = item['vote_average']
        if "runtime" in item:
            episode.runtime = item['runtime']
        episode.show_title = show_title
        # print("进来的 episode:", episode)
        # 全体工作人员
        credits:list = []
        if "crew" in item:
            crews = item['crew']
            if crews and len(crews) > 0:
                for crew in crews:
                    actor = Actors()
                    if 'job' in crew:
                        actor.type = crew['job']
                    if 'credit_id' in crew:
                        actor.id = crew['credit_id']
                    if 'name' in crew:
                        actor.name = crew['name']
                    if 'original_name' in crew:
                        actor.original_name = crew['original_name']
                    if 'profile_path' in crew:
                        actor.image = get_image_path(crew['profile_path'])
                    if "id" in guest:
                        id = crew["id"]
                        actor.profile = person_base_url + str(id)
                    credits.append(actor)
        # 演员
        if "guest_stars" in item:
            guest_stars = item['guest_stars']
            if guest_stars and len(guest_stars) > 0:
                for guest in guest_stars:
                    actor = Actors()
                    if 'character' in guest:
                        actor.role = guest['character']
                    if 'credit_id' in guest:
                        actor.id = guest['credit_id']
                    if 'name' in guest:
                        actor.name = guest['name']
                    if 'original_name' in guest:
                        actor.original_name = guest['original_name']
                    if 'profile_path' in guest:
                        actor.image =  get_image_path(guest['profile_path'])
                    if "id" in guest:
                        id = guest["id"]
                        actor.profile = person_base_url + str(id)
                    credits.append(actor)
        episode.credits = credits
        print("episode:", episode)
        episode_list.append(episode)
    return True, season, episode_list
'''
通用的get查询
url: 查询的url完整路径
返回: 是否成功，json数据
'''
def get_request(action):
    try:
        base_url = "https://api.themoviedb.org/3/"
        url = base_url + action
        print("开始请求 url:", url)
        headers = {"Authorization":"Bearer "+ os.getenv('tmdb_token','')}
        response = requests.get(url, headers=headers, timeout=10)
        status_code = response.status_code
        if response.status_code!=200:
            print("请求错误 :",str(status_code))
            msg= "请求错误 :"+str(status_code)
            return False, {"code":status_code,"msg":msg}
        data_json = response.json()
        # print("返回数据:", data_json)
        return True, data_json
    except requests.exceptions.Timeout as e:
        print("网络请求超时:",str(e))
        return False, {"code": 500, "msg": "网络请求超时!!!"}
    except Exception as e:
        print("请求异常:",str(e))
        return False, {"code": 500, "msg": str(e)}
    
"""获取图片的url
@param action 图片的url
@param is_thumb 是否是缩略图
@return 图片的url
"""
def get_image_path(action,is_thumb:bool=False):
    if not action:
        return None
    if is_thumb:
        return image_thumb_url+action
    else:
        return image_base_url+action
