

from xml.dom import minidom
import os


"""写入影视整体信息 nfo 文件
movie | tvshow
@param nfo_path nfo 文件路径
@param media_info 媒体信息  @see MediaInfo
@param root_tag 根元素 movie | tvshow
"""
def write_media_info(nfo_path, media_info,root_tag = "movie"):
    # print("nfo_path:", nfo_path, "  media_info:", media_info)
    # 创建DOM文档对象
    doc = minidom.Document()
    # 创建根元素
    root = doc.createElement(root_tag)
    doc.appendChild(root)
    # 添加标题番号
    add_node(doc, root, "num", media_info.num)
    add_node(doc, root, "title", media_info.title)
    original_title = media_info.original_title
    if original_title is None:
        original_title = media_info.title
    add_node(doc, root, "original_title", original_title)
    add_node(doc, root, "sorttitle", media_info.title)
    # 添加简介
    add_node(doc, root, "plot", media_info.plot)
    add_node(doc, root, "outline", media_info.plot)
    add_node(doc, root, "originalplot", media_info.plot)
    # 添加日期
    if media_info.released:
        add_node(doc, root, "tagline","发行日期 %s" % media_info.released)
    add_node(doc, root, "premiered", media_info.released)
    add_node(doc, root, "releasedate", media_info.released)
    add_node(doc, root, "release", media_info.released)
    add_node(doc, root, "year", media_info.year)
    # 评级
    add_node(doc, root, "mpaa", media_info.mpaa)
    add_node(doc, root, "customrating", media_info.mpaa)
    # actor
    # print("media_info.actors:", media_info.actors)
    # print("-------------------------------------")
    if media_info.actors:
        for actor_item in media_info.actors:
            # print("actor_item:", actor_item)
            actor_node = doc.createElement("actor")
            root.appendChild(actor_node)
            add_node(doc, actor_node, "name", actor_item.name)
            add_node(doc, actor_node, "type", actor_item.type)
            add_node(doc, actor_node, "role", actor_item.role)
            add_node(doc, actor_node, "thumb", actor_item.image)
            add_node(doc, actor_node, "profile", actor_item.profile)
    # 评分
    add_node(doc, root, "rating", str(media_info.rating))
    add_node(doc, root, "criticrating", str(media_info.rating))
    # 收藏人数
    add_node(doc, root, "votes", str(media_info.votes))
    # 时长
    add_node(doc, root, "runtime", str(media_info.runtime))
    # 系列
    add_node(doc, root, "series", media_info.series)
    if media_info.series:
        set = doc.createElement("set")
        root.appendChild(set)
        add_node(doc, set, "name", str(media_info.series))       
    # studio
    add_node(doc, root, "studio", media_info.studio)
    add_node(doc, root, "maker", media_info.studio)
    add_node(doc, root, "publisher", media_info.studio)
    add_node(doc, root, "label", media_info.studio)
    # 标签
    if media_info.tag:
        for tag in media_info.tag:
            add_node(doc, root, "tag", tag)
        for tag in media_info.tag:
            add_node(doc, root, "genre", tag)
    # poster
    add_node(doc, root, "poster", media_info.poster)
    add_node(doc, root, "cover", media_info.poster)
    add_node(doc, root, "trailer", media_info.trailer)
    add_node(doc, root, "website", media_info.website)
    if media_info.tmid:   
        node = doc.createElement('uniqueid')
        node_text = doc.createTextNode(str(media_info.tmid))
        node.appendChild(node_text)
        node.setAttribute('type', 'tmdb')
        node.setAttribute('default', 'true')
        root.appendChild(node)
    nfo_dir = os.path.dirname(nfo_path)
    if not os.path.exists(nfo_dir):
        os.makedirs(nfo_dir)
    # 将DOM文档写入文件并进行格式化
    with open(nfo_path, "w", encoding="utf-8") as f:
        doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8",standalone="yes")

