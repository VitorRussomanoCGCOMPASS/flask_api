from marshmallow import RAISE, post_load, pre_load, EXCLUDE


from flask_api.models.indexes import Indexes, IndexValues
from flask_api.schemas.base_schema import CustomSchema
from marshmallow_sqlalchemy.fields import Nested


class IndexesSchema(CustomSchema):
    class Meta:
        model = Indexes
        unknown = RAISE
        load_instance = True


class IndexValuesSchema(CustomSchema):
    class Meta:
        model = IndexValues
        unknown = RAISE
        dateformat = "%Y-%m-%d"
        load_instance = True
        load_relationships = True

    index = Nested(IndexesSchema)


class CDIValueSchema(IndexValuesSchema):
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def pre_loader(self, data, many, **kwargs):
        data["date"] = data["date"].rpartition("T")[0]
        return data
