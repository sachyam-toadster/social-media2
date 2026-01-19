from enum import Enum

class LikeTarget(str, Enum):
    POST = "post"
    COMMENT = "comment"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "Image"
    VIDEO = "Video"
    FILE = "File"