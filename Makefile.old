RELEASE_TYPE?=patch
tox:
	tox

release:
	make tox
	make push
	make bump
	make tag
	make push
	make pypi


bump:
	bumpversion $(RELEASE_TYPE)

tag:
	$(eval VERSION:=v$(shell bumpversion --dry-run --list patch | grep curr | sed -e 's/^.*=//g'))
	$(eval PREV_TAG:=$(shell git describe --tags --abbrev=0))
	(printf "Changes made in this version: \n"; git log $(PREV_TAG)..HEAD --graph --oneline --pretty="%h - %s") | git tag -F - -s $(VERSION)

push:
	git push
	git push --tags

pypi:
	python3 setup.py sdist bdist_wheel
	twine upload -s dist/*
