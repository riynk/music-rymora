# Upstream source register

Rymora reuses existing projects and libraries wherever appropriate. Every imported source must be pinned and its license retained.

## 1. Android application foundation — Koda

- Source: https://github.com/Ivorisnoob/Koda
- Pinned branch: `beta`
- Pinned commit: `5a97eccd7702e5aec6f9a443b31077a94e1bd303`
- License: GPL-3.0
- Integrated at: `android/vendor/koda` Git submodule

Why it is the base:
- One Android app already combines YouTube Music-style music discovery/playback with a separate video experience.
- It includes a local music library, offline cache, audio/video download queue and playlist downloads.
- Its lyric pipeline has multiple providers, a TTML-capable parser, local `.ttml`/`.lrc` sidecars and embedded lyrics.
- It already uses jaudiotagger for reading embedded lyrics and writing title/artist/album/artwork/lyrics to completed downloads.
- The UI is Jetpack Compose and playback uses Android Media3.

Relevant upstream code inspected at the pin:
- `app/src/main/java/com/ivor/ivormusic/data/LyricsParser.kt` — TTML, QRC, LRC/enhanced LRC and plain-text parsing.
- `data/LyricsConfiguration.kt` and `data/LyricsProviders.kt` — provider registry/order and remote provider adapters.
- `data/LyricsRepository.kt` — local-first lookup and remote provider fallback.
- `data/LocalLyricsSource.kt` — local `.ttml`/`.lrc` sidecars and embedded lyrics.
- `ui/player/PlayerSheetContent.kt` — player panel defaults to Up Next; Lyrics is a separate tab.
- `data/DownloadedAudioMetadata.kt` — writes tags, artwork and lyric data to downloaded audio.
- `gradle/libs.versions.toml` — includes jaudiotagger 3.0.1.

Important behavior: the upstream can prefetch lyrics when the track changes, but the normal player panel starts on **Up Next**. Rymora must preserve the visible behavior: lyric text never takes over the player or opens by itself; the user taps Lyrics to show it.

## 2. yt-dlp Android runtime — candidate integration

- Android implementation reference: https://github.com/deniscerri/ytdlnis
- Android wrapper/library reference: https://github.com/yausername/youtubedl-android
- yt-dlp source: https://github.com/yt-dlp/yt-dlp

YTDLnis demonstrates a mature Android yt-dlp workflow with Python/runtime packages, queueing, playlist downloads, audio/video options, FFmpeg and JavaScript challenge runtimes. The youtubedl-android project provides a Gradle library wrapper around yt-dlp with optional FFmpeg/aria2c modules.

Integration direction:
- Keep Koda's download UI, queue, persistence and metadata enrichment.
- Add a `DownloadBackend` adapter for yt-dlp rather than transplanting a second downloader app UI.
- Route extraction/download through the selected backend, then hand completed files to the existing library and metadata pipeline.
- Preserve quality/format options, queue, retry/cancel and progress.
- Re-evaluate Android Python runtime, yt-dlp, FFmpeg and YouTube challenge dependencies at build time; do not pin an old runtime without a device test.

YTDLnis is GPL-3.0; do not reuse its branding. yt-dlp itself is Unlicense, but packaged Android runtime artifacts can include third-party components with separate licenses. Retain notices for whichever artifact is selected.

**Not yet integrated:** the yt-dlp runtime is a planned adapter, not part of the current Koda submodule commit.

## 3. Metadata and tag editing

Koda already depends on `net.jthink:jaudiotagger:3.0.1` and uses it to read embedded lyrics and write tags/artwork/lyrics into downloaded audio. Rymora's missing piece is the interactive editor, not a replacement tag parser.

Planned editor capabilities:
- Single-track and batch editing
- Title, artist, album artist, album, track/disc number, year/date, genre, composer, publisher, comment and lyrics
- Replace/remove embedded artwork
- Safe write-back for MediaStore/Storage Access Framework URIs
- Preview changes and preserve the original file if writing fails

TagTag is a relevant feature reference, but its current repository snapshot has no visible LICENSE file. Do not copy its application source unless its maintainer supplies an explicit license. Mastigias is AGPL-3.0-only; adopting its source would require a deliberate licensing decision. Prefer the existing jaudiotagger dependency in the GPL-3.0 Koda foundation.

## 4. Lyrics and translation

Koda's lyric sources include YouLyPlus, BetterLyrics, NetEase, SimpMusic, LRCLIB, KuGou and Unison. Its parser can interpret TTML and word-timed lyric data, while local files take precedence for local tracks.

Planned Rymora adjustments:
- Prefer a valid TTML result with timing when available.
- Preserve original TTML payload/source metadata where available so downloads can retain TTML as a sidecar instead of flattening every result to LRC.
- Fall back to Enhanced LRC, ordinary LRC, then plain text.
- Keep lyrics closed until the user explicitly opens them.
- Add translation as a provider adapter that returns original and translated lines aligned to the original timing. Translation is user-triggered and optionally cached.

Do not add a second lyric engine unless testing shows a specific provider gap.

## 5. YouTube Music metadata

Koda already has a native YouTube Music/InnerTube metadata client and parses songs, artists, albums, playlists and related recommendations. Reuse it first. An additional Python `ytmusicapi` adapter is only needed if a specific endpoint or metadata field is missing.

## 6. Licensing rule

Before adding any upstream source:
1. Verify the exact repository commit and license file.
2. Record origin, version/commit and license in this register.
3. Keep original copyright and attribution notices.
4. Check compatibility with the GPL-3.0 Koda base and every bundled native/Python package.
5. Do not reuse source code from repositories with no explicit license.
