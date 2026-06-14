# DRINKOO Testing Documentation

Username: testuser
Password: password123

## Overview

Comprehensive test suite for the DRINKOO RAG chatbot application covering:

- Authentication (signup, login, password hashing)
- API Integration (all endpoints)
- Database integrity (schema, constraints, relationships)
- RAG Evaluation (Text2SQL validation, grounding)

## Test Files

### test_auth.py

Unit tests for authentication module:

- Password hashing and verification
- JWT token creation and validation
- User creation and authentication
- User existence checking

**Run:** `pytest Tests/test_auth.py -v`

### test_api_integration.py

Integration tests for FastAPI endpoints:

- Health check endpoints (`/health`, `/status`, `/version`)
- Authentication endpoints (`/auth/signup`, `/auth/login`, `/auth/logout`)
- Chatbot endpoint (`/chatbot/ask`, `/chatbot/history`)
- File upload endpoint (`/upload/image`)

**Run:** `pytest Tests/test_api_integration.py -v`

### test_database.py

Database integrity tests:

- Schema verification (all tables present)
- Foreign key constraints
- Data constraints (unit volume CHECK, unique constraints)
- Cascade delete behavior
- Seed data integrity
- SKU uniqueness

**Run:** `pytest Tests/test_database.py -v`

### test_rag_evaluation.py

RAG pipeline evaluation tests:

- Text retrieval accuracy
- RAG context formation
- Text2SQL validation (10 queries, ≥90% target)
- Faithfulness testing (≥0.85 target)
- Context relevance testing (>0.7 target)

**Run:** `pytest Tests/test_rag_evaluation.py -v`

## Running All Tests

### Full test suite with coverage:

```bash
pytest Tests/ -v --cov=backend --cov-report=html --cov-report=term
```

### Quick test without coverage:

```bash
pytest Tests/ -v
```

### Run specific test file:

```bash
pytest Tests/test_auth.py -v
```

### Run specific test class:

```bash
pytest Tests/test_auth.py::TestPasswordHashing -v
```

### Run specific test:

```bash
pytest Tests/test_auth.py::TestPasswordHashing::test_hash_password -v
```

## Test Coverage Targets

- **Authentication**: 95%+ coverage
- **API Endpoints**: 90%+ coverage
- **Database**: 100% schema coverage
- **RAG Pipeline**: 85%+ coverage

## Text2SQL Validation

The test suite includes 10 sample natural language queries with SQL validation:

1. **Product Lookup** - "What orange juice products do we have?"
2. **Ingredient Join** - "Which products contain strawberry?"
3. **Category Filter** - "What are all sparkling drinks?"
4. **Price Lookup** - "How much does Orange Splash cost?"
5. **Volume Comparison** - "Show me products under 300ml"
6. **Multi-table Join** - "What ingredients are in Berry Fizz?"
7. **Allergen Subquery** - "Which products are allergen-free?"
8. **Article Retrieval** - "Tell me about storage instructions"
9. **Sorting** - "List all products with prices sorted by cost"
10. **LIKE Search** - "Which products have coconut as ingredient?"

**Target:** ≥90% correctness

## RAG Evaluation Metrics

### Faithfulness (Target: ≥0.85)

- Measures factual consistency with source data
- Validates that generated responses match database content
- Tested on product facts, ingredients, and support articles

### Context Relevance (Target: >0.7)

- Measures relevance of retrieved documents to query
- Uses keyword matching and semantic relevance
- Validated across diverse query types

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
- name: Run tests
  run: pytest Tests/ -v --cov=backend --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Known Test Limitations

1. **Seed Data Dependency** - Tests depend on database being initialized with seed data
2. **Integration Tests** - Use TestClient which runs endpoints in-process (no network)
3. **LLM Integration** - OpenRouter API tests are mocked; full integration requires live API key
4. **Time-sensitive Tests** - JWT expiration tests may fail if clock skew exceeds token lifetime

## Troubleshooting

### Database locked error

```
sqlite3.OperationalError: database is locked
```

Solution: Ensure no other processes have the database open. Try resetting:

```bash
python scripts/load_data.py
```

### Import errors

```
ModuleNotFoundError: No module named 'backend'
```

Solution: Run tests from project root:

```bash
cd /path/to/assignment
pytest Tests/
```

### Token verification failures

```
AssertionError: token_data is None
```

Solution: Verify SECRET_KEY in config.py is consistent. JWT tests are sensitive to configuration changes.

## Coverage Report

After running tests, view the coverage report:

```bash
# Terminal report
pytest Tests/ --cov=backend --cov-report=term-missing

# HTML report
pytest Tests/ --cov=backend --cov-report=html
open htmlcov/index.html
```

## Performance Benchmarks

- **Auth Tests**: ~100ms total
- **API Integration Tests**: ~500ms total
- **Database Tests**: ~200ms total
- **RAG Evaluation Tests**: ~300ms total

**Total Test Suite**: ~1-2 seconds

## Future Test Enhancements

1. Performance/load testing with locust
2. Semantic similarity testing for RAG context
3. End-to-end Selenium tests for frontend
4. Database migration tests
5. Security penetration tests
6. Concurrency/race condition tests
