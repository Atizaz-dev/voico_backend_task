# Central import of all SQLModel ORM models.
# Alembic and the application import this module to ensure all models
# are registered with SQLModel's metadata before migrations run.

from app.modules.calls.schema import Call  # noqa: F401
