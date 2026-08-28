
from dataclasses import dataclass
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from requests import Response

from jsonapi_client.collection import JsonAPICollection, JsonAPISingleton
from jsonapi_client.schema import JsonAPIResourceSchema


@dataclass
class Person(JsonAPIResourceSchema):
    full_name: str


@dataclass
class Movie(JsonAPIResourceSchema):
    title: str
    year: int
    # By default, the Json:API payload contain the identifer only (id and type)
    director: Person


@dataclass
class Series(JsonAPIResourceSchema):
    title: str
    seasons: int

class MoviesCollection(JsonAPICollection[Movie]):
    endpoint = "/movies"
    schema = Movie

class MovieSingleton(JsonAPISingleton[Movie]):
    endpoint = "/movie"
    schema = Movie

class MediaCollection(JsonAPICollection[Movie | Series]):
    endpoint = "/media"
    schema = Movie | Series


class TestClient(TestCase):
    @patch("jsonapi_client.client.request")
    def test_list_paginated(self, test_request: MagicMock) -> None:
        collection = MoviesCollection(base_url="http://example.com/api", auth=None)
        fixture = Path("tests/fixtures/movies.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result, meta = collection.list().paginated()

        self.assertEqual(len(result), 2)
        self.assertEqual(meta["total"], 2)
        self.assertEqual(result[0].title, "Das weiße Band - Eine deutsche Kindergeschichte")
        self.assertEqual(result[0].year, 2009)
        self.assertEqual(result[0].director.full_name, "Michael Haneke")
        self.assertEqual(result[1].title, "Funny Games")
        self.assertEqual(result[1].year, 1997)
        self.assertEqual(result[1].director.full_name, "Michael Haneke")

    @patch("jsonapi_client.client.request")
    def test_list_all(self, test_request: MagicMock) -> None:
        collection = MoviesCollection(base_url="http://example.com/api", auth=None)
        fixture = Path("tests/fixtures/movies.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result = collection.list().all()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Das weiße Band - Eine deutsche Kindergeschichte")
        self.assertEqual(result[0].year, 2009)
        self.assertEqual(result[0].director.full_name, "Michael Haneke")
        self.assertEqual(result[1].title, "Funny Games")
        self.assertEqual(result[1].year, 1997)
        self.assertEqual(result[1].director.full_name, "Michael Haneke")

    @patch("jsonapi_client.client.request")
    def test_list_polymorphic(self, test_request: MagicMock) -> None:
        collection = MediaCollection(base_url="http://example.com/api", auth=None)
        fixture = Path("tests/fixtures/media.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result, meta = collection.list().paginated()

        self.assertEqual(len(result), 2)
        self.assertEqual(meta["total"], 2)
        self.assertIsInstance(result[0], Movie)
        self.assertIsInstance(result[1], Series)

    @patch("jsonapi_client.client.request")
    def test_get_resource(self, test_request: MagicMock) -> None:
        collection = MoviesCollection(base_url="http://example.com/api/761", auth=None)
        fixture = Path("tests/fixtures/movie.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result = collection.resource("761").get()
        self.assertEqual(result.title, "Funny Games")
        self.assertEqual(result.year, 1997)
        self.assertEqual(result.director.full_name, "Michael Haneke")

    @patch("jsonapi_client.client.request")
    def test_update_resource(self, test_request: MagicMock) -> None:
        collection = MoviesCollection(base_url="http://example.com/api/761", auth=None)
        fixture = Path("tests/fixtures/movie.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result = collection.resource("761").update(title="Funny Games")
        self.assertEqual(result.title, "Funny Games")
        self.assertEqual(result.year, 1997)
        self.assertEqual(result.director.full_name, "Michael Haneke")

    @patch("jsonapi_client.client.request")
    def test_create_resource(self, test_request: MagicMock) -> None:
        collection = MoviesCollection(base_url="http://example.com/api/761", auth=None)
        fixture = Path("tests/fixtures/movie.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result = collection.create(title="Funny Games")
        self.assertEqual(result.title, "Funny Games")
        self.assertEqual(result.year, 1997)
        self.assertEqual(result.director.full_name, "Michael Haneke")

    @patch("jsonapi_client.client.request")
    def test_cget_singleton(self, test_request: MagicMock) -> None:
        collection = MovieSingleton(base_url="http://example.com/api", auth=None)
        fixture = Path("tests/fixtures/movie.json")
        response = Response()
        response.status_code = 200
        response._content = fixture.read_bytes()
        test_request.return_value = response

        result = collection.resource().get()
        self.assertEqual(result.title, "Funny Games")
        self.assertEqual(result.year, 1997)
        self.assertEqual(result.director.full_name, "Michael Haneke")

