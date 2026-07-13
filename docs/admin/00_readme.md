# Admin Documentation for FDOrganizer (HITS Edition)

## Installation Overview

Installing FDOrganizer is raw and technical compared to most other software.
You will need some experience using a linux shell and editing files on the
command line to succeed.

The process is structured as follows

1.  [Installation of core files and technical web access](05_installation.md)  
    Afterwards you have a running FDOrganizer instance, but you can not do
    anything there yet. You do not even get an option to login.
2.  [configure administrative access](10_administrative_access.md)  
    You now have the option to configure FDO, but it still needs to be done.
3.  [configure user access](20_user_access.md)  
    Now you can log into FDOrganizer, create packages, upload files, and
    review packages.
4.  [maintenance](40_maintenance.md)  
    To keep FDO running smoothly, old data needs to be deleted. You will
    configure that here.

## Questionnaire Fields

You can add new questions to the interview and modify existing ones.
See [questionnaire-fields.md](50_questionnaire-fields.md) for more information.
However note that new questions will not be exported by default.
That requires extra work (i.e. a template that uses that information).

## Assumptions

In this documentation we will create a user named `fdorganizer`
with home directory `/srv/fdorganizer`. Into the home directory we clone the
git reporitory as `FDOrganizer` and create a python virtual environmnent as
`venv`.

Scripts and configurations are supplied on the assumption of these paths.


## Common Difficulties

* CouchDB (Fauxton) terminates sessions quickly, but stays on document/database pages.
  When it seems broken, reload page and log in again.
