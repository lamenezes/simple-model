clean: clean-eggs clean-build
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete

clean-eggs:
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

build: clean
	python setup.py sdist

test:
	py.test
	mypy simple_model

release-patch: build test
	bumpversion patch
	git push origin master --tags
	twine upload dist/*

release-minor: build test
	bumpversion minor
	git push origin master --tags
	twine upload dist/*
