from dataclasses import dataclass,field
from enum import Enum

class MediaType(Enum):
    MOVIE = 'movie'
    TV = 'tv'
    UNKNOWN = '未知'
    
@dataclass
class Actors:
    # 名字
    name: str = None
    # 原始名称
    original_name: str = None
    # 扮演角色
    role: str = None
    # 类型
    type: str = "Actor"
    # 对应id
    id: str = None
    # 对应图片地址
    image: str = None
    # 详情地址
    profile: str = None

@dataclass
class MediaInfo:
    # id
    tmid: str = None
    # 编号
    num: str = None
    # 标题
    title: str = None
    # 原标题
    original_title: str = None
    # 类型
    type: MediaType = MediaType.MOVIE
    # 简介
    plot: str = None
    # 发行日期
    released: str = None
    # 年份
    year: int = 0
    '''
    评级
    G - 小孩子的电影
    PG - 家庭电影，偶尔会有一些内容平淡的成熟电影
    PG-13 - 青少年电影或大片，即使有时不适合儿童，如果它足够温和的话
    R - 独立电影和知名电影
    NC-17 - 露骨的色情戏剧
    '''
    mpaa: str = "PG-13"
    # 评分
    rating: float = 0.0
    # 像看人数
    votes: int = 0
    # 时长 s
    runtime: int = 0
    # 系列
    series: str = None
    # 制作商
    studio: str = None
    # 封面
    poster: str = None
    # 预告
    trailer: str = None
    # 来源网站
    website: str = None
    # 标签
    tag:list = field(default_factory=list)
    # 演员 @ Actors
    actors: list[Actors] = field(default_factory=list)

@dataclass
class SeasonInfo:
    '''
        date = data_json['air_date']
        title = data_json['name']
        plot = data_json['overview']
        id = data_json['id']
        poster = data_json['poster_path']
        season_number = data_json['season_number']
        rating = data_json['vote_average']
    '''
    # id
    tmid: str = None
    # 日期
    released: str = None
    year: int = 0
    # 标题
    title: str = None
    # 剧集的标题
    show_title: str = None
    # 原标题
    original_title: str = None
    # 简介
    plot: str = None
    # 封面
    poster: str = None
    # 季数
    season_number: int = 0
    # 评分
    rating: float = 0.0
    # 总集数
    total_episodes: int = 0

@dataclass
class EpisodeInfo:
    # id
    tmid: str = None
    # show id
    show_tmid: str = None
    # 日期
    released: str = None
    # 标题
    title: str = None
    # 剧集的标题
    show_title: str = None
    # 原标题
    original_title: str = None
    # 简介
    plot: str = None
    # 封面
    poster: str = None
    # 季数
    season_number:int = 0
    # 集数
    episode_number: int = 0
    # 评分
    rating: float = 0.0
    # 时长
    runtime:int = 0
    # 作者
    actors: list= field(default_factory=list)




