# Import all models here so that app.database.Base.metadata knows about
# every table when we call Base.metadata.create_all() at startup.
from app.models.user import User, UserRole            # noqa: F401
from app.models.document import Document, DocumentStatus  # noqa: F401
from app.models.chat import ChatMessage                # noqa: F401
from app.models.unknown_question import UnknownQuestion  # noqa: F401
