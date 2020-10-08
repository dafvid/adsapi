import logging
import os
import uuid

from sqlalchemy import create_engine, Integer, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR

Base = declarative_base()

_log = logging.getLogger('budgetweb.db')
_log.setLevel(logging.DEBUG)


# Borrowed from
# https://gist.github.com/gmolveau/7caeeefe637679005a7bb9ae1b5e421e
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class DB:
    def __init__(self, path='ads_database.db', echo=False):
        self._path = path
        self._abspath = os.path.abspath(self._path)
        _log.info("Opening database {}".format(self._abspath))
        self._engine = create_engine(
            'sqlite+pysqlite:///{}'.format(self._path), echo=echo)
        self._sm = sessionmaker(self._engine)

    def exists(self):
        return os.path.exists(self._path)

    def create(self):
        print('Create new database {}'.format(self._abspath))
        Base.metadata.create_all(self._engine)

    def get_session(self):
        return self._sm()


class Ad(Base):
    __tablename__ = 'ad'

    id = Column(Integer, primary_key=True)
    uuid = Column(GUID, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    price = Column(Float)
