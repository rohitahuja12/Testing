#!bin/bash

mongosh <<EOF
rs.initiate() 
use admin
db.createUser({
	user:"admin", 
	pwd: "password", 
	roles: [{ 
		role: "userAdminAnyDatabase", db: "admin" 
	},{
		role: "clusterAdmin", db: "admin"
	}]})
EOF
