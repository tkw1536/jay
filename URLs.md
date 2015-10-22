# Jay's proposed URL Scheme

All URLs in the list below are relative to the hostname of Jay's instance

* `/settings` - Side-wide, global settings
  * `/users` - Admin and superadmin management
* `/<vote_sys_name>` - overview of all votes in a voting system
  * `/admin` - Voting system, local settings
  * `<vote_name>` - Where you actually vote. Redirect to results after close
  	* `/results` - The results of this vote
  	* `/admin` - Settings for this vote
* `/filters` - List of all filter trees on this voting instance (aka "The Forest")
  * `/new` - Creates a new filter tree and redirects to edit page
  * `<tree_id>` - ??? Maybe this could be where to test filters instead of `/test`
    * `/edit` - Edit a filter tree.
    * `/test` - Runs the filter against the user database to determine who is eligible
  
