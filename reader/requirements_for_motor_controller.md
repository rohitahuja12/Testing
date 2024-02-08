# Requirements for the Motor Controller

## Types of Requests to be Handled

- Go to pos, notify me on arrival (or error)
- Notify me in case of any errors 
- Continuously notify me of position

each client could get a pair of pipes, 1 in, 1 out
is each output queue identical? or are their contents unique?

input message types:
	home
	move to location
	get current location
	get status
	
output message types:
	message acknowledgement
	started movement
	completed movement
	error
