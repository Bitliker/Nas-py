"""提取正则表达
@param pattern 正则表达式
@param text 字符串
@param group 分组
@return 提取出的内容  xxx  or None
"""
def pattern(pattern:str, text:str, group:int = None):
    import re
    try:
        if group:
            return re.search(pattern, text).group(group)
        else:
            return re.search(pattern, text).group()
    except Exception as e:
        print("pattern:%s pattern:%s error:%s" % (pattern,text,str(e)))
        return None