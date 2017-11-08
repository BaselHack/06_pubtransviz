# Getting started

## React Application

### Instructions

1) create a `.env` file in `www` folder, following the structure of `.env.default`
2) replace the credentials in it, such as your `MAPBOX_TOKEN`
3) run `make front-dev`
4) you should see your app at `http://localhost:9000`


## Back-end

### Initialize content

To populate the database with data execute `builddata.py` in the `data` folder. This requires to set
the API key of the trias web-service (you can request it from https://opentransportdata.swiss/, format `VDV 431 Default`)

```shell
export TRIAS_API_KEY = 'your key'
```

#### Requirements

The following python modules are required for the back-end:

* pymongo
* progressbar2 (`pip install progressbar2`)
