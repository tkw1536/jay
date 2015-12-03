# Jay's proposed URL Scheme

All URLs in the list below are relative to the hostname of Jay's instance

* `/settings` - global settings management
  * `/superadmins` - Manage admins (page itself unused)
    * `/add` - Add a superadmin
    * `/remove` - Remove a superadmin
  * `/systems` - Voting System management
    * `/new` - Create a new voting system
    * `/<vote_sys_id>` - Edit voting system
      * `/delete` - Delete a voting system

* `/<vote_sys_name>` - overview of all votes in a voting system
  * `/settings` - Voting system, local settings
  * `/admins` - Manage admins (page itself unused)
    * `/add` - Add an admin
    * `/remove` - Remove an admin
  * `/new` - Creates a new vote in the system
  * `<vote_name>` - Where you actually vote. Redirect to results after close
  	* `/results` - The results of this vote
  	* `/edit` - Edit this vote
      * `/options` - Options (page itself unused)
        * `/add` - Adding a new option
        * `/edit` - Editing an option
        * `/delete` - Removing an option
      * `/filter` - Edit vote filter
      * `/stage` - Edit vote staging
      * `/delete` - Deleting a vote

* `/filters` - List of all filter trees on this voting instance (aka "The Forest")
  * `/new/<vote_sys_name>/` - Creates a new filter tree and redirects to edit page

  * `<tree_id>` - Runs the filter against the user database to give an example for who you can vote
    * `/edit` - Edit a filter tree.
    * `/delete` - Delete a filter tree.

* `/login` - Login to the system
* `/logout` - Logout of the system
* `/imprint` - Legal imprint
* `/privacy` - Privacy stuff
* `/help` - Help pages


Restricted Words:

'settings', 'systems', 'new', 'admin', 'results', 'edit', 'delete', 'login', 'logout', 'imprint', 'privacy', 'help', 'superadmins'
