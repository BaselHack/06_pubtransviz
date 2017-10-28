front:
	cd www && \
	npm i && \
	npm start

back:
	python server/main.py
