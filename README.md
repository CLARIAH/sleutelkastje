# Sleutelkastje
This is a proof-of-concept for transparently handling API keys, delegation tokens and general Satosa logins.

## Usage
Below are a number of API endpoints used for registering applications and their users with the
sleutelkastje.

### Adding an app

> PUT `{sleutelkastje_hostname}/{app_name}`

This request should contain a JSON body:

```json
{
  "credentials": "some-secret-key",
  "redirect": "test"
}
```

### Setting the functional admin for an app

> POST `{sleutelkastje_hostname}/{app_name}/func`

This request should contain a JSON body:
```json
{
  "eppn": "eppn-of-the-user"
}
```

### Inviting a user

In the browser, go to the following URL:

> `{sleutelkastje_hostname}/invite/{app_name}`
