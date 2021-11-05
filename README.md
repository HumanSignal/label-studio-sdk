# Label Studio SDK

This package provides a set of python classes for operating with Label Studio using <a href="https://labelstud.io/api/">Label Studio API</a> for <a href="labelstud.io">Label Studio</a>
    

## Install pdoc

```
make install
```
    
## Run http server with hot reloader

```
make watch
```
or
```
pdoc label_studio_sdk docs --http localhost:9999 --template-dir pdoc_templates/ --html
```

## Build html for deployment

```
make build
```
or
```
pdoc label_studio_sdk docs --template-dir pdoc_templates/ --html --force
```

## Deployment

Set AWS credentials first:
```
AWS_ACCESS_KEY_ID = <key>
AWS_SECRET_ACCESS_KEY = <secret>
```

```
make deploy
```






<img src="https://labelstud.io/images/opossum/other/5.svg" width="400px">