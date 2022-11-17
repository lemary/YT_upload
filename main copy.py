import shutil
import function
from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo
from datetime import datetime
import os

config = function.get_config()
channel = function.make_chanel()


def add_to_playlist(youtube_id, playlist_id, youtube):
    request = youtube.playlistItems().insert(
            part = "snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": youtube_id
                        }
                    }
                }
        )
    response = request.execute()
    return response

id = None

while True:
    print("\n input id or write exit \n")
    
    id = input()   
    if id == "exit":
        break

    data = function.get_table(config, "таблица монтажеров ")
    data = data[config["columns"]]
    data = data.set_index("lecture_id")
    
    result = function.read_table(config, "upload")
    
    print(data.loc[id])
    print("\npaste id again if all correct\n")
    
    if input() != id:
        continue
    
    video_path = f"{data.loc[id]['Ссылка на готовую запись']}\{id}.mp4"
    if not os.path.exists(video_path):
        print("file doesn't exist: "+video_path)
        continue
    video =  LocalVideo(file_path = video_path)

    video.set_title(data.loc[id]["Название Yt"])

    video_description = data.loc[id]["Описание Yt"]
    timecode_path = f"{data.loc[id]['Ссылка на готовую запись']}"+r"\timecode.txt"
    if os.path.exists(timecode_path):
        f = open(timecode_path, "r", encoding = "utf-8")
        timecode = f.read()
        video_description = f"{video_description}\n{timecode}"
        print(video_description)
    else:
        print("no timecode")
        print(timecode_path)
    video.set_description(video_description)

    video.set_category("education")
    video.set_default_language("ru")
    
    video.set_embeddable(True)
    video.set_license("youtube")
    video.set_privacy_status(data.loc[id]["privacyStatus"])
    video.set_public_stats_viewable(True)


    picture_path = f"{data.loc[id]['Ссылка на готовую запись']}\picture.jpg"
    if os.path.exists(picture_path):
        video.set_thumbnail_path(picture_path)
    else:
        print(f"There is no picture path -- {picture_path}\n")

   
    video = channel.upload_video(video)
    if video.id is not None:
        now = datetime.now().strftime("%d.%m.%Y %H:%M")

        play_list = f"{data.loc[id]['Плейлист'].removeprefix(config['playlist_prefix'])}"
        playlist = add_to_playlist(video.id, play_list, channel.channel)
        video_url = "youtu.be\\"+video.id
        print(f'sucsesfully uploaded: {video_url}')

        check = [now, id, video_url,playlist["snippet"]["playlistId"]]
        if playlist["snippet"]["playlistId"] != play_list:
            print("error to add to playlist")
            result.insert_rows(1, values=[now, id, video_url,False])

        else:
            print(f'sucsesfully add to {play_list}')
            result.insert_rows(1, values=[now, id, video_url, config['playlist_prefix']+playlist["snippet"]["playlistId"]]) 
    
    else:
        print(f'Failed uploaded: {id}')


