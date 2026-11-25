#!/usr/bin/env python3
"""Apply Rymora's lyrics behavior to the pinned Koda checkout.

The patch is intentionally anchor-based and fails closed if upstream changes.
It is idempotent and does not rewrite unrelated source.
"""
from pathlib import Path
import sys

def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: apply_rymora_lyrics.py <koda-submodule-path>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    base = root / "app/src/main/java/com/ivor/ivormusic/data"
    if not (base / "LyricsParser.kt").is_file():
        raise SystemExit(f"Not a Koda lyrics source tree: {root}")

    model = base / "LrcLine.kt"
    replace_once(
        model,
        """internal data class ParsedLyrics(
    val lines: List<LrcLine>,
    val syncType: LyricsSyncType
)""",
        """internal enum class LyricsSourceFormat { TTML, OTHER }

internal data class ParsedLyrics(
    val lines: List<LrcLine>,
    val syncType: LyricsSyncType,
    val sourceFormat: LyricsSourceFormat = LyricsSourceFormat.OTHER
)"""
    )

    parser = base / "LyricsParser.kt"
    replace_once(
        parser,
        """return when {
            isTtml(normalized) -> parseTtml(normalized)""",
        """return when {
            isTtml(normalized) -> parseTtml(normalized)?.copy(sourceFormat = LyricsSourceFormat.TTML)"""
    )

    local = base / "LocalLyricsSource.kt"
    replace_once(
        local,
        'val SIDECAR_EXTENSIONS = listOf("lrc", "ttml")',
        'val SIDECAR_EXTENSIONS = listOf("ttml", "lrc")'
    )

    repo = base / "LyricsRepository.kt"
    replace_once(
        repo,
        """val best = if (configuration.preferSynced) {
                stage.candidates.maxByOrNull { it.parsed.syncType.quality }
            } else stage.candidates.firstOrNull()""",
        """val best = if (configuration.preferSynced) {
                stage.candidates.maxByOrNull { candidate ->
                    (if (candidate.parsed.sourceFormat == LyricsSourceFormat.TTML) 100 else 0) +
                        candidate.parsed.syncType.quality
                }
            } else stage.candidates.firstOrNull { it.parsed.sourceFormat == LyricsSourceFormat.TTML }
                ?: stage.candidates.firstOrNull()"""
    )
    replace_once(
        repo,
        """val best = candidates.sortedBy { providers.indexOf(it.provider) }.let { ordered ->
                    if (configuration.preferSynced) ordered.maxByOrNull { it.parsed.syncType.quality }
                    else ordered.firstOrNull()
                }""",
        """val best = candidates.sortedBy { providers.indexOf(it.provider) }.let { ordered ->
                    if (configuration.preferSynced) ordered.maxByOrNull { candidate ->
                        (if (candidate.parsed.sourceFormat == LyricsSourceFormat.TTML) 100 else 0) +
                            candidate.parsed.syncType.quality
                    } else ordered.firstOrNull { it.parsed.sourceFormat == LyricsSourceFormat.TTML }
                        ?: ordered.firstOrNull()
                }"""
    )
    print("Rymora TTML-first lyrics behavior applied.")
    print("Priority: TTML source first, sync quality as tie-breaker; local TTML sidecar before LRC.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
