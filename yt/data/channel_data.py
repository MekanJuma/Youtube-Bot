from dataclasses import dataclass
from typing import List

@dataclass
class Thumbnail:
    url: str
    width: int
    height: int

@dataclass
class Thumbnails:
    default: Thumbnail
    medium: Thumbnail
    high: Thumbnail

@dataclass
class Snippet:
    # country: str
    description: str
    title: str
    thumbnails: Thumbnails

@dataclass
class Statistics:
    hiddenSubscriberCount: bool
    subscriberCount: str
    videoCount: str
    viewCount: str

@dataclass
class TopicDetails:
    topicCategories: List[str]
    topicIds: List[str]

@dataclass
class ContentDetails:
    relatedPlaylists: dict

@dataclass
class Item:
    contentDetails: ContentDetails
    id: str
    kind: str
    snippet: Snippet
    statistics: Statistics
    # topicDetails: TopicDetails

@dataclass
class ChannelData:
    items: List[Item]
