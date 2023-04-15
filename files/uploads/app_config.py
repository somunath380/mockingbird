"""Different confiurations for the app."""

import logging
from logging.config import dictConfig

import newrelic.agent
import sentry_sdk
from sentry_sdk import configure_scope
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sanic import SanicIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from config import current_config
from constants.common_constants import (
    BASE_DIR,
    GITSHA_FILE_NAME,
    NEW_RELIC_ENVIRONMENTS,
    PROJECT_NAME,
    SERVER_MODE,
)


logger = logging.getLogger(__file__)


def config_app(app):
    """Configure keepalive."""
    app.config.KEEP_ALIVE = False


def config_logs():
    """Configure log settings."""
    LOG_SETTINGS = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "[%(levelname)s] %(name)s "
                "%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                "datefmt": "%H:%M:%S",
            }
        },
    }
    dictConfig(LOG_SETTINGS)


def config_sentry():
    """Confgiure Sentry."""
    if current_config.ENABLE_SENTRY:
        with open(BASE_DIR + GITSHA_FILE_NAME, "r") as file:
            gitsha = file.readline()
        release = "{}.{}".format(PROJECT_NAME, gitsha)

        sentry_logging = LoggingIntegration(
            level=logging.ERROR, event_level=logging.ERROR
        )
        if current_config.MODE == SERVER_MODE:
            sentry_sdk.init(
                dsn=current_config.SENTRY_DSN,
                environment=current_config.SENTRY_ENVIRONMENT,
                integrations=[
                    SanicIntegration(),
                    AioHttpIntegration(),
                    RedisIntegration(),
                    SqlalchemyIntegration(),
                    sentry_logging,
                ],
                release=release,
            )
        else:
            sentry_sdk.init(
                dsn=current_config.SENTRY_DSN,
                environment=current_config.SENTRY_ENVIRONMENT,
                integrations=[
                    AioHttpIntegration(),
                    RedisIntegration(),
                    SqlalchemyIntegration(),
                    sentry_logging,
                ],
                release=release,
            )
        with configure_scope() as scope:
            scope.set_tag("MODE", current_config.MODE)


def config_new_relic():
    """Configure New Relic."""
    if current_config.ENV in NEW_RELIC_ENVIRONMENTS:
        newrelic.agent.initialize()
