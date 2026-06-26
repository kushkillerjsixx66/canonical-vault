import argparse
import json

from governance.stumpy.stumpy_engine import StumpyEngine
from runtime.veil.veil_interface import VeilInterface
from epistemic.vara.vara_interface import VaraInterface
from vara.scan_pipeline.vara_scan_pipeline import VaraScanPipeline
from vault_pipeline.vault_chain.vault_chain import VaultChain
from content_engine.field_intel_friday.field_intel_scheduler import FieldIntelScheduler

from .operator_commands import OperatorCommands


class OperatorCLI:
    """
    Canonical Operator CLI.

    Provides commands for:
    - runtime updates
    - triggering scans
    - viewing lineage
    - generating Field INTEL Friday reports
    - viewing governance violations
    """

    def __init__(self):
        self.stumpy = StumpyEngine()
        self.stumpy.start()

        self.event_queue = self.stumpy.event_queue
        self.vara = VaraInterface(self.event_queue)
        self.veil = VeilInterface(self.event_queue, self.vara)
        self.scan_pipeline = VaraScanPipeline(self.event_queue)
        self.chain = VaultChain()
        self.scheduler = FieldIntelScheduler(self.event_queue)

        self.commands = OperatorCommands(
            veil=self.veil,
            vara=self.vara,
            scan_pipeline=self.scan_pipeline,
            chain=self.chain,
            stumpy=self.stumpy,
            scheduler=self.scheduler,
        )

    def run(self):
        parser = argparse.ArgumentParser(description="Operator CLI")
        parser.add_argument("command", help="Command to execute")
        parser.add_argument("--identity", help="JSON identity dict")
        parser.add_argument("--state", help="JSON runtime state")
        parser.add_argument("--artifact", help="JSON artifact")
        parser.add_argument("--artifacts", help="JSON list of artifacts")

        args = parser.parse_args()

        cmd = args.command

        identity = json.loads(args.identity) if args.identity else None
        state = json.loads(args.state) if args.state else None
        artifact = json.loads(args.artifact) if args.artifact else None
        artifacts = json.loads(args.artifacts) if args.artifacts else None

        self.commands.execute(cmd, identity, state, artifact, artifacts)
