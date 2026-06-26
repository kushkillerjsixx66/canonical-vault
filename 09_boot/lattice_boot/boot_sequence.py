from governance.stumpy.stumpy_engine import StumpyEngine
from runtime.veil.veil_interface import VeilInterface
from epistemic.vara.vara_interface import VaraInterface
from vara.scan_pipeline.vara_scan_pipeline import VaraScanPipeline
from vault_pipeline.vault_chain.vault_chain import VaultChain
from content_engine.field_intel_friday.field_intel_scheduler import FieldIntelScheduler


class LatticeBoot:
    """
    Canonical Lattice Boot Sequence.

    Responsibilities:
    - Start Stumpy
    - Wire Veil → Vara → Stumpy
    - Wire Vara Scan Pipeline → Vault Chain → Stumpy
    - Wire Field INTEL Friday Scheduler
    """

    def __init__(self):
        self.stumpy = None
        self.event_queue = None
        self.veil = None
        self.vara = None
        self.scan_pipeline = None
        self.chain = None
        self.scheduler = None

    def start(self):
        """
        Boot the full Lattice.
        """
        # Governance engine
        self.stumpy = StumpyEngine()
        self.stumpy.start()
        self.event_queue = self.stumpy.event_queue

        # Epistemic + runtime
        self.vara = VaraInterface(self.event_queue)
        self.veil = VeilInterface(self.event_queue, self.vara)

        # Vault + scan pipeline
        self.scan_pipeline = VaraScanPipeline(self.event_queue)
        self.chain = VaultChain()

        # Content cadence
        self.scheduler = FieldIntelScheduler(self.event_queue)

        return {
            "stumpy": self.stumpy,
            "veil": self.veil,
            "vara": self.vara,
            "scan_pipeline": self.scan_pipeline,
            "chain": self.chain,
            "scheduler": self.scheduler,
        }

    def stop(self):
        """
        Shut down the Lattice.
        """
        if self.stumpy:
            self.stumpy.stop()
