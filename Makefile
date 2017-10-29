FRONT_PATH=www
API_PATH=api
DATA_PATH=data

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
	&& python3 -m SimpleHTTPServer 9000

api-dev:
	cd $(API_PATH) \
	&& sudo pip3 install -r requirements.txt \
	&& python3 main.py

feeddb1:
	cd $(DATA_PATH) \
	&& sudo pip3 install -r requirements.txt \
	&& python3 builddata.py -i StationsBaselArea.csv
