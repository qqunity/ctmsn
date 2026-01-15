from __future__ import annotations

from ctmsn.scenarios.time_process.runner import run


def main():
    for mode in ("sun", "prereq"):
        out = run(mode=mode)
        chk = out["check"]
        print("\n=== TIME PROCESS:", mode, "===")
        print("Derivation stats:", out["derivation"])
        print("Check ok:", chk.ok, "| violated:", chk.violated, "| unknown:", chk.unknown)
        print("forces(phi):", out["forces"].value)
        print("force(phi):", out["result"].status.value, "|", out["result"].explanation)
        print("Explain:")
        for line in out["explain"]:
            print("  -", line)


if __name__ == "__main__":
    main()
