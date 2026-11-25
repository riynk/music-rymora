package com.ivor.ivormusic.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class RymoraTtmlPayloadTest {
    @Test
    fun preservesRawTtmlAsOfflineSidecar() {
        val raw = """<?xml version="1.0"?><tt><body><p begin="1s">Original lyric</p></body></tt>"""
        val result = LyricsResult.Success(
            lines = listOf(LrcLine(1_000L, "Original lyric")),
            provider = "fixture",
            syncType = LyricsSyncType.LINE,
            sourceFormat = LyricsSourceFormat.TTML,
            rawTtml = raw
        )

        val payload = result.toDownloadLyricsPayload()

        assertEquals("ttml", payload.extension)
        assertEquals("application/ttml+xml", payload.mimeType)
        assertEquals(raw, payload.content)
    }

    @Test
    fun parserRetainsOriginalTtmlPayload() {
        val raw = """<tt><body><div><p begin="00:00:01.000">Original lyric</p></div></body></tt>"""
        val parsed = LyricsParser.parse(raw)

        assertEquals(LyricsSourceFormat.TTML, parsed?.sourceFormat)
        assertEquals(raw, parsed?.rawTtml)
        assertEquals("Original lyric", parsed?.lines?.single()?.text)
    }

    @Test
    fun lrcFallbackStillSerializesTimedLines() {
        val result = LyricsResult.Success(
            lines = listOf(LrcLine(1_230L, "Fallback line")),
            provider = "fixture",
            syncType = LyricsSyncType.LINE
        )

        val payload = result.toDownloadLyricsPayload()

        assertEquals("lrc", payload.extension)
        assertEquals("text/plain", payload.mimeType)
        assertTrue(payload.content.contains("[00:01.23]Fallback line"))
    }
}
