# Jay's proposed URL Scheme

All URLs in the list below are relative to the hostname of Jay's instance

* `/settings` - Side-wide, global settings
  * `/users` - Admin and superadmin management
* `/<vote_sys_name>` - overview of all votes in a voting system
  * `/admin` - Voting system, local settings
  * `/new` - Creates a new vote in the system
  * `/filters` - Manage filters
    * `/new` - Create a new filter (create + redirect only)
    * `/<id>` - Edit page of a certain filter
      * `/edit` - Edit a given filter
      * `/test` - Test a given filter
  * `<vote_name>` - Where you actually vote. Redirect to results after close
  	* `/results` - The results of this vote
  	* `/admin` - Settings for this vote
