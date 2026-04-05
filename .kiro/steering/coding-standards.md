# VehicleIQ Coding Standards

## Python Backend

### Language & Framework
- Python 3.11+ with type hints for all functions
- FastAPI for all API endpoints
- Pydantic v2 for data validation and serialization
- SQLAlchemy 2.0+ ORM (no raw SQL queries)
- Async/await patterns for I/O operations

### Code Style
- Black for code formatting (line length: 100)
- Ruff for linting (replace flake8, isort, pylint)
- Type hints required for all function signatures
- Docstrings for all public functions (Google style)

### Project Structure
```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Config, security, dependencies
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── tests/        # Test files
```

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

## TypeScript Frontend

### Language & Framework
- TypeScript 5.0+ with strict mode enabled
- Next.js 14 with App Router (not Pages Router)
- React 18 with functional components and hooks
- No class components

### UI Components
- shadcn/ui components only (no custom component libraries)
- TailwindCSS for all styling (no CSS modules or styled-components)
- Lucide React for icons
- Radix UI primitives (via shadcn/ui)

### Code Style
- ESLint with TypeScript rules
- Prettier for formatting
- No `any` type (use `unknown` if needed)
- Explicit return types for functions

### Project Structure
```
frontend/
├── app/              # Next.js App Router pages
├── components/       # React components
│   ├── ui/          # shadcn/ui components
│   └── features/    # Feature-specific components
├── lib/             # Utilities, API clients
├── hooks/           # Custom React hooks
└── types/           # TypeScript type definitions
```

### Naming Conventions
- Files: `kebab-case.tsx` for components, `camelCase.ts` for utilities
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase` (prefix interfaces with `I` only if needed for clarity)

## Testing Standards

### Python Testing
- pytest for unit and integration tests
- Hypothesis for property-based tests
- pytest-asyncio for async tests
- pytest-cov for coverage reporting
- Minimum 80% code coverage required

### TypeScript Testing
- Jest for unit tests
- React Testing Library for component tests
- fast-check for property-based tests
- Minimum 80% code coverage required

### Test Structure
- Test files: `test_*.py` or `*.test.ts`
- One test file per source file
- Group related tests with `describe` blocks (TypeScript) or classes (Python)
- Use descriptive test names: `test_fraud_detection_returns_confidence_score`

### Property-Based Testing
- Tag all property tests with requirement IDs
- Minimum 100 iterations per property test
- Use deterministic seeds for reproducibility
- Document which correctness property is being tested

Example:
```python
@given(st.integers(min_value=0, max_value=100))
def test_property_1_fraud_confidence_bounds(health_score):
    """Property 1: Fraud Confidence Score Bounds
    Validates: Requirements 1.7
    """
    result = detect_fraud(health_score=health_score)
    assert 0 <= result.fraud_confidence <= 100
```

## Error Handling

### Python
- Use specific exception types (ValueError, TypeError, etc.)
- Create custom exceptions for domain errors
- Always include error context in exception messages
- Log all errors with structured logging (use `structlog`)
- Never use bare `except:` clauses

### TypeScript
- Use try-catch for async operations
- Return Result types for operations that can fail
- Display user-friendly error messages in UI
- Log errors to console in development, to monitoring service in production

## Database

### Schema Management
- Alembic for database migrations
- Never modify migrations after they're committed
- Include both upgrade and downgrade paths
- Test migrations on sample data before deploying

### Query Patterns
- Use SQLAlchemy ORM for all queries
- Eager load relationships to avoid N+1 queries
- Use database indexes for frequently queried columns
- Implement pagination for list endpoints (default page size: 20)

## API Conventions

### Endpoint Structure
- Version prefix: `/v1/`
- Resource-based URLs: `/v1/assessments`, `/v1/fraud/detect`
- Use plural nouns for collections
- Use HTTP methods correctly: GET (read), POST (create), PUT (update), DELETE (delete)

### Request/Response Format
- Accept and return JSON only
- Use camelCase for JSON keys (frontend) and snake_case internally (backend)
- Include metadata in responses (timestamp, request_id)
- Use ISO 8601 format for dates: `2026-04-05T10:30:00Z`

### Status Codes
- 200: Success
- 201: Created
- 400: Validation error
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 429: Rate limit exceeded
- 500: Internal server error

## Security

### Authentication
- JWT tokens with 30-day expiry
- Store tokens in httpOnly cookies (not localStorage)
- Implement token refresh mechanism
- Hash passwords with bcrypt (cost factor: 12)

### Authorization
- Implement role-based access control (RBAC)
- Check permissions at API boundary
- Use row-level security for multi-tenant data
- Log all authorization failures

### Data Protection
- Encrypt sensitive data at rest (AES-256)
- Use TLS 1.3 for all communications
- Hash PII (owner names, contact details) with SHA-256
- Never log sensitive data (passwords, tokens, PII)

## Performance

### Backend
- Use Redis for caching (TTL: 24 hours for base prices, 7 days for embeddings)
- Implement database connection pooling (min: 10, max: 20)
- Use async processing for long-running tasks (Celery/ARQ)
- Set request timeouts (default: 30 seconds)

### Frontend
- Use Next.js Image component for all images
- Implement code splitting for route-based chunks
- Lazy load components below the fold
- Use React.memo for expensive components
- Debounce search inputs (300ms)

## Git Workflow

### Commit Messages
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Reference requirement/task IDs: `feat: implement fraud detection (REQ-1.1)`
- Keep first line under 72 characters
- Add detailed description for complex changes

### Branch Naming
- Feature branches: `feature/fraud-detection`
- Bug fixes: `fix/photo-upload-error`
- Tasks: `task/phase-1-infrastructure`

### Code Review
- All code must be reviewed before merging
- Run tests and linting before requesting review
- Address all review comments before merging
- Squash commits when merging to main

## Documentation

### Code Documentation
- Document all public APIs with docstrings
- Include parameter types, return types, and examples
- Document complex algorithms with inline comments
- Keep comments up-to-date with code changes

### API Documentation
- Use FastAPI automatic OpenAPI generation
- Add detailed descriptions for all endpoints
- Include request/response examples
- Document error responses

## Dependencies

### Version Management
- Pin exact versions in requirements.txt and package.json
- Update dependencies monthly for security patches
- Test thoroughly after dependency updates
- Document breaking changes in CHANGELOG.md

### Allowed Dependencies
- Backend: FastAPI, SQLAlchemy, Pydantic, Celery, Redis, Hypothesis, pytest
- Frontend: Next.js, React, shadcn/ui, TailwindCSS, Supabase client, fast-check
- AI/ML: PaddleOCR, YOLOv8, Transformers (bge-m3), scikit-learn
- No proprietary or closed-source dependencies
