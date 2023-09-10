from pyyoutube import Api
from data.video_data import *

from pytube import YouTube

def download(video_url):
    video = YouTube(video_url)
    video = video.streams.get_highest_resolution()
    
    try:
        video.download(VIDEO_SAVE_DIRECTORY)
    except:
        return "Failed to download video"

    return "video was downloaded successfully"



api_key = "api key here"

channel_id = "UCJK4lWXTBYJ8JVBRGU8tDjQ"
video_id = "Nd9BkIORPME"
playlist_id = 'PLzesgjpiATMOX3lOmgnNwGUJJId8vqIaK'

channel_url_pattern = 'https://www.youtube.com/channel/' + channel_id
video_url_pattern = 'https://www.youtube.com/watch?v=' + video_id    
playlist_url_pattern = 'https://www.youtube.com/playlist?list=' + playlist_id  

VIDEO_SAVE_DIRECTORY = "./videos"
AUDIO_SAVE_DIRECTORY = "./audio"

class YouTubeClient:
    def __init__(self, api_key, total_quota=10000):
        self.api = Api(api_key=api_key)
        self.total_quota = total_quota
        self.used_quota = 0

    def get_video_info(self, video_id):
        video = self.api.get_video_by_id(video_id=video_id)
        self.used_quota += 1  # list operation costs 1 unit
        return video.items[0].to_dict()

    def search_videos(self, keyword, count=10):
        search_response = self.api.search(q=keyword, count=count)
        self.used_quota += 100  # list operation costs 100 units
        return [item.to_dict() for item in search_response.items]

    def get_playlist_videos(self, playlist_id):
        playlist = self.api.get_playlist_by_id(playlist_id=playlist_id)
        self.used_quota += 1  # list operation costs 1 unit
        return playlist.items[0].to_dict()

    def get_channel_info(self, channel_id):
        channel = self.api.get_channel_info(channel_id=channel_id)
        self.used_quota += 1  # list operation costs 1 unit
        return channel.items[0].to_dict()
    
    def download(self, video_url):
        video = YouTube(video_url)
        video = video.streams.get_highest_resolution()
        
        try:
            video.download(VIDEO_SAVE_DIRECTORY)
        except:
            print("Failed to download video")

        print("video was downloaded successfully")
    
    def download_audio(self, video_url):
        video = YouTube(video_url)
        audio = video.streams.filter(only_audio = True).first()

        try:
            audio.download(AUDIO_SAVE_DIRECTORY)
        except:
            print("Failed to download audio")

        print("audio was downloaded successfully")
    
    def get_all_videos_from_channel(self, channel_id):
        next_page_token = ""

        video_ids = []
        while True:
            # Fetch the next page of search results
            search_response = self.api.search(
                channel_id=channel_id,
                count=50,  # Fetch the maximum number of results per request
                page_token=next_page_token
            )
            self.used_quota += 100

            for item in search_response.items:
                if item.id.videoId is not None:
                    video_ids.append(item.id.videoId)

            if search_response.nextPageToken is not None:
                next_page_token = search_response.nextPageToken
            else:
                break

        videos = []
        for video_id in video_ids:
            video_data = self.get_video_info(video_id)
            
            try:
                video = Video(
                    kind=video_data['kind'],
                    etag=video_data['etag'],
                    id=video_data['id'],
                    snippet=Snippet(**video_data['snippet']),
                    contentDetails=ContentDetails(**video_data['contentDetails']),
                    status=Status(**video_data['status']),
                    statistics=Statistics(**video_data['statistics']),
                    topicDetails=TopicDetails(**video_data['topicDetails']),
                    player=Player(**video_data['player']),
                )
                videos.append(video)
            except Exception as e:
                print(e)
                print(video_data)

        return videos

    def get_remaining_quota(self):
        return self.total_quota - self.used_quota



if __name__ == '__main__':
    client = YouTubeClient(api_key)

    # Get video info
    # video_info = client.get_video_info(video_id)
    # print(json.dumps(video_info, indent=4, sort_keys=True))

    # Search videos
    # search_keyword = 'python tutorial'
    # search_results = client.search_videos(search_keyword)
    # print(json.dumps(search_results, indent=4, sort_keys=True))

    # Get playlist videos
    # playlist_videos = client.get_playlist_videos(playlist_id)
    # print(json.dumps(playlist_videos, indent=4, sort_keys=True))

    # Get channel info
    # channel_info = client.get_channel_info(channel_id)
    # print(json.dumps(channel_info, indent=4, sort_keys=True))
    
    # Download
    # client.download('https://www.youtube.com/shorts/QoWimxnHSx0?feature=share')
    
    # videos = client.get_all_videos_from_channel('UCPIWehw43V2ZP-K8-qbkpRQ')
    # video_dicts = [asdict(video) for video in videos]
    
    # df = pd.DataFrame(video_dicts)
    # df.to_excel('videos.xlsx')
    # with open('videos.json', 'w') as f:
    #     json.dump(videos, f, indent=4)
