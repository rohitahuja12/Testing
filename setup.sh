export PHOENIX_HOME=$(pwd)
export HOST_PHOENIX_HOME=$PHOENIX_HOME
export DB_PROTOCOL=mongodb
export DB_HOST=db
export DB_USER=admin
export DB_PASSWORD=password
export MOCK_READER_ATTACHMENT_PATHS=""
export MOCK_READER_ID=""

#export ATTACHMENTS_DRIVER=s3
export ATTACHMENTS_DRIVER=mongo

# Used when ATTACHMENTS_DRIVER is s3
export ATTACHMENTS_BUCKET=brightest-bio-attachments-dev

# Uncomment to point the services at a local instance of the api
export API_URL=resource-api

# Uncomment to point the services at the dev environment
#export API_URL=api.dev.brightestbio.com
