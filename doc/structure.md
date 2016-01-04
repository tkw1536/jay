## Folder Structure

Jay is powered by Django. It has the following folder structure:

* general django stuff
  * jay/ -- Generic Application configuration files
  * templates/ -- django templates
  * static/ -- Static resources
* django apps:
  * core/ -- Core App
    * no models
    * no implementations
    * home page only
  * votes/
    * voting models
    * vote edit page and vote implementation
  * settings/ -- Settings and Genera
    * VotingSystem model
    * superadmins and systems management
  * users/ -- User Model
    * user model
    * authentication backend (OpenJUB)
    * no views
  * filters/ -- User filters
    * UserFilter model
    * filter implementation (via js: PyExecJS)
    * filter edit page (AKA the forest)
* doc/ -- Documentation
  * minimal developer level documentation