"""下载图片
@param image_url 图片地址
@param target_path 保存路径 xxx/xxx/xxx.jpg
"""
def download_image(image_url , target_path,headers = {}):
    import requests
    try:
        print("下载图片:%s  to %s" % (image_url, target_path))
        response = requests.get(image_url,headers = headers)
        if response.status_code == 200:
            # 下载并且保存文件
            with open(target_path, 'wb') as file:
                file.write(response.content)
            print('图片下载成功:%s' % target_path)
        else:
            print('图片下载失败:%s' % target_path)
        return True
    except Exception as e:
        print('图片下载异常:%s' % target_path)
        return False
    
"""提取视频帧
@param video_path 视频地址  xxx/xxx/xxx.mp4
@param target_path 保存路径 xxx/xxx/xxx.jpg
@param frame_count 第几帧 10
"""
def frame_video_image(video_path, target_path, frame_count:int = 10 )->bool:
    import cv2
    try:
        cap = cv2.VideoCapture(video_path)
        total_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if frame_count > total_count:
            frame_count = total_count - 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
        _, frame = cap.read()
        cv2.imencode('.jpg',frame)[1].tofile(target_path)
        cap.release()
        cv2.destroyAllWindows()
        return True
    except Exception as e:
        print("提取视频帧失败:%s" % e)
        return False
