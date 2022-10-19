""" .. include::../docs/utils.md
"""
import logging

from lxml import etree
from collections import defaultdict

logger = logging.getLogger(__name__)

_LABEL_TAGS = {'Label', 'Choice'}
_NOT_CONTROL_TAGS = {'Filter', }
