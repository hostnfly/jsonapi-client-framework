from datetime import date, datetime

from .collection import JsonAPICollection, JsonAPISingleton, T
from .decoders import register
from .query import JsonAPIFilterValue, JsonAPIIncludeValue, JsonAPIQuery, JsonAPISortValue
from .schema import JsonAPIResourceIdentifier, JsonAPIResourceSchema

register(date, date.fromisoformat)
register(datetime, datetime.fromisoformat)
