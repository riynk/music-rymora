# Rymora implementation plan

## Product behavior locked from the owner's requirements

- Native Android smartphone app, not a WebView wrapper.
- YouTube Music-like discovery and player layout with Rymora identity.
- Online audio streaming and offline playback.
- Music-video browsing and playback.
- Music and video downloads through a yt-dlp/Python-capable backend.
- YouTube Music catalog metadata and detailed artist/album/track information in-app.
- TTML-first synchronized lyrics with line/word timing where the provider supplies it.
- Lyrics are **opt-in in the UI**: no automatic lyrics panel on startup or track changes.
- Online lyric translation, aligned with the original lines.
- Local tag editor with single-file and batch operations.
- Local library, playlists, artwork and downloaded-media management.

## Phase A — turn upstream into Rymora

- Change application ID, app label, launcher icon and in-app name to Rymora.
- Preserve Koda's license and third-party notices.
- Apply the Rymora dark palette: background `#101010`, surface `#191919`, coral `#FF5D72`, soft pink `#FF9BA8`, mint `#B6F0D2`.
- Keep the existing Compose navigation, music/video modes and player architecture.

## Phase B — player and lyrics behavior

- Keep Up Next as the initial player panel.
- Keep Lyrics as an explicit tab/button; changing tracks must not switch the panel to Lyrics.
- Ensure relaunch and process restoration do not unexpectedly open the lyric panel.
- Prefer TTML source format before sync quality; use sync quality as the tie-breaker. (Rymora overlay implemented; CI validation pending.)
- Preserve original raw TTML payload and store a TTML sidecar for offline use (not yet implemented).
- Use Enhanced LRC/LRC and plain text as fallbacks.
- Save local TTML sidecars when the selected source is TTML; keep LRC sidecars when LRC was the source (not yet implemented).
- Do not replace a valid local lyric with a lower-quality remote result without user choice.

## Phase C — yt-dlp download adapter

- Define a backend interface matching the existing download queue's media request and progress model.
- Keep the existing UI, queue and job persistence; use yt-dlp as an extraction/download backend.
- Support audio-only, video, format/quality selection, playlist/batch, cancellation, retries and foreground notifications.
- Hand completed files back to the existing metadata/tag pipeline.
- Test Android background restrictions, storage permissions, FFmpeg muxing and YouTube challenge handling on a physical phone.

## Phase D — music info and tag editor

- Reuse Koda's YouTube Music client for catalog data.
- Add track/artist/album information pages without leaving the app.
- Reuse the existing jaudiotagger dependency for supported audio tag formats.
- Add single-track edit, batch edit, artwork replacement, lyrics edit and filename templates.
- Write through Android MediaStore/SAF safely; never assume every user file has a raw filesystem path.

## Phase E — online translation

- Add a translation-provider interface with source selection and rate/error handling.
- Keep original and translated lyric lines separately aligned to original timestamps.
- Support the chosen target language and cache accepted translations.
- Make translation user-triggered; do not silently replace the original lyric.

## Phase F — validation and APK

- Run upstream unit tests and add parser/provider/tag-editor tests.
- Build the debug variant using the upstream Gradle wrapper and documented JDK/SDK.
- Test audio/video, background playback, downloads, offline mode, TTML/LRC switching, no-auto-lyrics behavior, translation and metadata writes on a physical Android device.
- Only mark a build complete after the APK exists and installs successfully.
