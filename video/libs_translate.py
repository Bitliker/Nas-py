import os
import enum as _enum

class Language(_enum.Enum):
    CHINESE = "zh"
    ENGLISH = "en"
    JAPANESE = "ja"
    FRENCH = "fr"
    SPANISH = "es"
    KOREAN = "ko"

class TranslateType(_enum.Enum):
    DETECT = "detect"
    TRANSLATE = "translate"

"""翻译文章
@param text 要翻译的文本
@param from_lang 要翻译的语言
@param to_lang 翻译后的语言
@param type 翻译类型
@return 翻译后的文本  bool, str   e.g:  True, "翻译后的文本"
"""
def translate(text:str, from_lang:Language, to_lang:Language,type:TranslateType):
    env_type = os.getenv('translate_type','baidu')

    if env_type == 'google':
        return google_translate(text, from_lang, to_lang)
    else:
        return baidu_translate(text, from_lang, to_lang)
    


def baidu_translate(text:str, from_lang:Language, to_lang:Language):
    pass

def google_translate(text:str, from_lang:Language, to_lang:Language):
    pass