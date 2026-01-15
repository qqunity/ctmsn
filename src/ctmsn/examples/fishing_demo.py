from __future__ import annotations

from ctmsn.scenarios.fishing.runner import run


def main():
    out = run()
    chk = out["check"]

    print("\n=== FISHING (4.14) canonical ===")
    print("Derivation:", out["derivation"])
    print("Check ok:", chk.ok, "| violated:", chk.violated, "| unknown:", chk.unknown)
    print("forces(phi):", out["forces"].value)
    print("force(phi):", out["result"].status.value, "|", out["result"].explanation)

    print("\nExplain:")
    for line in out["explain"]:
        print("  -", line)


if __name__ == "__main__":
    main()
