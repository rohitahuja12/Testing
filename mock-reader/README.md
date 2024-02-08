# Mock Reader

This project listens to scans in the db and reacts to them as the reader will when it is fully integrated into the phoenix system. This project exists for testing and to support UI developent on the Phoenix architecture. 

# Dependencies

Install the dependencies for this project:
`python -m pip install -r requirements.txt`

# Running

To run this project outside a container: `python ./main.py`
To run this project inside a container use the dockerfile to build an image or use the docker-compose script in the parent directory.
To specify which attachments will be attatched to a scan by the mock-reader, please set the `MOCK_READER_ATTACHMENT_PATHS` environment variable to a comma-separated list of absolute paths within the reader container. Reference volume mounts.
To specify which readerId the `mock-reader` will emulate please set the `MOCK_READER_ID` environment variable.
