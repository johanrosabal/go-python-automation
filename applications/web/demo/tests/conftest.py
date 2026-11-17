import pytest
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from applications.web.demo.fixtures.preconditions import (
    logged_in_session,
    as_standard_user,
    as_problem_user,
    as_performance_glitch_user,
    as_error_user,
    as_visual_user,
)


@pytest.fixture
def app(request):
    """
    Returns the DemoApp orchestrator from the test class instance.
    This allows functional fixtures to interact with pages.
    """
    return request.instance.app
