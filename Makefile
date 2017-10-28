FRONT_PATH=www
API_PATH=api

front-dev:
	cd $(FRONT_PATH) \
	&& npm i \
	&& npm start

front-build:
	cd $(FRONT_PATH) \
	&& sudo npm i -g webpack \
	&& webpack -p

front-prod:
	cd $(FRONT_PATH)/dist \
	&& python -m SimpleHTTPServer 9000

api-dev:
	cd $(API_PATH) \
	&& sudo pip install -r requirements.txt \
	&& python main.py
