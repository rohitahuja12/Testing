#!/usr/bin/env bash

cd /home/reader/Phoenix

aws ecr get-login-password --region us-east-2 | \
	docker login --username AWS --password-stdin \
	046456031965.dkr.ecr.us-east-2.amazonaws.com
docker compose pull
docker compose up lfa-reader
