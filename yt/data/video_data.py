from dataclasses import dataclass
from typing import List, Optional

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
    standard: Thumbnail
    maxres: Thumbnail

@dataclass
class Localized:
    title: str
    description: str

@dataclass
class Snippet:
    publishedAt: str
    channelId: str
    title: str
    description: str
    thumbnails: Thumbnails
    channelTitle: str
    tags: Optional[List[str]]
    categoryId: str
    liveBroadcastContent: str
    defaultLanguage: Optional[str]
    localized: Localized
    defaultAudioLanguage: Optional[str]

@dataclass
class ContentDetails:
    duration: str
    dimension: str
    definition: str
    caption: str
    licensedContent: bool
    regionRestriction: Optional[dict]
    contentRating: dict
    projection: str
    hasCustomThumbnail: Optional[bool]

@dataclass
class Status:
    uploadStatus: str
    failureReason: Optional[str]
    rejectionReason: Optional[str]
    privacyStatus: str
    publishAt: Optional[str]
    license: str
    embeddable: bool
    publicStatsViewable: bool
    madeForKids: bool
    selfDeclaredMadeForKids: Optional[bool]

@dataclass
class Statistics:
    viewCount: int
    likeCount: int
    dislikeCount: Optional[int]
    commentCount: int

@dataclass
class TopicDetails:
    topicIds: Optional[List[str]]
    relevantTopicIds: Optional[List[str]]
    topicCategories: List[str]

@dataclass
class Player:
    embedHtml: str
    embedHeight: Optional[int]
    embedWidth: Optional[int]

@dataclass
class Video:
    kind: str
    etag: str
    id: str
    snippet: Snippet
    contentDetails: ContentDetails
    status: Status
    statistics: Statistics
    topicDetails: TopicDetails
    player: Player
    liveStreamingDetails: Optional[dict]


