# Sleutelkastje
This is a proof-of-concept for a centralised API key authentication system to be used for several HuC APIs. This will help making it easier to have role-based permissions and authentication in small applications where building its own authentication system would not be practical.

Sleutelkastje allows application owners ("operators") to add "items" to their applications, for a more granular access to the application itself. Users can then be invited to an application with specific roles per item. Authentication to the Sleutelkastje itself (for accepting invitations and managing API keys) supports OIDC.

## Documentation
The API for interacting with the Sleutelkastje has been documented in the [OpenAPI specification](openapi.yaml).
