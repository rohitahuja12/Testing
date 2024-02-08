# CLI for Phoenix Platform

run installer in cli dir,
	- installs python
	- dependencies for CLI

after running installer, add $PHOENIX\_HOME/cli to your PATH so `phx` can be invoked from anywhere.

The phx cli allows easy command-line interaction with the resource-api, allowing a user to manipulate most of the entities in the system. Attachments are not fully supported at this time.

To get usage details about the cli, run `phx` from the root of phoenix home.

# GAL

`phx parse gal <input> <output>` will parse a gal file and produce the `features` and `spots` sections of a product definition. Additional details about the product will be needed before uploading that product into the database for usage. Please consult schema in `resource-api/src/json_routes/product` for details.
