"""Use this file to add models which don't fall under any other category."""

from lib.models.db import Base
from sqlalchemy import Column, String, Text

import uuid


class Setting(Base):
    """Should mostly be used as a key-value store.

    May evolve in the future.
    """

    __tablename__ = 'setting'
    id = Column(String(36), primary_key=True)

    section = Column(String(36), nullable=False)
    option = Column(String(36), nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    def __init__(self, section='', option='', value='', description=''):
        self.id = str(uuid.uuid4())
        self.section = section
        self.option = option
        self.value = value
        self.description = description

    @staticmethod
    def get_value_by_section_option(section, option, cast=None, as_bool=False):
        setting = (Setting
                   .query
                   .filter(Setting.section == section)
                   .filter(Setting.option == option)
                   .first())
        if setting is None:
            value = ''
        else:
            value = setting.value

        if as_bool:
            return bool(value)
        elif cast is not None:
            return cast(value)
        else:
            return value
