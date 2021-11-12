# Deploy the Label Studio SDK documentation

To deploy the Label Studio SDK documentation locally, follow these steps. 


## Install pdoc

```
make install
```
    
## Run HTTP server with hot reloader

```
make watch
```
or
```
pdoc label_studio_sdk docs --http localhost:9999 --template-dir docs/pdoc_templates/ --html
```

## Build HTML for deployment

```
make build
```
or
```
pdoc label_studio_sdk docs --template-dir docs/pdoc_templates/ --html --force
```

## Deployment

Set AWS credentials first:
```
AWS_ACCESS_KEY_ID = <key>
AWS_SECRET_ACCESS_KEY = <secret>
```

then perform the deployment:
```
make deploy
```