"""写入季节信息 nfo 文件
season.nfo
@param nfo_path nfo 文件路径
@param season_info 季节信息  @see SeasonInfo
"""
def write_season_info(nfo_path, season_info):
    # 创建DOM文档对象
    doc = minidom.Document()
    # 创建根元素
    root = doc.createElement('season')
    doc.appendChild(root)
    add_node(doc, root, "title", season_info.title)
    original_title = season_info.original_title
    if original_title is None:
        original_title = season_info.title
    add_node(doc, root, "original_title", original_title)
    add_node(doc, root, "showtitle", season_info.show_title)
    add_node(doc, root, "sorttitle", season_info.title)

    add_node(doc, root, "plot", season_info.plot)
    add_node(doc, root, "outline", season_info.plot)

    add_node(doc, root, "premiered", season_info.released)
    add_node(doc, root, "aired", season_info.released)
    add_node(doc, root, "releasedate", season_info.released)
    add_node(doc, root, "release", season_info.released)
    add_node(doc, root, "year", season_info.year)
    add_node(doc, root, "ratings", season_info.rating)

    add_node(doc, root, "lockdata", 'false')

    add_node(doc, root, "seasonnumber", season_info.season_number)

    add_node(doc, root, "poster", season_info.poster)
    if season_info.tmid:   
        node = doc.createElement('uniqueid')
        node_text = doc.createTextNode(str(season_info.tmid))
        node.appendChild(node_text)
        node.setAttribute('type', 'tmdb')
        node.setAttribute('default', 'true')
        root.appendChild(node)
    nfo_dir = os.path.dirname(nfo_path)
    if not os.path.exists(nfo_dir):
        os.makedirs(nfo_dir)
    # 将DOM文档写入文件并进行格式化
    with open(nfo_path, "w", encoding="utf-8") as f:
        doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8",standalone="yes")    

"""写入集信息 nfo 文件
episode.nfo
@param nfo_path nfo 文件路径
@param episode_info 集信息  @see EpisodeInfo
"""
def write_episode_info(nfo_path, episode_info):
    # 创建DOM文档对象
    doc = minidom.Document()
    # 创建根元素
    root = doc.createElement('episodedetails')
    doc.appendChild(root)
    add_node(doc, root, "title", episode_info.title)
    original_title = episode_info.original_title
    if original_title is None:
        original_title = episode_info.title
    add_node(doc, root, "original_title", original_title)
    add_node(doc, root, "showtitle", episode_info.show_title)
    add_node(doc, root, "sorttitle", episode_info.title)

    add_node(doc, root, "plot", episode_info.plot)
    add_node(doc, root, "outline", episode_info.plot)

    add_node(doc, root, "premiered", episode_info.released)
    add_node(doc, root, "aired", episode_info.released)
    add_node(doc, root, "releasedate", episode_info.released)
    add_node(doc, root, "release", episode_info.released)
    add_node(doc, root, "ratings", episode_info.rating)

    add_node(doc, root, "lockdata", 'false')

    add_node(doc, root, "seasonnumber", episode_info.season_number)
    add_node(doc, root, "episodenumber", episode_info.episode_number)
    add_node(doc, root, "tmdid", episode_info.tmid)
    if episode_info.tmid:   
        node = doc.createElement('uniqueid')
        node_text = doc.createTextNode(str(episode_info.tmid))
        node.appendChild(node_text)
        node.setAttribute('type', 'tmdb')
        node.setAttribute('default', 'true')
        root.appendChild(node)
    nfo_dir = os.path.dirname(nfo_path)
    if not os.path.exists(nfo_dir):
        os.makedirs(nfo_dir)
    # 将DOM文档写入文件并进行格式化
    with open(nfo_path, "w", encoding="utf-8") as f:
        doc.writexml(f, indent="", addindent="  ", newl="\n", encoding="utf-8",standalone="yes")  

'''
添加xml节点
doc: xml文档
parant: 父节点
name: 节点名
text: 节点文本
'''
def add_node(doc, parant, name, text):
    if text:
        node = doc.createElement(name)
        node_text = doc.createTextNode(str(text))
        node.appendChild(node_text)
        parant.appendChild(node)

