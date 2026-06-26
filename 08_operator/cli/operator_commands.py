class OperatorCommands:
    """
    Canonical Operator Commands.

    Each command is a governed operator action.
    """

    def __init__(self, veil, vara, scan_pipeline, chain, stumpy, scheduler):
        self.veil = veil
        self.vara = vara
        self.scan_pipeline = scan_pipeline
        self.chain = chain
        self.stumpy = stumpy
        self.scheduler = scheduler

    # ------------------------------------------------------------------
    # COMMAND DISPATCH
    # ------------------------------------------------------------------

    def execute(self, cmd, identity, state, artifact, artifacts):
        if cmd == "runtime":
            self.runtime(identity, state)
        elif cmd == "scan":
            self.scan(artifact, identity, state)
        elif cmd == "lineage":
            self.lineage()
        elif cmd == "violations":
            self.violations()
        elif cmd == "intel":
            self.intel(artifacts, state)
        else:
            print(f"Unknown command: {cmd}")

    # ------------------------------------------------------------------
    # COMMAND IMPLEMENTATIONS
    # ------------------------------------------------------------------

    def runtime(self, identity, state):
        """
        Send a runtime update through Veil → Vara → Stumpy.
        """
        self.veil.submit_runtime_update(identity, state)
        print("Runtime update submitted.")

    def scan(self, artifact, identity, state):
        """
        Run Vara Scan Pipeline manually.
        """
        lineage = self.chain.load_all()
        result = self.scan_pipeline.run(artifact, lineage, state)
        print("Scan result:", result)

    def lineage(self):
        """
        Display lineage chain.
        """
        entries = self.chain.load_all()
        for e in entries:
            print(e)

    def violations(self):
        """
        Display governance violations.
        """
        violations = self.stumpy.get_violations()
        for v in violations:
            print(v)

    def intel(self, artifacts, state):
        """
        Run Field INTEL Friday scheduler.
        """
        path = self.scheduler.run(artifacts, state)
        print("Field INTEL Friday report stored at:", path)
