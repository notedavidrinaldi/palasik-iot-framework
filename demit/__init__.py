"""DEMIT Super App ecosystem."""

__all__ = ["DemitRuntime", "BaseDemitApp", "run"]

from demit.core.runtime import DemitRuntime
from demit.core.app import BaseDemitApp
from demit.main import run

__version__ = "0.0.1"
