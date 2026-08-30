import logging
import json
from dataclasses import asdict
from vara_scan import run_vara_scan, VaraConfig

# Setup logging to view scan output in real time
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

if __name__ == "__main__":
    # Configure Vara Scan parameters
    config = VaraConfig(
        keywords=[
            "AI", "compute", "GPU", "LLM", "inference", 
            "semiconductor", "sanctions", "Federal Reserve"
        ],
        sweep_depth_hours=12,
        active_planes=["tech", "economic", "geopolitical", "scientific"],
        scan_label="manual_live_scan_01"
    )

    print("=" * 60)
    print(f" Starting Vara Scan [{config.scan_label}]")
    print("=" * 60)

    # Trigger scan pipeline
    report = run_vara_scan(config)

    # Display Scan Summary
    print("\n" + "=" * 60)
    print(" SCAN SUMMARY")
    print("=" * 60)
    print(f"Scan ID       : {report.scan_id}")
    print(f"Timestamp     : {report.timestamp}")
    print(f"Active Planes : {', '.join(report.active_planes)}")
    print(f"Total Signals : {len(report.signals)}")
    print(f"Clusters      : {len(report.clusters)}")
    print(f"Null Result   : {report.null_result}")

    if report.signals:
        print("\n--- Top Sample Signals Passed to Vault ---")
        for i, sig in enumerate(report.signals[:5], 1):
            print(f"[{i}] [{sig.get('plane')}] {sig.get('title')[:60]}... (Novelty: {sig.get('novelty_score')})")

