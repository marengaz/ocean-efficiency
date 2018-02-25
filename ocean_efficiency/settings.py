
import atexit
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from ocean_efficiency.utils.sqlalchemy import setup_event_handlers


log = logging.getLogger(__name__)

# The SqlAlchemy connection string to the metadata database.
# SqlAlchemy supports many different database engine, more information
# their website
SQL_ALCHEMY_CONN = 'sqlite:////Users/benmarengo/code/oceanefficiency/oe.db'

# If SqlAlchemy should pool database connections.
SQL_ALCHEMY_POOL_ENABLED = True

# The SqlAlchemy pool size is the maximum number of database connections
# in the pool. 0 indicates no limit.
SQL_ALCHEMY_POOL_SIZE = 5

# The SqlAlchemy pool recycle is the number of seconds a connection
# can be idle in the pool before it is invalidated. This config does
# not apply to sqlite.
SQL_ALCHEMY_POOL_RECYCLE = 3600

# How many seconds to retry re-establishing a DB connection after
# disconnects. Setting this to 0 disables retries.
SQL_ALCHEMY_RECONNECT_TIMEOUT = 300

engine = None
Session = None


def configure_vars():
    global SQL_ALCHEMY_CONN


def configure_orm(disable_connection_pool=False):
    log.debug("Setting up DB connection pool (PID %s)" % os.getpid())
    global engine
    global Session
    engine_args = {}

    pool_connections = SQL_ALCHEMY_POOL_ENABLED
    if disable_connection_pool or not pool_connections:
        engine_args['poolclass'] = NullPool
    elif 'sqlite' not in SQL_ALCHEMY_CONN:
        # Engine args not supported by sqlite
        engine_args['pool_size'] = SQL_ALCHEMY_POOL_SIZE
        engine_args['pool_recycle'] = SQL_ALCHEMY_POOL_RECYCLE

    engine = create_engine(SQL_ALCHEMY_CONN, **engine_args)
    reconnect_timeout = SQL_ALCHEMY_RECONNECT_TIMEOUT
    setup_event_handlers(engine, reconnect_timeout)

    Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine))


def dispose_orm():
    """ Properly close pooled database connections """
    log.debug("Disposing DB connection pool (PID %s)", os.getpid())
    global engine
    global Session

    if Session:
        Session.remove()
        Session = None
    if engine:
        engine.dispose()
        engine = None


configure_vars()
configure_orm()

Base = declarative_base(bind=engine)
# Base.metadata.create_all(engine)

# Ensure we close DB connections at gunicon worker terminations
atexit.register(dispose_orm)

