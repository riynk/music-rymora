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
)""", encoding="utf-8")
        (data / "LyricsParser.kt").write_text(
            """return when {
            isTtml(normalized) -> parseTtml(normalized)""", encoding="utf-8")
        (data / "LocalLyricsSource.kt").write_text(
            'val SIDECAR_EXTENSIONS = listOf("lrc", "ttml")', encoding="utf-8")
        (data / "LyricsRepository.kt").write_text(
            """val best = if (configuration.preferSynced) {
                stage.candidates.maxByOrNull { it.parsed.syncType.quality }
            } else stage.candidates.firstOrNull()
val best = candidates.sortedBy { providers.indexOf(it.provider) }.let { ordered ->
                    if (configuration.preferSynced) ordered.maxByOrNull { it.parsed.syncType.quality }
                    else ordered.firstOrNull()
                }""", encoding="utf-8")
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
        self.assertIn("copy(sourceFormat = LyricsSourceFormat.TTML)", parser)
        self.assertIn('listOf("ttml", "lrc")', local)
        self.assertIn("sourceFormat == LyricsSourceFormat.TTML", repo)
        self.assertEqual(repo.count("sourceFormat == LyricsSourceFormat.TTML"), 2)

    def test_fails_closed_when_upstream_anchor_changes(self):
        (self.data / "LyricsRepository.kt").write_text("upstream changed unexpectedly", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected one anchor", result.stderr)

if __name__ == "__main__":
    unittest.main()
