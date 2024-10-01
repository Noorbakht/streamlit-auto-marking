from datetime import datetime, timezone
from uuid import uuid4
from pynamodb.models import Model
from pynamodb.attributes import (
    JSONAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)


class Submission(Model):
    class Meta:
        table_name = "Submissions"

    id = UnicodeAttribute(hash_key=True, default=lambda: str(uuid4()))
    author = UnicodeAttribute()
    content = UnicodeAttribute()
    title = UnicodeAttribute()
    status = UnicodeAttribute(default_for_new="Reviewing")
    assessment = JSONAttribute(null=True)
    created_at = UTCDateTimeAttribute(default_for_new=datetime.now(timezone.utc))
    checkbox = False
