# UI Webapp

The UI Webapp is the main GUI for the Phoenix system.


## CORS disabled chrome session for local development 
start a chrome session with web security disabled to allow for local development against the cloud dev resource api
```
open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_sess_1" --disable-web-security
```

## Building the App Container for local development

Export resource-api's url
```
export PHX_API_URL=localhost:5000
```

Build the container
```
docker-compose build --build-arg PHX_API_URL={$PHX_API_URL} ui-webapp
```

Run the container
```
docker-compose up -d ui-webapp
```

## Building and Pushing the App Container

Build the container from the root directory of `Phoenix`
```
export PHX_API_URL={ENVIRONMENT}.api.brightestbio.com
docker-compose build --build-arg PHX_API_URL={$PHX_API_URL} ui-webapp
```

Login to ECR. The dev instructions are here, other environments will differ slightly. The login command for each environment can be created by replacing the account number in each request with the desired account.
```
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 046456031965.dkr.ecr.us-east-2.amazonaws.com
```

Tag the container, updating the `dev` part to the desired environment.
```
docker tag phoenix_ui-webapp:latest 046456031965.dkr.ecr.us-east-2.amazonaws.com/phoenix_ui_webapp:dev
```

Push it real good.
```
docker push 046456031965.dkr.ecr.us-east-2.amazonaws.com/phoenix_ui_webapp:dev
```

Once the container is pushed, log into ECS and kill the current task associated with the API and new one will be created from the most recent image.

### (OSX) Connecting the local webapp to the cloud dev resource api

It's possible to launch a web-security disabled chrome instance which will ignore any cors errors you'll receive when connecting the local webapp to the cloud resource api right now. 

```
set API_URL dev.api.brightestbio.com
open -na Google\ Chrome --args --disable-web-security --user-data-dir=$HOME/profile-folder-name
```

### to build for s3

REACT_APP_API_URL=api.dev.brightestbio.com npm run build --production