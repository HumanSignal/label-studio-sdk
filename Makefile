SHELL := /bin/bash

install:
	pip install -r requirements.txt
	pip install pdoc3==0.10.0 boto3==1.19.11

watch:
	pdoc label_studio_sdk docs --http localhost:9999 --template-dir pdoc_templates/

build:
	pdoc label_studio_sdk docs --template-dir pdoc_templates/ --html --force

deploy:
	python3 deploy.py