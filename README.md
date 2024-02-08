# Phoenix

Phoenix is a software platform to control Brightest Bio readers and analyze the data created by those readers. The components of the platform are designed to be deployed in a distributed manner. The `resource-api` and `analyzer` are currently deployed to the cloud and everything in `reader` is deployed to a reader.


## Domain Entities and Vocab

A Reader is a machine that takes images of plates or slides. It is also the name of the software component (`./reader`) that controls that machine. The data associated with running a reader is called a Scan (schema at `./resource-api/src/json_routes/scan.json`). A Scan is a singular instance of processing a plate or slide through the reader. The Analyzer (`./analyzer`) analyzes scans and produces Analyses (schema at `./resource-api/src/json_routes/analysis.json`). The UI (`./ui`) is the graphical user interface for interacting with these entities. The CLI (`./cli`) is the command-line based interface for interacting with these entitites. The UI and the CLI both utilize the resource-api (`./resource-api`) which is the HTTP interface for interacting with these entitites. All configuration and run data is ultimately stored in the database (`./db`). 

Please see the `README.md` files inside of each subdirectory for details about the component projects.

Each component is containerized (for the time being) and can be controlled using docker compose, configured through the `docker-compose.yml` file in the root directory. It is not advisable at this time to simply run `docker compose up` on this project as it will bring up dev-mode and prod-mode services simultaneously. It is better to bring them up individually.

## Installation

Copy this repository to disk. Set an environment variable of `PHOENIX_HOME` to the path where this repository is stored. For example `export PHOENIX_HOME=/home/ian/Phoenix`. Add this command to your `bash.rc` file or other configuration scripts to ensure it is set automatically in new shells.

Install the CLI: `sudo -E ./cli/install.sh`
Use `phx` to install the platform: `sudo -E ./phx admin install`

## Running

To ensure you are using the latest version of all images, run `docker-compose pull` prior to building or starting any containers.

After modifying any code (this includes pulling changes from a remote branch), run `docker-compose build` to ensure the latest changes are reflected in your containers.

To run all the components simultaneously (not usually recommended), run `docker-compose up` in this directory. Individual components can also be started with `docker-compose up db`, for example. Refer to the service names in `./docker-compose.yml` to modify this command for the different services. To start the 'normal' suite of containers (db, api, reader, analyzer) run `phx run start-headless`.

## Source Code Control Policies and Procedures

The general workflow to add new code into the codebase after you have cloned the repository:

1.  Get the latest dev branch: `git checkout dev`
2.  Create and switch to your own feature branch: `git checkout -b xx/feature-branch-name`, where `xx` are your initials and the `feature-branch-name` is a brief description of what you will be working on  
3.  Make changes to your own feature branch code base
4.  Make commits and push changes to the remote branch to save your work in the repository:
	1. To see what files have changed in your branch, use:  `git status`
	2. Add the desired changed files to your commit: `git add <filename>` 
	3. When you have added all of the files you wish to commit:  `git commit -m "Your message here."`, where your message is a description of the changes in the commit.  If you wish to add more detailed information, omit the `-m` parameter and string and you will be switched to an editor context to detail your changes.
5.  Push your changes to the repository with:  `git push`
	1.  If this is the first time you are pushing to the repository with this branch git should provide you with a command to accomplish this after your first attempt.  It will be something along the lines of: `git push --set-upstream origin <xx/feature-branch-name>`
6.  Repeat steps 3 through 5 until you are ready to merge your code into the main dev branch.
7.  When you are ready, create a pull request (PR) via the github UI.  Select the `New pull request` button from the `Pull requests` tab.
8.  Follow the instructions and document your changes.  **Note:  You cannot complete the PR until your code has been reviewed and approved by 1 other person.**
9.  Once your pull request has been reviewed and approved, it is a good practice to merge the latest dev branch into your feature branch locally before merging online.  To do this:
	1.  Switch back to dev and pull:  `git checkout dev` then, `git pull`
	2.  Switch back to your feature branch:  `git checkout xx/feature-branchname`
	3.  Merge dev into your feature branch:  `git merge dev`
	4.  Resolve merge conflicts, if any.
	5.  Push the merge back to the repo:  `git push`
10.  Hit the 'Squash and Merge' button on the pull request page and confirm that the PR has merged successfully. 

## General Tips

### Deleting all stored entries of a given resource

*Ensure you have `jq` installed.*

This command will delete the most recently created scan. By changing the word `scans` to the name of another collection you can repeat the pattern for other document types.

```bash
phx api delete scans $(phx api getall scans | jq -r ".[-1]._id")
```

### Creating calibration attachments

``` bash
curl -X POST -d @/Users/pomme/dev/Phoenix-test-data/calibration.json localhost:5000/scans/62bc63ccfbc943fa5b82066b/attachments/config
```

where `calibration.json` contains 

```JSON
{"cameraCenterCalibrated": {"x":10000,"y":10000}}
```

### Creating a reader mock entity

When the reader starts up if the `MOCK_READER` environment variable is set it will start in mock mode, if it is not set it will expect a reader to be connected. Set the `MOCK_READER` variable to the serialNumber of the `readerMock` that the reader should use for its configuration. Also attach an image called `img` to that readerMock.

mockReader.json
```
{
        "serialNumber": "reader123MOCK",
        "micronsPerMotorStep": {
            "x": 3.175,
            "y": 3.175,
            "z": 1
        },
        "cameraCenterApprox": {
            "x": 45000, 
            "y": -8000
        },
        "cameraFovDims": {
            "x": 4000,
            "y": 4000
        },
        "defaultZ": 800,
        "mockImageTopLeft": {
            "x": 0,
            "y": 0
        },
        "mockImageBottomRight": {
            "x": 120000,
            "y": 400000
        }
    }
```

create readerMock:
```
phx api create readerMocks <path/to/mockReader.json>
```

attach image:
```
curl -X POST --data-binary @<path/to/mockReaderImage.tif> <dbHost:Port>/readerMocks/(phx api getall readerMocks serialNumber=reader123MOCK | jq -r ".[0]._id")/attachments/img
```

Then be sure to restart the reader and go about your hardware-free business.
```
phx run stop reader; phx run up reader;
```

### Moving an Entire Scan from Cloud to Local

Download scan
```
curl https://dev.api.brightestbio.com/scans/6390da7288cfea1806e9e68f > scan.json
```
Modify the `scan.json` file and remove the `_id` field.
Upload scan to local. Note the `_id` in the response, you will need it to upload attachments.
```
curl -X POST -H "Content-Type: application/json" -d @scan.json http://localhost:5000/scans
```
Download all the attachments. Modify for different scans. This example only moves 3 plate rows of images.
```
for x in A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B12 C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12; do curl https://dev.api.brightestbio.com/scans/6390da7288cfea1806e9e68f/attachments/$x > $x; done;
```
Upload all the attachments. Replace `newScanId` with the `_id` of the remote scan (retrieved in an earlier step).
```
for x in A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B12 C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12; do curl --request POST --data-binary @"$x" http://localhost:5000/scans/<newScanId>/attachments/$x; done;
```
Verify the attachments are there...
```
curl http://localhost:5000/scans/<newScanId>/attachments
```
