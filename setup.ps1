# Set PHOENIX_HOME to the current directory
$env:PHOENIX_HOME = Get-Location
$env:HOST_PHOENIX_HOME = $env:PHOENIX_HOME
$env:DB_PROTOCOL = "mongodb"
$env:DB_HOST = "db"
$env:DB_USER = "admin"
$env:DB_PASSWORD = "password"
$env:MOCK_READER_ATTACHMENT_PATHS = ""
$env:MOCK_READER_ID = ""

# Set ATTACHMENTS_DRIVER to mongo
$env:ATTACHMENTS_DRIVER = "mongo"

# Used when ATTACHMENTS_DRIVER is s3
$env:ATTACHMENTS_BUCKET = "brightest-bio-attachments-dev"

# Uncomment to point the services at a local instance of the api
$env:API_URL = "resource-api"

# Uncomment to point the services at the dev environment
# $env:API_URL = "api.dev.brightestbio.com"