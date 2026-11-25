# ADR-002: yt-dlp runtime candidate for Rymora

**Status:** Candidate for a build/API spike only; not adopted. YouTube reliability is a release-blocking validation criterion.  
**Date:** 2026-11-25

## User requirement

Rymora must retain its native download queue and UX while using a Python/yt-dlp backend for audio/video extraction and downloading.

## Candidates reviewed

### A. `ffmpegkit-maintained/yt-dlp-android` v2.0.2 — build/API spike candidate

- Embeds CPython 3.13 through Chaquopy and calls yt-dlp in-process.
- MIT library license; bundled third-party notices are provided by the project.
- Java/Kotlin API uses `YtDlp.init()`, request/response types and progress callbacks.
- Trade-offs: reported AAR footprint ~60–80 MB for supported ABIs; arm64-v8a and x86_64 only; yt-dlp version is fixed by the library build and needs a dependency bump for updates; no TLS impersonation in the basic free runtime.
- This aligns closest with the requested Python runtime, but it is a dependency evaluation only. Verify artifact provenance, build reproducibility, APIs, device compatibility, notices and current release state before adding it.

Source: https://github.com/ffmpegkit-maintained/yt-dlp-android

### B. `yausername/youtubedl-android`

- Established Android wrapper bundling Python and yt-dlp, with optional FFmpeg and aria2 modules.
- GPL-3.0.
- README currently documents an older Python runtime; current yt-dlp increasingly requires modern Python. ABI packaging, native library page-size compatibility, and maintenance/version provenance must be checked for the exact release.
- Less attractive as the default for a new app until a current runtime and reproducible build are confirmed.

Source: https://github.com/yausername/youtubedl-android

### C. YTDLnis

- Mature Android downloader app with its own downloader integration, bundled Python/runtime and plugin/package update system.
- GPL-3.0 application. Its app architecture and package system are useful research, but importing its UI or full app into Rymora would be unnecessary and would increase maintenance and copyleft review scope.
- Treat as a behavioral reference, not the integration target.

Source: https://github.com/deniscerri/ytdlnis

## Decision

Run a dependency spike on candidate A before adoption. Keep Rymora's existing `DownloadRepository` and queue. Implement an interface such as:

- `probe(request): DownloadFormats`
- `start(request, destination, callbacks): DownloadJob`
- `cancel(jobId)`
- `resume(jobId)` (only if backend actually supports resumable state)
- `mapProgress(event): DownloadProgress`

Do not make the backend own UI, queue persistence, destination permissions, metadata editing, or lyrics fetching. It should resolve and download media only; the app orchestrates those other responsibilities.

## Spike acceptance criteria

1. The selected runtime builds with the pinned upstream Koda Gradle/AGP/Kotlin toolchain.
2. A clean install initializes the Python runtime on supported arm64 devices.
3. Audio-only and video download probe/transfer work with progress, cancellation and clear failure states.
4. FFmpeg mux/extract behavior is tested separately and no native ABI conflicts occur.
5. Output is written through app-controlled storage/SAF and verified before the current metadata/tag pipeline runs.
6. Runtime size and ABI limits are documented and reflected in APK/AAB distribution strategy.
7. yt-dlp version updates, third-party notices, security updates and legal/policy review are tracked.
8. A mock backend unit test validates the queue adapter without network or native runtime.

**No downloader dependency is committed yet.** This ADR records the selected spike candidate, not a completed feature.


## Additional validation gate (2026-11-26)

The currently published v2.0.2 free artifact is available from Maven Central, but its upstream documentation explicitly excludes TLS fingerprint impersonation. Its maintainer describes curl-cffi fingerprint impersonation as a Pro-only feature and notes that standard HTTP may be blocked by some sites, including YouTube. Therefore **this candidate is not approved for production integration until a real YouTube test succeeds on a physical arm64 device**. A build/API spike alone is insufficient.

- Upstream README: https://github.com/ffmpegkit-maintained/yt-dlp-android
- v2.0.2 release: https://github.com/ffmpegkit-maintained/yt-dlp-android/releases/tag/v2.0.2
- Maven artifact: https://central.sonatype.com/artifact/dev.ffmpegkit-maintained/yt-dlp-android/2.0.2

The library's advertised free ABI support is arm64-v8a and x86_64 only. Rymora currently produces a 32-bit ABI APK as part of its debug matrix; if adopting the dependency, disable 32-bit packaging intentionally and test the distribution split. Do not add this large runtime before resolving both compatibility and YouTube reliability.
