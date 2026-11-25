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
        """enum class LyricsSourceFormat { TTML, OTHER }

internal data class ParsedLyrics(
    val lines: List<LrcLine>,
    val syncType: LyricsSyncType,
    val sourceFormat: LyricsSourceFormat = LyricsSourceFormat.OTHER,
    val rawTtml: String? = null
)"""
    )

    replace_once(
        model,
        """        val provider: String,
        val syncType: LyricsSyncType
    ) : LyricsResult()""",
        """        val provider: String,
        val syncType: LyricsSyncType,
        val sourceFormat: LyricsSourceFormat = LyricsSourceFormat.OTHER,
        val rawTtml: String? = null
    ) : LyricsResult()"""
    )

    parser = base / "LyricsParser.kt"
    replace_once(
        parser,
        """return when {
            isTtml(normalized) -> parseTtml(normalized)""",
        """return when {
            isTtml(normalized) -> parseTtml(normalized)?.copy(sourceFormat = LyricsSourceFormat.TTML, rawTtml = content)"""
    )

    local = base / "LocalLyricsSource.kt"
    replace_once(
        local,
        'val SIDECAR_EXTENSIONS = listOf("lrc", "ttml")',
        'val SIDECAR_EXTENSIONS = listOf("ttml", "lrc")'
    )

    replace_once(
        local,
        """private fun ParsedLyrics.toResult(provider: String) = LyricsResult.Success(
        lines = lines,
        provider = provider,
        syncType = syncType
    )""",
        """private fun ParsedLyrics.toResult(provider: String) = LyricsResult.Success(
        lines = lines,
        provider = provider,
        syncType = syncType,
        sourceFormat = sourceFormat,
        rawTtml = rawTtml
    )"""
    )

    repo = base / "LyricsRepository.kt"
    replace_once(
        repo,
        """private data class ProviderCandidate(
    val provider: RemoteLyricsProvider,
    val parsed: ParsedLyrics
) {
    fun toSuccess() = LyricsResult.Success(
        lines = parsed.lines,
        provider = provider.name,
        syncType = parsed.syncType
    )
}""",
        """private data class ProviderCandidate(
    val provider: RemoteLyricsProvider,
    val parsed: ParsedLyrics
) {
    fun toSuccess() = LyricsResult.Success(
        lines = parsed.lines,
        provider = provider.name,
        syncType = parsed.syncType,
        sourceFormat = parsed.sourceFormat,
        rawTtml = parsed.rawTtml
    )
}"""
    )
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
    metadata = base / "DownloadedAudioMetadata.kt"
    download = base / "DownloadRepository.kt"
    replace_once(
        metadata,
        """private fun Long.toLrcTimestamp(): String {""",
        """internal data class DownloadLyricsPayload(
    val extension: String,
    val mimeType: String,
    val content: String
)

internal fun LyricsResult.Success.toDownloadLyricsPayload(): DownloadLyricsPayload =
    if (sourceFormat == LyricsSourceFormat.TTML && !rawTtml.isNullOrBlank()) {
        DownloadLyricsPayload("ttml", "application/ttml+xml", rawTtml)
    } else {
        DownloadLyricsPayload("lrc", "text/plain", toDownloadLyrics())
    }

private fun Long.toLrcTimestamp(): String {"""
    )
    replace_once(
        download,
        """?.toDownloadLyrics()
                            ?.takeIf(String::isNotBlank)""",
        """?.toDownloadLyricsPayload()
                            ?.takeIf { it.content.isNotBlank() }"""
    )
    replace_once(
        download,
        """val name = storage.buildMusicCompanionFileName(
                            request.title,
                            request.subtitle,
                            "lrc"
                        )
                        storage.createPendingMusicCompanion(
                            name,
                            "text/plain",
                            privateStorage
                        )?.also { target ->
                            pendingTargets += target
                            storage.openOutput(target)?.bufferedWriter(Charsets.UTF_8)?.use {
                                it.write(body)
                            } ?: throw java.io.IOException("Could not write lyric storage entry")""",
        """val name = storage.buildMusicCompanionFileName(
                            request.title,
                            request.subtitle,
                            body.extension
                        )
                        storage.createPendingMusicCompanion(
                            name,
                            body.mimeType,
                            privateStorage
                        )?.also { target ->
                            pendingTargets += target
                            storage.openOutput(target)?.bufferedWriter(Charsets.UTF_8)?.use {
                                it.write(body.content)
                            } ?: throw java.io.IOException("Could not write lyric storage entry")"""
    )
    replace_once(
        download,
        """artworkFile = artworkTemp,
                        lyrics = lyrics""",
        """artworkFile = artworkTemp,
                        lyrics = lyrics?.content"""
    )
    player_source = Path(__file__).resolve().parent.parent / "android/overlays/PlayerScreen.kt"
    player_target = root / "app/src/main/java/com/ivor/ivormusic/ui/player/PlayerScreen.kt"
    player_target.parent.mkdir(parents=True, exist_ok=True)
    player_target.write_text(player_source.read_text(encoding="utf-8"), encoding="utf-8")

    artwork_source = Path(__file__).resolve().parent.parent / "android/overlays/SongArtwork.kt"
    artwork_target = root / "app/src/main/java/com/ivor/ivormusic/ui/components/SongArtwork.kt"
    artwork_target.parent.mkdir(parents=True, exist_ok=True)
    artwork_target.write_text(artwork_source.read_text(encoding="utf-8"), encoding="utf-8")

    test_source = Path(__file__).resolve().parent.parent / "android/overlays/RymoraTtmlPayloadTest.kt"
    test_target = root / "app/src/test/java/com/ivor/ivormusic/data/RymoraTtmlPayloadTest.kt"
    test_target.parent.mkdir(parents=True, exist_ok=True)
    test_target.write_text(test_source.read_text(encoding="utf-8"), encoding="utf-8")

    print("Rymora TTML-first lyrics behavior applied.")
    print("TTML raw payload is retained and exported as a .ttml sidecar; LRC/plain fallback remains.")
    print("Local artwork now falls back to embedded cover extraction.")
    print("Now Playing favorite is persisted and its content scrolls on compact displays.")
    print("Priority: TTML source first, sync quality as tie-breaker; local TTML sidecar before LRC.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
