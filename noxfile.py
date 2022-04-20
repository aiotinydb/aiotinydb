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
    session.install("mypy", "types-aiofiles")
    session.run("mypy", "--ignore-missing-imports", "aiotinydb")


@nox.session(python=["3.6","3.7","3.8","3.9","3.10","pypy3"])
def test(session: nox.Session):
    session.install(".", "coverage[toml]") #, "hypothesis", "responses")
    try:
        session.run(
            "coverage", "run", "-m", "unittest", "discover"
        )
    finally:
        session.run("coverage", "report")
