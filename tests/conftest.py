import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--save-to-json",
        action="store",
        nargs="?",
        const="scripts_json",
        help="Save lock/unlock scripts to JSON files in the specified directory",
    )
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def save_to_json_folder(request):
    return request.config.getoption("--save-to-json")
