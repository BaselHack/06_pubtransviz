front:
	cd www && \
	npm i && \
	npm start

front-prod:
	cd www/dist && \
	python -m SimpleHTTPServer 9000

back:
	python server/main.py
