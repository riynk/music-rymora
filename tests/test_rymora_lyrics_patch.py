import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "apply_rymora_lyrics.py"

class LyricsOverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        data = self.root / "app/src/main/java/com/ivor/ivormusic/data"
        data.mkdir(parents=True)
        (data / "LrcLine.kt").write_text(
            """internal data class ParsedLyrics(
    val lines: List<LrcLine>,
    val syncType: LyricsSyncType
)
data class Success(
        val provider: String,
        val syncType: LyricsSyncType
    ) : LyricsResult()""", encoding="utf-8")
        (data / "LyricsParser.kt").write_text(
            """return when {
            isTtml(normalized) -> parseTtml(normalized)""", encoding="utf-8")
        (data / "LocalLyricsSource.kt").write_text(
            '''val SIDECAR_EXTENSIONS = listOf("lrc", "ttml")
private fun ParsedLyrics.toResult(provider: String) = LyricsResult.Success(
        lines = lines,
        provider = provider,
        syncType = syncType
    )''', encoding="utf-8")
        (data / "LyricsRepository.kt").write_text(
            """private data class ProviderCandidate(
    val provider: RemoteLyricsProvider,
    val parsed: ParsedLyrics
) {
    fun toSuccess() = LyricsResult.Success(
        lines = parsed.lines,
        provider = provider.name,
        syncType = parsed.syncType
    )
}
val best = if (configuration.preferSynced) {
                stage.candidates.maxByOrNull { it.parsed.syncType.quality }
            } else stage.candidates.firstOrNull()
val best = candidates.sortedBy { providers.indexOf(it.provider) }.let { ordered ->
                    if (configuration.preferSynced) ordered.maxByOrNull { it.parsed.syncType.quality }
                    else ordered.firstOrNull()
                }""", encoding="utf-8")
        (data / "DownloadedAudioMetadata.kt").write_text(
            "private fun Long.toLrcTimestamp(): String {", encoding="utf-8")
        (data / "DownloadRepository.kt").write_text(
            '''?.toDownloadLyrics()
                            ?.takeIf(String::isNotBlank)
val name = storage.buildMusicCompanionFileName(
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
                            } ?: throw java.io.IOException("Could not write lyric storage entry")
artworkFile = artworkTemp,
                        lyrics = lyrics''', encoding="utf-8")
        self.data = data

    def tearDown(self):
        self.temp.cleanup()

    def run_patch(self):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root)], check=True, capture_output=True, text=True)

    def test_patch_applies_and_is_idempotent(self):
        self.run_patch()
        self.run_patch()
        model = (self.data / "LrcLine.kt").read_text()
        parser = (self.data / "LyricsParser.kt").read_text()
        local = (self.data / "LocalLyricsSource.kt").read_text()
        repo = (self.data / "LyricsRepository.kt").read_text()
        self.assertIn("enum class LyricsSourceFormat { TTML, OTHER }", model)
        self.assertIn("rawTtml = content", parser)
        self.assertIn("rawTtml: String? = null", model)
        self.assertIn('listOf("ttml", "lrc")', local)
        self.assertIn("sourceFormat == LyricsSourceFormat.TTML", repo)
        self.assertGreaterEqual(repo.count("sourceFormat == LyricsSourceFormat.TTML"), 4)
        self.assertIn("rawTtml = parsed.rawTtml", repo)
        self.assertIn("rawTtml = rawTtml", local)
        metadata = (self.data / "DownloadedAudioMetadata.kt").read_text()
        download = (self.data / "DownloadRepository.kt").read_text()
        self.assertIn('DownloadLyricsPayload("ttml", "application/ttml+xml", rawTtml)', metadata)
        self.assertIn("body.extension", download)
        self.assertIn("body.content", download)
        self.assertIn("lyrics?.content", download)
        kotlin_test = self.root / "app/src/test/java/com/ivor/ivormusic/data/RymoraTtmlPayloadTest.kt"
        self.assertTrue(kotlin_test.is_file())
        self.assertIn("preservesRawTtmlAsOfflineSidecar", kotlin_test.read_text())
        artwork = self.root / "app/src/main/java/com/ivor/ivormusic/ui/components/SongArtwork.kt"
        self.assertTrue(artwork.is_file())
        self.assertIn("readEmbeddedCover", artwork.read_text())
        self.assertIn("MediaMetadataRetriever", artwork.read_text())
        player = self.root / "app/src/main/java/com/ivor/ivormusic/ui/player/PlayerScreen.kt"
        self.assertTrue(player.is_file())
        player_text = player.read_text()
        self.assertIn("viewModel.toggleCurrentSongLike()", player_text)
        self.assertIn("verticalScroll(rememberScrollState())", player_text)
        self.assertIn("!it.filePath.isNullOrBlank()", player_text)
        self.assertIn("playbackFailures.collect", player_text)
        self.assertIn("SnackbarHost(snackbarHostState)", player_text)

    def test_fails_closed_when_upstream_anchor_changes(self):
        (self.data / "LyricsRepository.kt").write_text("upstream changed unexpectedly", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected one anchor", result.stderr)

if __name__ == "__main__":
    unittest.main()
