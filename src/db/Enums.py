from enum import Enum

class LikeTarget(str, Enum):
    POST = "post"
    COMMENT = "comment"