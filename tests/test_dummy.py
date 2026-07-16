from typing import Iterator
from textwrap import dedent

from pytest import fixture
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage

@fixture(scope="session")
def couchdb(request) -> Iterator[DockerContainer]:
    env = {
        "COUCHDB_USER": "fdo",
        "COUCHDB_PASSWORD": "fdo",
    }
    with DockerContainer("couchdb", ports=[5984], env=env) as container:
        yield container


@fixture(scope="session")
def fdorganizer_image() -> Iterator[DockerImage]:
    with DockerImage(".", tag="fdorganizer-in-test") as image:
        yield image

@fixture()
def fdorganizer(fdorganizer_image: DockerImage, couchdb: DockerContainer) -> Iterator[DockerContainer]:
    if fdorganizer_image.tag is None:
        assert False, "FDO image has no TAG"

    addr = couchdb.get_container_host_ip()
    couchdb.env.get("COUCHDB_USER")

    env = {
        "COUCHDB_HOST": addr,
        "COUCHDB_PORT": "5984",
        "COUCHDB_USER": couchdb.env.get("COUCHDB_USER", ""),
        "COUCHDB_PASSWORD": couchdb.env.get("COUCHDB_PASSWORD", ""),
    }

    command = dedent("""
    ./docker_init.sh
    ./start.sh
    """)


    with DockerContainer(
        image=fdorganizer_image.tag,
        env=env,
        command=command,
    ) as container:
        yield container



def test_dummy(fdorganizer):
    
    assert True


