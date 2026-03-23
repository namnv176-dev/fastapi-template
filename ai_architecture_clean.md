# AI-Compatible Modular Monolith Architecture

## Project Structure

```
app/
├── core/
├── db/
│   ├── models/
│   └── session.py
│
├── repositories/
│   ├── base.py
│   ├── user_repo.py
│   └── research_repo.py
│
├── dependencies/
│   ├── db.py
│   └── providers.py
│
├── modules/
│   ├── user/
│   │   ├── api/
│   │   ├── services/
│   │   ├── access.py
│   │   └── schemas/
│   │
│   ├── research/
│   │   ├── api/
│   │   ├── services/
│   │   ├── access.py
│   │   └── schemas/
│
└── main.py
```

---

## Module Responsibilities

### API Layer
- Handle HTTP request/response
- Validate input/output using schemas
- Call service layer only

### Service Layer
- Contain business logic
- Control transaction (commit/rollback)
- Call repositories and access functions

### Repository Layer
- Perform database operations only
- Must receive DB session from service
- Must NOT commit or rollback

### Access Layer (cross-module)
- Provide controlled access to another module
- Must be simple and explicit
- Must NOT contain complex business logic

### Models (db/models)
- Centralized definition
- Each model has a single owner module
- Only owner module can modify model

---

## Rules

### Transaction
- Transaction is handled ONLY in service
- Repository must not commit or rollback

### Repository Usage
- Always pass `db` from service
- No session creation inside repository

### Cross-module Access
- Do NOT import other module services
- Do NOT call repository of another module for write
- Use access.py for interaction

### API Usage
- API must not call repository directly
- API must call service

### Dependency Injection
- Use for DB session and config only
- Do not control transaction in DI

---

## Implementation Examples

### Service with Transaction

```python
def create_order(self, db, data):
    try:
        self.user_repo.update_balance(db, data.user_id, data.amount)
        self.order_repo.create(db, data)
        db.commit()
    except Exception:
        db.rollback()
        raise
```

---

### Repository

```python
def create(db, data):
    db.add(data)
```

---

### Access Function

```python
# modules/user/access.py

def get_user_basic_info(db, user_id):
    return user_repo.get_basic(db, user_id)
```

---

### API

```python
@router.get("/")
def get_users(service: UserService, db):
    return service.get_users(db)
```
