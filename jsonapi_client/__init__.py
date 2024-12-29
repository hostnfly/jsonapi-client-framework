from datetime import datetime

from .decoders import register
from .collection import JsonAPICollection, JsonAPISingleton, T
from .query import JsonAPIFilterValue, JsonAPIQuery, JsonAPISortValue, JsonAPIIncludeValue

register(datetime,  datetime.fromisoformat)
