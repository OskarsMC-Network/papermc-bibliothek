import dataclasses
import datetime
import hashlib
import importlib.metadata
import json
from io import BytesIO
from json import JSONDecodeError
from typing import List, Dict

import dateutil.parser
import urllib3

try:
    __version__ = importlib.metadata.version('papermc-bibliothek')
except importlib.metadata.PackageNotFoundError:
    try:
        __version__ = importlib.metadata.version('bibliothek')
    except importlib.metadata.PackageNotFoundError:
        __version__ = "0.0.0"

PAPER_INSTANCE = 'https://api.papermc.io/v2/'


@dataclasses.dataclass()
class BibliothekProject:
    project_id: str
    project_name: str
    version_groups: List[str]
    versions: List[str]


@dataclasses.dataclass()
class BibliothekVersionGroup:
    project_id: str
    project_name: str
    version_group: str
    versions: List[str]


@dataclasses.dataclass()
class BibliothekChange:
    commit: str
    summary: str
    message: str


@dataclasses.dataclass()
class BibliothekDownload:
    name: str
    sha256: str


@dataclasses.dataclass()
class BibliothekVersionGroupBuild:
    version: str
    build: int
    time: datetime.datetime
    channel: str
    promoted: bool
    changes: List[BibliothekChange]
    downloads: Dict[str, BibliothekDownload]


@dataclasses.dataclass()
class BibliothekVersionGroupBuilds:
    project_id: str
    project_name: str
    version_group: str
    versions: List[str]
    builds: List[BibliothekVersionGroupBuild]


@dataclasses.dataclass()
class BibliothekVersionBuilds:
    project_id: str
    project_name: str
    version: str
    builds: List[int]


@dataclasses.dataclass()
class BibliothekBuild:
    project_id: str
    project_name: str
    version: str
    build: int
    time: datetime.datetime
    channel: str
    promoted: bool
    changes: List[BibliothekChange]
    downloads: Dict[str, BibliothekDownload]


class BibliothekException(Exception):
    pass


class UnexpectedResponseBibliothekException(Exception):
    def __init__(self, response: urllib3.response.HTTPResponse):
        self.response: urllib3.response.HTTPResponse = response

        self._end = self.response.data

        if self.response.status == 404:
            try:
                self._end = "Error: " + json.loads(self._end.decode('utf-8'))["error"]
            except JSONDecodeError:
                self._end = "Data: " + str(self._end)
        else:
            self._end = "Data: " + self._end

        super().__init__()

    def __str__(self):
        return f"HTTP Code: {self.response.status}, expected 200. {self._end}"


