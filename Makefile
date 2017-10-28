front-dev:
	cd www \
	&& npm i \
	&& npm start

front-build:
	cd www \
	&& sudo npm i -g webpack \
	&& webpack -p

front-prod:
	cd www/dist \
	&& python -m SimpleHTTPServer 9000

back:
	cd server \
	&& pip install -r requirements \
	&& python main.py
