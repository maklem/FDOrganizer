
# FDOrganizer Configuration

After logging into Fauxton (see section [administrative access](10_administrative_access.md) on how to get there)
you are presented a list of databases, which are all empty.

You can think of them in groups:
* technical databases: `_global_changes`, `_replicator`, `_users`. We will not touch them.
* authentication databases: `organisations`, `identityproviders`, (`users`). We will configure these now.
* data databases: `packages`, `folders`, `documents`, `metadata`, `reviews`. These describe the data handled within FDO.

In CouchDB every database contains *documents*, which look like json files.
They have technical fields `_id` and `_rev`. Any other field is userdata.

To configure access, we need at least one organisation and one identityprovider.

## Organisations

In FDOrganizer an organisation defines 
* which external data sources can be used to import data,
* who may review submitted packages, and
* (optionally) where exported data is stored

A configuration could look like
```json
{
    "idp_tag": "university.example",
    "name": "Example University",
    "reviewers": [
        "reviewer",
        "admin"
    ],
    "plugins": [
        "dummy"
    ],
    "export_subdirectory": "example_university_data_dir"
}
```

Pay attention to the fields

* `idp_tag` is the name for an `organisation` that an identity provider will refer to.
  It may be set there by value or mapped from user attributes supplied by an external
  identity provider (i.e. Keycloak)
* `reviewers` will review packages and their metadata.
  If using a randomized identifier for user names, it is recommended to prepend a descriptive line.
  ```json
  "reviewers": [
    "Reviewer Name",
    "somerandomnumbersandcharacters@org.example",
    "Another Reviewer Named",
    "morerandomnumbersandcharacters@org.example"
  ]
  ```

## Identity Provider

FDO supports authentication over OpenIDConnect. It can be configured for two use cases.

For testing there is an additional option of local users.

### Login using OIDC for a single organisation

In many cases an identity provider allows users from a single organisation to log in.

Note: Field `organisation` in this document, has to match `idp_tag` defined in an organisation before.

```json
{
    "name": "Login of Example University",
    "type": "KEYCLOAK",
    "client_id": "fdo",
    "client_secret": "12345678",
    "url": "https://localhost:8000/realms/master/protocol/openid-connect/",
    "username_field": "preferred_username",
    "displayname_field": "email",
    "organisation": "university.example",
    "scope": [
        "openid",
        "profile"
    ]
}
```

### Login using OIDC for organisations distinguished by user attributes

In project HITS we have a single identity provider for all organisations.
Instead of a fixed `organisation`, here we need to configure `organisation_field`.
It refers to a data field in userinfo, which we get from the OIDC server.

```json
{
    "name": "Multi-Site Login",
    "type": "KEYCLOAK",
    "client_id": "fdo-multi-site",
    "client_secret": "12345678",
    "url": "https://localhost:8000/realms/master/protocol/openid-connect/",
    "username_field": "preferred_username",
    "displayname_field": "email",
    "organisation_field": "org",
    "scope": [
        "openid",
        "profile"
    ]
}
```

If a user authenticates, they are mapped to a matching organisation.
If no such organisation exists, the login is cancelled.

### Login using local users

> [!WARNING]
> Highly insecure! Only use in a dev/testing environment not accessible from the internet.

For local users we have a tiny configuration, with `type: LOCAL`.
```json
{
    "name": "Login of Example University [Local]",
    "type": "LOCAL",
    "organisation": "university.example"
}
```

Additionally we need user documents with name and password, that need to be stored in the `users` database.

For a regular user
```json
{
    "username": "nutzer1",
    "password": "passwort1"
}
```

In the example a user named `reviewer` is a reviewer. It can be created with
```json
{
    "username": "reviewer",
    "password": "reviewer"
}
```