class Bibliothek:
    def __init__(self, base_url: str = PAPER_INSTANCE, user_agent: str = f'papermc-bibliothek/{__version__}') -> None:
        """
        Create a Bibliothek instance
        :param base_url: Base URL for the API client, default is the papermc instance.
        """
        self.pool_manager = urllib3.PoolManager(headers={'User-Agent': user_agent})
        self.base_url = base_url

    @staticmethod
    def _change_data_list_to_change_list(changes_list: list) -> List[BibliothekChange]:
        changes = []
        for change in changes_list:
            changes.append(BibliothekChange(change['commit'], change['summary'], change['message']))
        return changes

    @staticmethod
    def _download_data_dict_to_download_dict(download_dict: dict) -> Dict[str, BibliothekDownload]:
        downloads = {}
        for download_key in download_dict.keys():
            download = download_dict[download_key]
            downloads[download_key] = BibliothekDownload(download["name"], download["sha256"])
        return downloads

    def get_projects(self) -> List[str]:
        """
        Get the list of projects
        :return: A List of projects
        """
        response = self.pool_manager.request("GET", f"{self.base_url}projects")
        if response.status != 200:
            raise UnexpectedResponseBibliothekException(response)

        return json.loads(response.data)["projects"]

    def get_project(self, project_id: str) -> BibliothekProject:
        """
        Get a bibliothek project
        :param project_id: a valid bibliothek project id
        :return: The bibliothek project
        """
        response = self.pool_manager.request("GET", f"{self.base_url}projects/{project_id}")
        if response.status != 200:
            raise UnexpectedResponseBibliothekException(response.status)

        project_dict = json.loads(response.data)

        return BibliothekProject(project_dict["project_id"], project_dict["project_name"],
                                 project_dict["version_groups"], project_dict["versions"])

    def get_version_group(self, project_id: str, version_group: str) -> BibliothekVersionGroup:
        """
        Get a version group
        :param project_id: a valid bibliothek project id
        :param version_group: a valid bibliothek version group
        :return: A bibliothek version group object
        """
        response = self.pool_manager.request("GET",
                                             f"{self.base_url}projects/{project_id}/version_group/{version_group}")
        if response.status != 200:
            raise UnexpectedResponseBibliothekException(response)

        version_group_dict = json.loads(response.data)

        return BibliothekVersionGroup(version_group_dict["project_id"], version_group_dict["project_name"],
                                      version_group_dict["version_group"], version_group_dict["versions"])

    def get_version_group_builds(self, project_id: str, version_group: str) -> BibliothekVersionGroupBuilds:
        """
        Get the builds for a bibliothek version group
        :param project_id: a valid bibliothek project id
        :param version_group: a valid version group
        :return: a bibliothek version group builds object
        """
        response: urllib3.response.HTTPResponse = self.pool_manager.request("GET",
                                                                            f"{self.base_url}projects/{project_id}/version_group/{version_group}/builds")
        if response.status != 200:
            raise UnexpectedResponseBibliothekException(response)

        version_group_builds_dict = json.loads(response.data)

        builds = []
        for build in version_group_builds_dict[
            "builds"]:
            builds.append(
                BibliothekVersionGroupBuild(build["version"], build["build"], dateutil.parser.parse(build["time"]),
                                            build["channel"], build["promoted"],
                                            self._change_data_list_to_change_list(build["changes"]),
                                            self._download_data_dict_to_download_dict(build["downloads"])))

        return BibliothekVersionGroupBuilds(version_group_builds_dict["project_id"],
                                            version_group_builds_dict["project_name"],
                                            version_group_builds_dict["version_group"],
                                            version_group_builds_dict["versions"], builds)

    def get_version_builds(self, project_id: str, version: str) -> BibliothekVersionBuilds:
        """
        Get a bibliothek version
        :param project_id: a valid bibliothek project id
        :param version: a valid version for the provided project id
        :return: a bibliothek version object
        """
        response = self.pool_manager.request("GET",
                                             f"{self.base_url}projects/{project_id}/versions/{version}")
        if response.status != 200:
            raise UnexpectedResponseBibliothekException(response)

        version_dict = json.loads(response.data)

        return BibliothekVersionBuilds(version_dict["project_id"], version_dict["project_name"],
                                       version_dict["version"], version_dict["builds"])

    def get_build(self, project_id: str, version: str, build: int) -> BibliothekBuild:
        """
        get a specific build
        :param project_id: a valid bibliothek project id
        :param version: a valid bibliothek version for the project id
        :param build: a valid bibliothek build for the version on the project
        :return: a bibliothek build object
        """
        response: urllib3.response.HTTPResponse = self.pool_manager.request("GET",
                                                                            f"{self.base_url}projects/{project_id}/versions/{version}/builds/{build}")
        if response.status != 200:
            raise UnexpectedResponseBibliothekException(response)

        build_dict = json.loads(response.data)

        return BibliothekBuild(build_dict["project_id"], build_dict["project_name"],
                               build_dict["version"], build_dict["build"], dateutil.parser.parse(build_dict["time"]),
                               build_dict["channel"], build_dict["promoted"],
                               self._change_data_list_to_change_list(build_dict["changes"]),
                               self._download_data_dict_to_download_dict(build_dict["downloads"]))

    def download_build(self, project_id: str, version: str, build: int, filename: str) -> BytesIO:
        """
        downloads a build
        :param project_id: a valid bibliothek project id
        :param version: a valid bibliothek version for the project
        :param build: a valid bibliothek build
        :param filename: the name of the download, eg: `paper-1.18.2-286.jar`
        :return: A BytesIO object with the download
        """
        request = self.pool_manager.request("GET",
                                            f"{self.base_url}projects/{project_id}/versions/{version}/builds/{build}/downloads/{filename}",
                                            preload_content=False)

        download_bytesio = BytesIO()
        while True:
            data = request.read(2 ** 16)  # 64kb
            if not data:
                break
            download_bytesio.write(data)

        request.release_conn()

        if request.status != 200:
            raise UnexpectedResponseBibliothekException(request)

        return download_bytesio

    @staticmethod
    def check_hash(object_to_compare: bytes, hash_to_compare: str) -> bool:
        """
        Compare the hash of a bytes object to a hash
        :param object_to_compare: the object to compare
        :param hash_to_compare: the hash to compare
        :return: if the hashes match
        """
        object_hash = hashlib.sha256(object_to_compare)
        return object_hash.hexdigest() == hash_to_compare
