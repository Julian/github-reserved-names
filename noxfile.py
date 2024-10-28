from pathlib import Path
from tempfile import TemporaryDirectory

import nox

ROOT = Path(__file__).parent
PYPROJECT = ROOT / "pyproject.toml"
FILE = ROOT / "github_reserved_names.py"
TESTS = ROOT / "test_github_reserved_names.py"


nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = []


def session(default=True, **kwargs):  # noqa: D103
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(**kwargs)(fn)

    return _session


@session(python=["3.8", "3.9", "3.10", "3.11", "pypy3"])
def tests(session):
    """
    Run the test suite with a corresponding Python version.
    """
    session.install("pytest", ROOT)
    session.run("pytest", TESTS)


@session()
def audit(session):
    """
    Audit dependencies for vulnerabilities.
    """
    session.install("pip-audit", ROOT)
    session.run("python", "-m", "pip_audit")


@session(tags=["build"])
def build(session):
    """
    Build a distribution suitable for PyPI and check its validity.
    """
    session.install("build", "twine")
    with TemporaryDirectory() as tmpdir:
        session.run("python", "-m", "build", ROOT, "--outdir", tmpdir)
        session.run("twine", "check", "--strict", tmpdir + "/*")


@session(tags=["style"])
def style(session):
    """
    Check Python code style.
    """
    session.install("ruff")
    session.run("ruff", "check", FILE, TESTS, __file__)


@session()
def typing(session):
    """
    Check static typing.
    """
    session.install("pyright", ROOT)
    session.run("pyright", *session.posargs, FILE)
