from pathlib import Path

import nox

ROOT = Path(__file__).parent
PYPROJECT = ROOT / "pyproject.toml"
FILE = ROOT / "github_reserved_names.py"
TESTS = ROOT / "test_github_reserved_names.py"


nox.options.sessions = []


def session(default=True, **kwargs):
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(**kwargs)(fn)

    return _session


@session(python=["3.8", "3.9", "3.10", "3.11", "pypy3"])
def tests(session):
    session.install("pytest", ROOT)
    session.run("pytest", TESTS)


@session()
def audit(session):
    session.install("pip-audit", ROOT)
    session.run("python", "-m", "pip_audit")


@session(tags=["build"])
def build(session):
    session.install("build")
    tmpdir = session.create_tmp()
    session.run("python", "-m", "build", ROOT, "--outdir", tmpdir)


@session(tags=["style"])
def readme(session):
    session.install("build", "twine")
    tmpdir = session.create_tmp()
    session.run("python", "-m", "build", ROOT, "--outdir", tmpdir)
    session.run("python", "-m", "twine", "check", "--strict", tmpdir + "/*")


@session(tags=["style"])
def style(session):
    session.install("ruff")
    session.run("ruff", "check", FILE, TESTS, __file__)


@session()
def typing(session):
    session.install("pyright", ROOT)
    session.run("pyright", FILE)
