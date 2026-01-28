# palasik/core/plugin.py

from abc import ABC, abstractmethod

class PalasikPlugin(ABC):
    """
    Kontrak dasar untuk seluruh plugin PALASIK.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Nama unik plugin.
        """
        pass

    @abstractmethod
    def version(self) -> str:
        """
        Versi plugin.
        """
        pass

    @abstractmethod
    def on_start(self, context):
        """
        Dipanggil saat agent mulai.
        """
        pass

    @abstractmethod
    def on_event(self, event: dict, context):
        """
        Dipanggil saat event diterima.
        """
        pass

    @abstractmethod
    def on_stop(self, context):
        """
        Dipanggil saat agent berhenti.
        """
        pass
