# Admin Documentation for FDOrganizer (HITS Edition)

## Overview

### Enabling Administrative Access

* nginx
* ip based filter
* couch-db users

### Accessing the admin interface

* https://hostname:5984/
* login with username/password (from above)

### Organisations

* reviewers
* optional file output location

### Identity Providers

* OIDC
* local users

### Automatic Deletion of Packages

* configured in ...?

### Questionnaire Fields

You can add new questions to the interview and modify existing ones.
See [questionnaire-fields.md](50_questionnaire-fields.md) for more information.
However note that new questions will not be exported by default.
That requires extra work (i.e. a template that uses that information).

## Common Difficulties

* CouchDB (Fauxton) session terminates, but stays on document/database pages
  * reload page and log in again.