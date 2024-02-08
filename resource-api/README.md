# Resource API

The resource API serves as the central API for the Phoenix system.

## Building and Pushing the API Container

Build the container from the root directory of `Phoenix`
```
docker build -t phoenix_api -f ./resource-api/dockerfile .
```

Login to ECR. The dev instructions are here, other environments will differ slightly. The login command for each environment can be created by replacing the account number in each request with the desired account.
```
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 046456031965.dkr.ecr.us-east-2.amazonaws.com
```

Tag the container, updating the `dev` part to the desired environment.
```
docker tag phoenix_api:latest 046456031965.dkr.ecr.us-east-2.amazonaws.com/phoenix_api:dev
```

Push it real good.
```
docker push 046456031965.dkr.ecr.us-east-2.amazonaws.com/phoenix_api:dev
```

Once the container is pushed, log into ECS and kill the current task associated with the API and new one will be created from the most recent image.
