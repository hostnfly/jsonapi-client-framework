# jsonapi-client-framework

Json:API Client Framework provides an object-oriented approach to build your [Json:API](https://jsonapi.org/) clients.

## Installing

```sh
pip install jsonapi-client-framework
```

## Usage

```python
from jsonapi_client import JsonAPICollection, JsonAPIResourceSchema


# Create your dataclass
class Person(JsonAPIResourceSchema):
    first_name: str
    last_name: str
    year_of_birth: int


# Easy setup
class People(JsonAPICollection[Person]):
    endpoint = "/people"
    schema = Person


people = People(base_url="https://your_api.domain.com/v1")
```

## Features

### Get full results as a list

```python
# GET https://your_api.domain.com/v1/people?page[number]=1
# GET https://your_api.domain.com/v1/people?page[number]=2
# ...
# GET https://your_api.domain.com/v1/people?page[number]=23
people_list = people.resources().get()
```

### Get a single result's page

```python
# GET https://your_api.domain.com/v1/people?page[number]=2
people_list, meta = people.resources().paginated(page=2).get()

# GET https://your_api.domain.com/v1/people?page[number]=2&page[size]=30
people_list, meta = people.resources().paginated(page=2, size=30).get()
```

### Filter results

```python
# GET https://your_api.domain.com/v1/people?filter[date_of_birth]=1984&page=1
# ...
# GET https://your_api.domain.com/v1/people?filter[date_of_birth]=1984&page=4
people_list = people.resources().get(filters={"date_of_birth": 1984})
```

### Sort results

```python
# GET https://your_api.domain.com/v1/people?sort=first_name,last_name&page=1
# ...
# GET https://your_api.domain.com/v1/people?sort=first_name,last_name&page=23
people_list = people.resources().get(sort=["first_name", "last_name"])
```

### Related resources

```python
from jsonapi_client import JsonAPIResourceIdentifier


class Movie(JsonAPIResourceSchema):
    title: str
    year: int
    # By default, the Json:API payload contain the identifer only (id and type)
    director: Person | JsonAPIResourceIdentifier


class Movies(JsonAPICollection[Movie]):
    endpoint = "/movies"
    schema = Movie


movies = Movies(base_url="https://your_api.domain.com/v1")

# GET https://your_api.domain.com/v1/movies/178
movie = movies.resource("178").get()
movie.director.id  # => "7"

# GET https://your_api.domain.com/v1/movies/178?include=director
movie = movies.resource("178").get(include="director")
movie.director.year_of_birth  # => 1961

# GET https://your_api.domain.com/v1/movies/178?include=director&page=2
# ...
# GET https://your_api.domain.com/v1/movies/178?include=director&page=117
movies_list_with_directors = movies.resources().get(include="director")
```

### Get a single resource as an object

```python
# GET https://your_api.domain.com/v1/people/49
person = people.resource("49").get()
```

### Update a resource

```python
# PUT https://your_api.domain.com/v1/movies/179
#
# Request payload
#
# {
#   "data": {
#     "attributes": {
#       "year": 1993
#     },
#     "relationships": {
#       "director": {
#         "data": {
#           "id": "55"
#         }
#       }
#     }
#   }
# }
updated_movies = movies.resource("179").update(year=1993, director={"id": "55"})
```

## Advanced features

### Authentication

Json:API Client framework uses [`requests`](https://requests.readthedocs.io/en/latest/) library, so you can take advantage of
its [authentication](https://docs.python-requests.org/en/latest/user/authentication/) feature.

```python
from requests.auth import HTTPBasicAuth

people = People(base_url="https://your_api.domain.com/v1", auth=HTTPBasicAuth('user', 'pass'))
```

### Custom encoding/decoding

```python
from datetime import datetime

from jsonapi_client import encoders, decoders

def to_timestamp(datetime):
    return datetime.timestamp()

# Encode/decode datetime objects as timestamps
encoders.register(datetime, to_timestamp)
decoders.register(datetime, datetime.fromtimestamp)
```
