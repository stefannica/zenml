# ZenML API

## Run the database

To start the database
```shell script
docker-compose -f compose.dev.db.yaml up
```

For the first time you run the database:
```shell script
./bootstrap.sh
```

## Run app locally
Make virtualenv and install requirements.txt. Then install GDP.

Finally, navigate to api and run:

```shell script
set -o allexport
source compose.dev.env
set +o allexport
```

Navigate to api/app and run:
```shell script
uvicorn app.main:app --reload
```
