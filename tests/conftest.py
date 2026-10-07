# Conftest
#
# PyTest's file for shared fixtures and overrides
from collections.abc import Iterator
from textwrap import dedent

from pytest import fixture
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


@fixture(scope="session")
def fdorganizer_image() -> Iterator[DockerImage]:
    with DockerImage(".", tag="fdorganizer-in-test") as image:
        yield image
        print("=== Logs: fdorganizer_image ===")
        print(image.get_logs())


FDORGANIZER_SCOPE="module"


@fixture(scope=FDORGANIZER_SCOPE)
def fdo_network() -> Iterator[Network]:
    net = Network()
    net.create()
    yield net
    # net.remove()


@fixture(scope=FDORGANIZER_SCOPE)
def couchdb(request, fdo_network: Network) -> Iterator[DockerContainer]:
    env = {
        "COUCHDB_USER": "fdo",
        "COUCHDB_PASSWORD": "fdo",
    }
    container = (
        DockerContainer("couchdb")
        .with_network(fdo_network)
        .with_envs(**env)
        .waiting_for(LogMessageWaitStrategy("Apache CouchDB has started on"))
    )
    with container:
        yield container
        print("=== Logs: couchdb ===")
        print(container.get_logs())



@fixture(scope=FDORGANIZER_SCOPE)
def fdorganizer(fdorganizer_image: DockerImage, couchdb: DockerContainer, fdo_network: Network) -> Iterator[DockerContainer]:
    if fdorganizer_image.tag is None:
        assert False, "FDO image has no TAG"

    addr = couchdb.get_docker_client().bridge_ip(container_id=couchdb.get_wrapped_container().id)

    env = {
        "COUCHDB_HOST": addr,
        "COUCHDB_PORT": "5984",
        "COUCHDB_USER": couchdb.env.get("COUCHDB_USER", ""),
        "COUCHDB_PASSWORD": couchdb.env.get("COUCHDB_PASSWORD", ""),
        "TOKEN_SECRET": "this-is-a-test",
        "TEST_SESSION_NOT_SECURE": "yes",
    }

    command = dedent("""
    bash -c "./docker_init.sh && ./start.sh"
    """)

    container = (
        DockerContainer(fdorganizer_image.tag)
        .with_envs(**env)
        .with_network(fdo_network)
        .with_command(command)
        .waiting_for(LogMessageWaitStrategy("=== done. ===").with_startup_timeout(30))
    )
    with container:
        yield container
        print("=== Logs: fdorganizer ===")
        print(container.get_logs())


@fixture(scope=FDORGANIZER_SCOPE)
def fdorganizer_url(fdorganizer: DockerContainer) -> str:
    addr = fdorganizer.get_docker_client().bridge_ip(container_id=fdorganizer.get_wrapped_container().id)
    return f"http://{addr}:8000/"
