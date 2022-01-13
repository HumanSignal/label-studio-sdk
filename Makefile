SHELL := /bin/bash

install:
	pip install -r requirements.txt
	pip install pdoc3==0.10.0 boto3==1.19.11

watch:
	pdoc label_studio_sdk docs --http localhost:9999 --template-dir docs/pdoc_templates/

build:
	# wget http://localhost:4000/header.html -O docs/pdoc_templates/head.mako
	pdoc label_studio_sdk docs --template-dir docs/pdoc_templates/ --html --force

deploy:
	python3 deploy.py

test:
	pytest tests