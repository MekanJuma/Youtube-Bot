from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient.errors import HttpError

from yt.credentials import *
from yt.data.channel_data import *
import re


class YouTubeManager:
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_FORCE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    YOUTUBE_SCOPES = [YOUTUBE_UPLOAD_SCOPE, YOUTUBE_FORCE_SSL_SCOPE]
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.creds = creds[channel_name]
        self.client_secrets_file = self.creds["CLIENT_SECRETS_FILE"]
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(
            self.client_secrets_file, scope=self.YOUTUBE_SCOPES
        )
        storage = Storage(f"channels/{self.channel_name}-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        return build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            credentials=credentials,
        )

    def get_my_channel_details(self):
        request = self.youtube.channels().list(
            part="id, snippet, statistics, contentDetails, topicDetails", mine=True
        )
        response = request.execute()
        channels = self.dict_to_dataclass(response)
        selected_channel = channels.items[0] if len(channels.items) > 0 else None

        return selected_channel

    def upload_yt_video(self, file_path, title, description, tags, categoryId):
        body = dict(
            snippet=dict(
                title=title, description=description, tags=tags, categoryId=categoryId
            ),
            status=dict(privacyStatus="public", selfDeclaredMadeForKids=False),
        )

        try:
            insert_request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True),
            )

            response = None
            while response is None:
                status, response = insert_request.next_chunk()

            if "id" in response:
                video_url = "https://www.youtube.com/watch?v=" + response["id"]
                return ("success", "Video was successfully uploaded.", video_url)
            else:
                status, msg = (
                    "error",
                    f"The upload failed with an unexpected response: {response}",
                    None,
                )
                return status, msg
        except HttpError as e:
            print("ERROR", e)
            return "error", f"An HTTP error {e.resp.status} occurred: {e.content}", None
        except Exception as e:
            print("ERROR", e)
            return "error", f"An error occurred: {e}", None

    def delete_video(self, video_id):
        request = self.youtube.videos().delete(id=video_id)
        request.execute()

    def update_video(self, video_id, title, description, category_id):
        request = self.youtube.videos().update(
            part="snippet,status",
            body={
                "id": video_id,
                "snippet": {
                    "title": title,
                    "description": description,
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": "public"},
            },
        )
        response = request.execute()

    def get_comments(self, video_id):
        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
        )
        response = request.execute()
        count = 1
        while response:
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]

                author = comment["snippet"]["authorDisplayName"]
                text = comment["snippet"]["textDisplay"]
                comment_id = comment["id"]
                print(f"Comment Number {count}")
                print(
                    f'Comment Id: {comment_id}\nAuthor: {author}\nText: {text}\n{30*"<=>"}'
                )

                count += 1

            # Check if there are more comments and continue iterating
            if "nextPageToken" in response:
                response = (
                    self.youtube.commentThreads()
                    .list(
                        part="snippet",
                        videoId=video_id,
                        textFormat="plainText",
                        pageToken=response["nextPageToken"],
                    )
                    .execute()
                )
            else:
                break

    def reply_to_comment(self, comment_id, text):
        request = self.youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": text,
                },
            },
        )
        response = request.execute()
        print(f'Replied to comment: {response["id"]}')

    def get_channel_id(self, username):
        request = self.youtube.channels().list(
            part="id, snippet, statistics, contentDetails, topicDetails",
            forUsername=username,
        )
        response = request.execute()

        return response

    def get_video_categories(self):
        try:
            request = self.youtube.videoCategories().list(
                part="snippet", regionCode="US"
            )
            response = request.execute()

            for item in response["items"]:
                print(f'id: {item["id"]}, title: {item["snippet"]["title"]}')
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")

    def dict_to_dataclass(self, d):
        return ChannelData(
            items=[
                Item(
                    contentDetails=ContentDetails(**item["contentDetails"]),
                    id=item["id"],
                    kind=item["kind"],
                    snippet=Snippet(
                        # country=item['snippet']['country'],
                        description=item["snippet"]["description"],
                        title=item["snippet"]["title"],
                        thumbnails=Thumbnails(
                            default=Thumbnail(
                                **item["snippet"]["thumbnails"]["default"]
                            ),
                            medium=Thumbnail(**item["snippet"]["thumbnails"]["medium"]),
                            high=Thumbnail(**item["snippet"]["thumbnails"]["high"]),
                        ),
                    ),
                    statistics=Statistics(**item["statistics"]),
                    # topicDetails=TopicDetails(**item['topicDetails']),
                )
                for item in d["items"]
            ],
        )


def clean_title(title):
    remove_tags = re.sub(r"@[A-Za-z0-9_.]+", "", title)
    remove_credits = remove_tags.lower().replace("credits:", "").replace("credits", "")

    tags = """
    #shorts #cats #animals #cute
    #CuteCats #AdorableKittens #FunnyCats #CatsOfInstagram #CatsPlaying #FluffyCats #KittensPlaying #CatLovers #CatVideos #CuteAnimals #PurrfectPets #FelineFriends #KittensOfYouTube #CuteCatCompilation #MeowMoments #CatNapTime #KittyLove #CatCutenessOverload #PawsomeFelines #CutestCatEver
    """

    result = remove_credits + tags
    return result.upper()


