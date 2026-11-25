# Rymora — Technical Audit

**Audit date:** 2026-11-25  
**Audited branch:** `android-foundation`  
**Audited parent commit:** `d75596637b11d2a665d3e269f80277546fb712a0`  
**Pinned Android upstream:** [Ivorisnoob/Koda](https://github.com/Ivorisnoob/Koda), commit `5a97eccd7702e5aec6f9a443b31077a94e1bd303` (Koda 5.4 / `beta`)  
**Status:** CI debug build and upstream unit tests pass; product integration and device validation remain open.

## 1. Executive verdict

Rymora is **not an Android tutorial project**. The selected upstream, Koda, is a substantial Kotlin/Jetpack Compose Android application with an established music client, video player, local library, Media3 playback services, queue, downloads, lyrics providers, settings, widgets, Android Auto support and a large test/source tree.

However, the current Rymora branch is still an **integration scaffold**, not a completed Rymora fork:
- The application source is referenced as a Git submodule. The Rymora parent repository contains no standalone Gradle Android project.
- The branding script changes a limited set of source strings and theme values. It does not rebrand all translations or replace every upstream identity.
- The CI pipeline now builds a debug APK and runs upstream unit tests; an artifact is verified for run [45620251758](https://github.com/riynk/music-rymora/actions/runs/45620251758).
- TTML-first selection is implemented; an additional overlay now carries the original TTML payload through parsing and exports `.ttml` offline sidecars while retaining LRC fallback. JVM regression tests are added; validation of this latest overlay is pending. yt-dlp backend, lyric translation and general tag-editor UI remain unimplemented.
- The APK is a CI debug artifact, not yet install-tested on a physical device.

**Conclusion:** Koda remains the high-feature upstream foundation. A debug APK now builds successfully, but the branch is not production-ready or device-validated. Continue with maintainable fork ownership and the remaining Rymora-specific differentiators.

## 2. What was actually inspected

The audit inspected:
- Rymora repository metadata, branches, commit history and recursive tree.
- The Android branch's submodule pointer, bootstrap and branding scripts, workflow and implementation documents.
- The pinned Koda repository metadata, exact commit, recursive source tree, Gradle configuration, manifest, README, roadmap, security policy and third-party notices.
- Lyrics parser, provider registry, lyrics repository, local sidecar lookup, player panel state, player view-model fetch calls, download metadata writer and download repository.
- The recorded GitHub Actions job steps and complete job log for run [45616467002](https://github.com/riynk/music-rymora/actions/runs/45616467002).

This was a repository/source/CI audit plus a successful hosted Gradle unit-test and debug-APK build. It was **not** a physical-device install/playback test; no such result is claimed.

## 3. Upstream assessment — what Koda already gives Rymora

At the pinned commit, Koda is a native Android project:
- Kotlin + Jetpack Compose; one Gradle `:app` module and Gradle wrapper.
- Media3 playback and Android media-service integration.
- YouTube Music search/catalog flows and music metadata parsing.
- Separate music and video experiences, video player, captions/subtitles, PiP and video queue.
- Local library, local playlists, offline cache and media downloads.
- Background audio, notification/lock-screen controls, widgets and Android Auto integration.
- Multiple player styles, adaptive layouts, theme/palette customization, history and listening statistics.
- Multiple online lyric providers, TTML/LRC/QRC parsing, local sidecars and embedded lyrics.
- jaudiotagger dependency for reading/writing metadata in parts of the download pipeline.

The upstream tree contained 1,125 entries at the audited commit, including tests, Gradle configuration, license and third-party notices. The Koda pin matches the `beta` branch tip at the audit time; it is a fixed commit rather than a floating submodule checkout.

This is a credible feature-rich foundation. Rymora should reuse these systems rather than recreate a basic sample player.

## 4. Requirements coverage

| Rymora requirement | Upstream at audited pin | Rymora status / work required |
|---|---|---|
| YouTube Music-like discovery and metadata | Present | Rebrand and validate; catalog extraction depends on unofficial YouTube interfaces |
| Online audio playback | Present | Build and device validation required |
| Offline/local playback and library | Present | Validate cold start, storage access, cache and file permissions |
| Music video browsing/playback | Present | Validate on device, including PiP and audio/video handover |
| Lyrics not shown automatically | Player panel defaults to Up Next; Lyrics is an explicit panel/tab | Preserve this behavior; lyrics data may still be fetched in background |
| TTML parsing | Present | Parsing support is not the same as TTML-first preference |
| TTML-first provider selection | Not present upstream | Rymora overlay adds format-aware ranking; regression-tested in CI |
| Preserve TTML for offline use | Not present in current download serialization | Preserve source format/raw TTML; do not flatten every result into LRC |
| LRC / Enhanced LRC fallback | Present | Retain as fallback and regression-test |
| yt-dlp / Python download backend | Not integrated; Koda uses its NewPipe-based downloader | Add a pluggable adapter; retain queue, progress, persistence and metadata handoff |
| Music video/audio download | Present through upstream downloader | Switch or extend backend to meet the yt-dlp requirement |
| General tag editor | Not present | Build editor UI and safe write-back using the existing metadata library where supported |
| In-app artist/album/song information | Much of the catalog and artist/album detail is present | Audit field completeness and fill missing data through existing metadata APIs |
| Online lyric translation | Not present | Add user-invoked translation provider(s), line alignment and cache |
| Translation available offline | Not present | Cache accepted translations and associate them with the local track/lyric version |
| Rymora identity | Partial overlay only | Complete branding, translations, icons, package/update identity and notices |

## 5. Confirmed technical findings

### RYM-001 — CI fails before the Android project is built
**Severity: P0 / release blocker**

The only recorded Android workflow run checked out the Rymora repository and Koda submodule successfully and installed JDK 21. It then failed in **Set up Android SDK**. The job log shows:

```text
sdkmanager tools
Warning: Failed to find package 'tools'
... sdkmanager failed with exit code 1
```

Google no longer serves the legacy SDK `tools` package. The branding step, Gradle build and artifact upload were skipped. The run produced zero APK artifacts.

**Remediation committed:** workflow now uses `android-actions/setup-android@v4` and installs `platform-tools` only; Gradle resolves build tools. It also runs overlay regression tests, upstream JVM unit tests and debug APK assembly. Run [45620251758](https://github.com/riynk/music-rymora/actions/runs/45620251758) completed successfully. Artifact `rymora-android-debug` was uploaded (ZIP 126,461,215 bytes; APKs inside include universal and ABI-specific builds). Artifact verified; physical install remains untested.

**Interpretation:** The original failure did not demonstrate a Kotlin/Gradle compilation defect. It demonstrated a broken SDK setup step. The SDK setup cause is now fixed; the app still needs the test and build stages to finish successfully before an APK can be claimed.

### RYM-002 — The Rymora repository is a wrapper around an upstream submodule
**Severity: P1 / architecture**

`android/vendor/koda` is a Git submodule pointing to `Ivorisnoob/Koda`. This preserves upstream history and makes version pinning explicit, but the Koda application files are not normal files owned by the Rymora parent branch. Feature changes made inside a checked-out submodule do not become Rymora commits unless they are committed to a repository that owns that submodule.

The current submodule points to the upstream repository, where the Rymora project does not have push ownership. A branding script is not enough for ongoing feature development.

**Recommendation:** create a Rymora-owned fork of Koda and repoint the submodule to that fork at a reviewed commit. Keep upstream as the merge source; maintain a documented upstream-sync process. This is preferable to carrying a growing pile of patch files or repeatedly copying the whole app.

### RYM-003 — TTML support exists, but TTML is not the selected priority
**Severity: P1 / core product requirement**

The upstream parser can parse TTML, including timed spans. However:
- The normalized lyrics model stores parsed lines and a sync-quality enum; it does not retain a first-class source-format field or the raw TTML payload.
- The remote repository ranks candidates by sync quality (word/line/plain), not by source format. A word-timed result in another format can outrank a valid TTML result.
- Local sidecar lookup uses the extension order `lrc`, then `ttml`; an LRC sidecar can be selected before a TTML sidecar.
- The download metadata path converts parsed timed lyrics back to LRC/Enhanced LRC/plain text. It does not preserve the original TTML document.

**Implemented in the Rymora overlay (commit `1ee3287`):** the normalized model now has a source-format marker (`TTML` vs `OTHER`); the parser tags TTML results; the remote candidate rank puts TTML ahead of sync quality (sync quality is the tie-breaker); and local sidecar search checks TTML before LRC. A fail-closed, idempotent overlay is run by bootstrap, with fixture regression tests in `tests/test_rymora_lyrics_patch.py`.

**Still open:** raw TTML payload preservation and TTML sidecar writing for downloaded files. The overlay does not claim lossless TTML offline preservation yet. Enhanced LRC/LRC/plain remain fallback formats. The overlay's fixture tests and the upstream Gradle test/build must pass before treating this implementation as validated.

### RYM-004 — Lyrics are hidden by default, but are prefetched automatically
**Severity: P2 / behavior to preserve and test**

The classic player panel initializes to `UpNext`, and the adaptive companion pane initializes to `UP_NEXT`; Lyrics is a separate user-selected tab. The player view-model also calls lyric fetching when restoring a session and when the media item changes.

This is consistent with the stated requirement **provided fetched text never takes over the visible player**. Keep the initial visible pane on Up Next and make opening Lyrics an explicit action. Add UI tests for first launch, track changes, relaunch/process restoration and switching between audio/video modes.

### RYM-005 — yt-dlp is only a documented direction, not an implementation
**Severity: P1 / core product requirement**

The pinned Koda source currently uses a NewPipe Extractor download path. Rymora's `UPSTREAMS.md` lists YTDLnis and youtubedl-android as candidates, but neither is wired into the app.

**Recommendation:** introduce a backend interface behind the existing queue. Evaluate an Android-compatible yt-dlp/Python runtime, FFmpeg muxing, JavaScript challenge runtime, ABI packaging, storage permissions, cancellation, pause/resume, playlist support, cookies/session isolation and license notices. Keep the existing queue/progress/persistence UI. Do not transplant a second downloader app's UI.

### RYM-006 — There is metadata writing, not a general-purpose tag editor
**Severity: P1 / core product requirement**

jaudiotagger is already present. The inspected metadata code enriches completed downloads (title, artist, album, lyrics, artwork) and local lyrics lookup reads embedded tags. That does not provide a general editor for existing user files.

Koda's roadmap explicitly lists an ID3 tag editor as not planned. Rymora must deliberately diverge from that product decision.

**Recommendation:** add single-track and batch editing, artwork replacement, lyrics/tag editing, filename templates and preview. Use Android Storage Access Framework / MediaStore URIs rather than assuming a raw filesystem path. Write through a temporary copy, verify the result, preserve the original on failure, and refresh the media index.

### RYM-007 — Lyrics translation is absent
**Severity: P1 / core product requirement**

The inspected lyric code contains provider fetching, parsing, romanization and presentation customization, but no online lyrics-translation engine. Romanization is not translation.

**Recommendation:** add a provider interface that accepts source text and target language, returns per-line translations, preserves the original lyric timestamps and singer/line grouping, is invoked by the user, handles quotas/errors and caches accepted translations for offline display.

### RYM-008 — Branding overlay is incomplete
**Severity: P1 / product identity**

The script changes the application ID and selected base-resource/theme values, but:
- The Kotlin namespace/package remains `com.ivor.ivormusic` (technically allowed, but still upstream identity).
- Only the base `values/strings.xml` is edited; localized resources such as `values-id/strings.xml` still contain “Koda”.
- The base strings file has many user-visible “Koda” references beyond the app label.
- The launcher icon, all screenshots, help/about copy, download-folder naming and translated strings still need an explicit branding decision.
- The update-checker target changes to the Rymora repository, but that repository does not yet publish a tested Rymora release.

The exact replacement anchors currently present in the pinned Gradle/theme/resource files were checked and each required anchor occurred once. This is a static anchor check, not a successful execution of the complete bootstrap on a real checkout.

### RYM-009 — Licensing and attribution need a release gate
**Severity: P1 / distribution**

Koda is GPL-3.0. Its license and third-party notices must remain with the derived distribution and the combined project's source/distribution approach must comply with applicable GPL-3.0 terms. The Rymora parent repository currently has no top-level license declared. The new yt-dlp runtime, Python, FFmpeg, JS engine, lyric providers and other bundled artifacts each need a versioned license/notice inventory.

Do not copy source from an unlicensed repository merely because it has a useful feature. Recheck licenses at the exact commit/artifact selected.

### RYM-010 — The YouTube data layer is an upstream dependency risk
**Severity: P2 / operational reliability**

Koda documents that it uses YouTube's internal/InnerTube interfaces and NewPipe extraction rather than an official YouTube Music API key. This is feature-rich but can break when upstream response formats, streaming restrictions or challenge mechanisms change. Keep extraction behind adapters, record provider/source errors, apply backoff, avoid retry storms and retain local/offline functionality when remote services fail. Treat this as a reliability and policy review item, not as a claim that the app cannot be built.

### RYM-011 — Current build pipeline is not release-grade
**Severity: P1 / release process**

The workflow now runs JVM unit tests before assembling a debug APK, and the SDK setup failure from the first run has been corrected. The corrected run is still in progress: unit tests have started, while APK assembly and artifact upload are pending. There is no confirmed Rymora APK yet. Lint, instrumentation tests and physical-device tests are not part of the current workflow. It does not create a signed release build, publish release checksums or produce a dependency/license report as a release artifact.

**Recommendation:** confirm the current unit-test and debug-build run, then add lint and a test matrix. Add a separately protected release workflow with owner-controlled signing, versioning, checksums, changelog and license/third-party notices. Pin critical GitHub Actions to reviewed immutable SHAs before public releases.

### RYM-012 — Android permissions and exported components need a Rymora-specific security pass
**Severity: P2 / privacy and platform compatibility**

The upstream manifest declares audio/video media permissions, legacy external-storage read permission, broad `MANAGE_EXTERNAL_STORAGE`, foreground service permissions for playback/data sync, notifications, network state, wake lock and battery-optimization exemption requests. The application also declares backup/data-extraction configuration and exported services/providers required for media integrations, widgets and other Android surfaces.

These choices support Koda's extensive feature set, but Rymora must not carry them forward blindly. In particular, the tag editor and downloader should use Storage Access Framework/MediaStore access where sufficient; broad all-files access should have a clear necessity and user-facing explanation. Exported media services/providers and imported playlists, subtitles, backup archives, stream manifests and session cookies need explicit regression tests against the upstream security policy.

**Recommendation:** create a permission-to-feature matrix, verify each exported component's intent filters and caller expectations, review backup inclusion/exclusion for credentials and personal data, and test untrusted file/metadata parsing and write-path confinement before distributing Rymora.

## 6. Build and platform profile at the pinned upstream

| Setting | Audited value |
|---|---|
| Android language/UI | Kotlin / Jetpack Compose |
| Playback | AndroidX Media3 |
| Namespace | `com.ivor.ivormusic` |
| Upstream application ID | `com.ivor.ivormusic` before overlay |
| Min SDK | 26 (Android 8.0) |
| Target SDK | 36 |
| Compile SDK | 37 |
| JDK in current CI | 21 |
| Gradle wrapper | 9.6.1 |
| Android Gradle Plugin | 9.3.1 |
| Kotlin | 2.4.20 |
| Media3 | 1.11.0 |
| NewPipe Extractor | v0.26.5 |
| jaudiotagger | 3.0.1 |

These versions describe the pinned commit and must be rechecked if the submodule moves.

## 7. Remediation plan — product engineering, not tutorial scaffolding

### Gate 0 — Make the existing build verifiable
- Stop requesting the removed SDK `tools` package.
- Run upstream JVM tests and `:app:assembleDebug`.
- Confirm the branding overlay applies to the real checkout and remains idempotent.
- Publish the APK only as a CI debug artifact after a successful build.
- Record exact failing task/logs rather than treating SDK setup as an app compilation failure.

### Gate 1 — Put the source under Rymora's control
- Fork Koda into a Rymora-owned repository.
- Repoint the submodule to the owned fork and pin an immutable commit.
- Keep upstream origin/remotes and document how to sync upstream changes.
- Separate Rymora changes into reviewable commits and preserve all original notices.

### Gate 2 — Implement the four differentiators
1. TTML-first lyrics selection and lossless TTML offline preservation.
2. yt-dlp/Python downloader backend behind the existing download queue.
3. General tag editor with safe SAF/MediaStore writes and rollback.
4. Online lyrics translation preserving per-line timing and original text.

### Gate 3 — Finish identity and metadata experiences
- Complete Rymora visual identity, launcher artwork, localized strings and About/licensing screens.
- Review artist, album and track information for completeness; expose detailed info in-app.
- Add Indonesian and English copy review while retaining existing localization infrastructure.

### Gate 4 — Device and release validation
- Test streaming/offline playback, background service, notifications, headset/Bluetooth, Android Auto, seek/crossfade, queue restore and audio/video handover.
- Test download cancellation/retry, playlist downloads, FFmpeg muxing, storage URI writes and low-storage behavior.
- Test TTML parsing/timing, provider fallback, local sidecars, translation alignment and no-auto-lyrics UI.
- Test tag editor round-trip and failure rollback across MP3, M4A, FLAC and other formats the selected tag library truly supports.
- Test process death, Android 8 compatibility, recent Android storage/notification behavior, rotation, PiP and battery restrictions.
- Publish only after clean CI, physical-device smoke tests, license review and a reproducible signed release.

## 8. Acceptance criteria

Rymora is not considered a release candidate until:
- A clean recursive checkout can run the documented bootstrap.
- Branding validation passes against the pinned Rymora-owned source.
- Unit tests, lint and debug build pass in CI.
- A debug APK is produced and installed on a physical Android device.
- Lyrics stay closed unless the user opens them; TTML wins when a valid TTML result is available.
- Downloaded TTML remains available offline without silently degrading to plain text/LRC-only storage.
- yt-dlp downloads run through the existing queue and complete with correct tags/artwork.
- Translation is user-triggered and timestamp-aligned.
- Tag edits safely persist to selected files and recover from failed writes.
- Music/video playback and local library remain usable when online providers are unavailable.
- GPL-3.0 and third-party notices are complete for the exact distributed build.

---

**Audit disposition:** Keep Koda as the foundation. CI is fixed and produces a debug APK. Next, move to a Rymora-owned maintained fork or pin a reproducible overlay strategy, then implement TTML raw-payload preservation, downloader integration, translation and tag editing. Device validation and licensing/security review remain release gates.
