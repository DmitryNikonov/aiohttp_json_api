import logging

from boltons.typeutils import issubclass

from .const import JSONAPI
from .handlers import *
from .middleware import jsonapi_middleware
from .registry import Registry
from .schema.schema import Schema

logger = logging.getLogger(__name__)


def setup_jsonapi(app, schemas, *, base_path='/api', version='1.0.0',
                  api_version=None, meta=None):
    default_meta = {
        'api-version': api_version
    }
    base = {
        'version': version,
        'meta': meta or default_meta
    }
    schema_by_type = {}
    schema_by_resource = {}

    for schema_cls in schemas:
        assert issubclass(schema_cls, Schema), \
            f'Schema class is required. Got: {schema_cls}'

        schema = schema_cls(app)
        schema_by_type[schema.type] = schema
        if schema.resource_class is None:
            logger.warning(
                'The schema "%s" is not bound to a resource class.',
                schema.type
            )
        else:
            schema_by_resource[schema.resource_class] = schema

    app[JSONAPI] = Registry(base=base,
                            schema_by_type=schema_by_type,
                            schema_by_resource=schema_by_resource)

    collection_resource = app.router.add_resource(
        f'{base_path}/{{type}}',
        name='jsonapi.collection'
    )
    resource_resource = app.router.add_resource(
        f'{base_path}/{{type}}/{{id}}',
        name='jsonapi.resource'
    )
    relationships_resource = app.router.add_resource(
        f'{base_path}/{{type}}/{{id}}/relationships/{{relation}}',
        name='jsonapi.relationships'
    )
    related_resource = app.router.add_resource(
        f'{base_path}/{{type}}/{{id}}/{{relation}}',
        name='jsonapi.related'
    )

    collection_resource.add_route('GET', get_collection)
    collection_resource.add_route('POST', post_resource)
    resource_resource.add_route('GET', get_resource)
    resource_resource.add_route('PATCH', patch_resource)
    resource_resource.add_route('DELETE', delete_resource)
    relationships_resource.add_route('GET', get_relationship)
    relationships_resource.add_route('POST', post_relationship)
    relationships_resource.add_route('PATCH', patch_relationship)
    relationships_resource.add_route('DELETE', delete_relationship)
    related_resource.add_route('GET', get_related)

    app.middlewares.append(jsonapi_middleware)

    return app
