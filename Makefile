all: setup lint test

setup:
	@pip install flake8 mock nose

lint:
	@flake8 lambdakube/* --max-line-length=100

test:
	@python setup.py test


# Command to aid CI/CD and CloudFormation development
release: lint
	@git status
	$(eval COMMENT := $(shell bash -c 'read -e -p "Comment: " var; echo $$var'))
	@git add --all; \
	 git commit -m "$(COMMENT)"; \
	 git push