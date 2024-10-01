from datetime import datetime, timezone
from pynamodb.models import Model
from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)


class RubricDimension(MapAttribute):
    name = UnicodeAttribute()
    description = UnicodeAttribute()
    weight = NumberAttribute()


class Rubric(Model):
    class Meta:
        table_name = "Rubrics"

    name = UnicodeAttribute(hash_key=True)
    description = UnicodeAttribute(null=True)
    created_at = UTCDateTimeAttribute(default_for_new=datetime.now(timezone.utc))
    dimensions = ListAttribute(of=RubricDimension)
