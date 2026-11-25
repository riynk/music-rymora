# Rymora overlay patches

Rymora does not fork or copy the complete upstream tree into this repository yet. `scripts/apply_rymora_branding.py` applies a minimal, deterministic set of local overlay edits to the checked-out Koda submodule:

- Android application ID becomes `com.riynk.rymora`.
- App label and debug label become Rymora.
- App version starts at `0.1.0-alpha01`.
- GitHub update metadata points to `riynk/music-rymora`.
- Default accent palette becomes Rymora coral/pink/mint.
- Background and surface colors align with the Rymora palette.

The script is idempotent and fails clearly if upstream changes invalidate an expected replacement. Review the upstream diff before updating the pinned submodule commit.

Run it through `bash scripts/bootstrap-android.sh` from the repository root.
