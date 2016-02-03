# Introduction

Jay provides secret majority votes to any member of Jacobs University. This guide elaborates on defining filters, configuring a vote, and the permissions of different classes of users.

# Filters

Filters are user-defined, arbitrary complexity boolean expressions. Users who satisfy the specified condition can vote.  Jay defines multiple primitive operators that can be applied to compare fields in a user's profile to given constants.

#### Primitives
* Equality: `equals` or `==` or `===`, all equivalent
* Less than: `<`
* Greater than: `>`

#### Logic
* Binary: `AND` `OR` `XOR`
* Unary: `NOT`
* Constants: `true` `false`

#### User profile fields

Any field in the user profile object can be used in a primitive filter expression. A sample user is provided below.
```
{
  "eid": "39126",
  "email": "l.kuboschek@jacobs-university.de",
  "username": "lkuboschek",
  "active": true,
  "firstName": "Leonhard",
  "lastName": "Kuboschek",
  "fullName": "Leonhard Kuboschek",
  "country": "Germany",
  "flag": "https://api.jacobs-cs.club/flags/Germany.png",
  "picture": "https://api.jacobs-cs.club/user/image/lkuboschek/image.jpg",
  "college": "Nordmetall",
  "phone": "6210",
  "room": "NB-351",
  "isCampusPhone": true,
  "type": [
    "Student"
  ],
  "isStudent": true,
  "isFaculty": false,
  "isStaff": false,
  "description": "ug 17 CS",
  "status": "undergrad",
  "year": "17",
  "majorShort": "CS",
  "major": "Computer Science"
}
```

# Votes

#### Staging
Votes have 5 stages that are activated in the following order:

###### Init
Newly created votes are created in this state. All details are editable.

###### Staged
Once votes enter this state, no further edits to any part of it are allowed. If an opening time is set, the vote will open automatically.

###### Open
Any eligible user can vote. If a closing time is specified, the vote will close automatically.

###### Closed
No further voting is allowed. Individual user participation records are discarded. Results are visible to admins of the voting system instance. If a publication time was specified, the results will be published at that time.

###### Public
The last stage of any vote. Results are public.


# Permissions

#### Anyone
* View vote results
* View a list of voting systems

#### Logged in users
* Vote, if eligible

#### System admins
* Create vote in system instance
* Create and edit filters in system instance
* Change admin rights for system instance

#### Super admins
* Create or edit any vote
* Create or edit any filter
* Change super admin to others
