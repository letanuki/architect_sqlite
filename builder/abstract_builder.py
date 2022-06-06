# coding: utf-8
from abc import abstractmethod
from typing import Optional

from __version__ import __VERSION__


class AbstractBuilder:
    """Abstract script builder, do not create object with this class!

    :var AbstractBuilder.EXT: file extension
    :var AbstractBuilder.PRETTY_NAME: a pretty name use to find the builder
    :var AbstractBuilder.COMMENT: line comment char

    """
    EXT = ""
    PRETTY_NAME = ""
    COMMENT = ""

    @classmethod
    @abstractmethod
    def dump(cls, datas) -> Optional[str]:
        """Generate script

        :param datas: datas used to build the script.
        :type datas: Any
        :return: script as string
        :rtype: str
        """
        pass

    @classmethod
    def get_dump_filepath(cls, filepath: str) -> str:
        """Return filename with extension"""
        return f"{filepath}{cls.EXT}"

    @classmethod
    def generate_header(cls):
        """Generate script header with information sucha as tool version.

        ..note :: we did note add date to avoid git commit if the file has not been modified
        """
        return f"""{cls.COMMENT} Build with architectSQLite v{__VERSION__}
{cls.COMMENT}A bullb_ull's lazy tool"""