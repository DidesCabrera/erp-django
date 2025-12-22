# Architecture Principles

- Django monolith
- Fat models, thin views
- No nutrition logic in views or templates
- Templates are read-only consumers

Draft lifecycle:
- Entities created as draft
- Finalization is explicit
- Draft entities cannot be forked or copied
