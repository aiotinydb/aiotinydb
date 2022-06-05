import nox


@nox.session
def lint(session: nox.Session):
    session.install(".","pyproject-flake8", "flake8-quotes", "pylint")
    session.run("pflake8", "aiotinydb")
    session.run(
        "pylint",
        "--output-format=colorized",
        "--reports=no",
        "aiotinydb",
    )


@nox.session
def mypy(session: nox.Session):
    session.install(".", "mypy", "types-aiofiles")
    session.run("mypy")


@nox.session(python=["3.6", "3.7", "3.8", "3.9", "3.10", "pypy3"])
def test(session: nox.Session):
    session.install("-e", ".[test]")
        session.run(
        "pytest",
        "--cov",
        "--cov-report=xml",
        "--cov-report=term",
        )
