Sync is a service which is responsible for synchronizing data in the local database with data in other locations. The unit of work is a 'job' and those are JSON files.

*** Only supports new creation at this time ***
{
	"description": "Synchronize products in database with products on local disk",
	"pollPeriodSeconds": "1",
	"source": {
		"type": "fileSystem",
		"path": "/products",
	},
	"destination": {
		"type": "resourceApi",
		"host": "0.0.0.0:5000",
		"documentType": "products"
	}
}

types of items supported:

	source/dest:
		file
		db doc
		s3

	items:
		binary
