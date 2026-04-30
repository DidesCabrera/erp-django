# Architecture Layers

My Scoope is currently structured as a modular Django monolith.

The goal is to keep Django as the main product shell while separating business logic, presentation composition, and interface concerns.

## Layers

### Interface

Path examples:

- `notas/interface/views/`
- `notas/urls.py`

Responsibilities:

- Receive HTTP requests.
- Apply Django decorators.
- Read form/request data.
- Call application use cases or commands.
- Manage web-only concerns such as `messages`, `redirect`, `render`, and uploaded files.
- Build the final page response.

Interface code should not contain core business writes such as creating meals, updating DailyPlanMeal relations, replacing snapshots, or creating shares.

### Application Use Cases

Path examples:

- `notas/application/use_cases/`

Responsibilities:

- Orchestrate page-level flows.
- Build page data.
- Coordinate access services, picker payloads, and presentation builders.
- Keep views thin.

Use cases can prepare data for the web interface, but should avoid owning visual structure directly when that belongs to presentation.

### Application Commands

Path examples:

- `notas/application/services/commands/`

Responsibilities:

- Execute write operations.
- Create, update, delete, copy, fork, save, share, configure, and attach domain objects.
- Encapsulate changes that may later be reused from API, MCP, internal AI, or mobile clients.
- Return explicit result objects.

Commands should not depend on:

- `request`
- `messages`
- `redirect`
- templates
- HTML
- JavaScript
- browser state

### Application Services

Path examples:

- `notas/application/services/`

Responsibilities:

- Shared application rules.
- Access resolution.
- Nutrition calculations.
- Food aggregation.
- User-specific nutrition context.

### Presentation

Path examples:

- `notas/presentation/`

Responsibilities:

- Build viewmodels.
- Build content contracts for templates.
- Resolve icons, titles, labels, navigation, breadcrumbs, header actions, and UI metadata.
- Convert application data into UI-ready structures.

Presentation should not execute writes to the database.

### Domain

Path examples:

- `notas/domain/`

Responsibilities:

- Django models.
- Domain properties.
- Nutrition fields.
- Core invariants.
- Model-level calculations where appropriate.

### Templates and Static Assets

Path examples:

- `notas/templates/`
- `notas/static/notas/`

Responsibilities:

- Render UI.
- Handle client-side interaction.
- Consume already-prepared contracts.

Templates and JavaScript should not duplicate business rules when those rules belong to commands or services.