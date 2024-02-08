#!/bin/bash


/bin/bash /scripts/wait-for-it.sh -t 120 localhost:27017 -- /scripts/initialize-rs.sh &

/usr/bin/mongod --bind_ip_all --replSet rs0


