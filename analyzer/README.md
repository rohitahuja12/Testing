# Analyzer

The anyzer component for the Auragent Reader Phoenix Architecture.

## Analyses

The schema for an analysis can be found in `Phoenix/db/schemas/analysis.json`.

### Scan/Analysis Artifacts
All artifacts are stored in the DB using the GridFS API. They are retrievable from the API.

### Build and publish new intermediate container

This is shamelessly copied from the amazon console and pasted here for our convenience.

`aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/q3t3c9n8`
`docker build -t auragent-reader-analyzer-partial-public -f ./analyzer/dockerfile.intermediate .`
`docker tag auragent-reader-analyzer-partial-public:latest public.ecr.aws/q3t3c9n8/auragent-reader-analyzer-partial-public:latest`
`docker push public.ecr.aws/q3t3c9n8/auragent-reader-analyzer-partial-public:latest`
