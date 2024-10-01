from datetime import datetime, timezone
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute


class Persona(Model):
    class Meta:
        table_name = "Personas"

    name = UnicodeAttribute(hash_key=True)
    description = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default_for_new=datetime.now(timezone.utc))
