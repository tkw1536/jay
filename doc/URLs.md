# Jay's proposed URL Scheme

All URLs in the list below are relative to the hostname of Jay's instance

* `/settings` - Admin and superadmin management, create new vote system

* `/<vote_sys_name>` - overview of all votes in a voting system
  * `/admin` - Voting system, local settings
  * `/new` - Creates a new vote in the system

  * `<vote_name>` - Where you actually vote. Redirect to results after close
  	* `/results` - The results of this vote
  	* `/admin` - Settings for this vote

* `/filters` - List of all filter trees on this voting instance (aka "The Forest")
  * `/new/<vote_sys_name>/` - Creates a new filter tree and redirects to edit page

  * `<tree_id>` - Runs the filter against the user database to give an example for who you can vote
    * `/edit` - Edit a filter tree.
    * `/delete` - Delete a filter tree. 
