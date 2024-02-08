## Components

### Orchestrator

	The Orchestrator service controls the starting, restarting, and termination of all other services on the reader. It is configured by json file and is the only service invoked by the container on startup.
	Different service configurations can be achieved by editing `reader/dockerfile` to invoke the orchestrator with other config files.

### Reader-API

	The Reader-API (RAPI) is the semi-RESTful frontend for the Reader-Task-Worker. Tasks are issued to the worker through this API. Task can also be interrupted through this API. Only one task can exist at a time.

### Reader-Task-Worker
	
	The Reader-Task-Worker is responsible for executing tasks. It is the only service that issues commands to the camera, stages, and laser. 

	The RTW is invoked by command line, with the first argument to the process being the `id` of the task to be executed. RTW will retrieve the rest of the details about that task from the api. When that task has completed (in success or error) the RTW will gracefully release its hardware resources and exit. 


