from __future__ import annotations

from ctmsn.scenarios.fast_smith.runner import run


def main():
    out = run()
    chk = out["check"]
    print("Initial ctx:", out["ctx0"])
    print("Check ok:", chk.ok)
    print("Violated:", chk.violated)
    print("Unknown:", chk.unknown)
    print("forces(phi):", out["forces"].value)
    print("force(phi):", out["result"].status.value, "|", out["result"].explanation)


if __name__ == "__main__":
    main()
