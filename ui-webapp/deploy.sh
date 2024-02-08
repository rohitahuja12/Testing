
#!/bin/bash

aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 046456031965.dkr.ecr.us-east-2.amazonaws.com
export PHX_API_URL=dev.api.brightestbio.com
docker-compose build --build-arg PHX_API_URL={$PHX_API_URL} ui-webapp
docker tag phoenix_ui-webapp:latest 046456031965.dkr.ecr.us-east-2.amazonaws.com/phoenix_ui_webapp:dev
docker push 046456031965.dkr.ecr.us-east-2.amazonaws.com/phoenix_ui_webapp:dev
