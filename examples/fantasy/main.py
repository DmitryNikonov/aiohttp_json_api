#!/usr/bin/env python
"""Simple JSON API application example with in-memory storage."""

import asyncio
import os
import logging

import time
from aiohttp import web
from aiopg.sa import create_engine

from aiohttp_json_api import setup_jsonapi


async def close_db_connections(app):
    app['db'].close()
    await app['db'].wait_closed()


async def init(db_dsn: str, debug=False, loop=None) -> web.Application:
    from examples.fantasy.schemas import (
        AuthorSchema, BookSchema, ChapterSchema,
        PhotoSchema, StoreSchema, SeriesSchema
    )
    from examples.fantasy.controllers import (
        CommonController, BooksController
    )

    app = web.Application(debug=debug, loop=loop)
    engine = await create_engine(dsn=db_dsn, echo=debug)
    app['db'] = engine
    app.on_cleanup.append(close_db_connections)

    # Note that we pass schema classes, not instances of them.
    # Schemas instances will be initialized application-wide.
    # Schema instance is stateless, therefore any request state must be passed
    # to each of Schema's method as JSONAPIContext instance.
    # JSONAPIContext instance created automatically in JSON API middleware
    # for each request. JSON API handlers use it in calls of Schema's methods.
    setup_jsonapi(
        app,
        {
            AuthorSchema: CommonController,
            BookSchema: BooksController,
            ChapterSchema: CommonController,
            PhotoSchema: CommonController,
            StoreSchema: CommonController,
            SeriesSchema: CommonController
        },
        log_errors=debug, meta={'fantasy': {'version': '0.0.1'}}
    )

    return app


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s [%(asctime)s.%(msecs)03d] '
               '(%(name)s): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.Formatter.converter = time.gmtime

    dsn = os.getenv('EXAMPLE_DSN',
                    'postgresql://example:somepassword@localhost/example')
    port = os.getenv('EXAMPLE_PORT', 8082)

    app = asyncio.get_event_loop().run_until_complete(init(dsn, debug=True))

    # More useful log format than default
    log_format = '%a (%{X-Real-IP}i) %t "%r" %s %b %Tf ' \
                 '"%{Referrer}i" "%{User-Agent}i"'
    web.run_app(app, port=port, access_log_format=log_format)


if __name__ == '__main__':
    main()
