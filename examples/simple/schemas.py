from aiohttp_json_api.schema import BaseSchema, fields, relationships

from .models import Article, Comment, People


class SchemaWithStorage(BaseSchema):
    @property
    def storage(self):
        return self.app['storage'][self.resource_class.__name__]

    async def query_collection(self, context, **kwargs):
        return self.storage

    async def query_resource(self, resource_id, context, **kwargs):
        return self.storage.get(resource_id)


class PeopleSchema(SchemaWithStorage):
    type = 'people'
    resource_class = People

    first_name = fields.String()
    last_name = fields.String(allow_blank=True)
    twitter = fields.String(allow_none=True)

    async def fetch_resource(self, resource_id, context, **kwargs):
        pass

    async def delete_resource(self, resource_id, context, **kwargs):
        pass


class CommentSchema(SchemaWithStorage):
    resource_class = Comment

    body = fields.String()
    author = relationships.ToOne(foreign_types=(PeopleSchema.type,))

    async def fetch_resource(self, resource_id, context, **kwargs):
        pass

    async def delete_resource(self, resource_id, context, **kwargs):
        pass


class ArticleSchema(SchemaWithStorage):
    resource_class = Article

    title = fields.String()
    author = relationships.ToOne(foreign_types=(PeopleSchema.type,))
    comments = relationships.ToMany(foreign_types=(CommentSchema.type,))

    async def fetch_resource(self, resource_id, context, **kwargs):
        pass

    async def delete_resource(self, resource_id, context, **kwargs):
        pass
