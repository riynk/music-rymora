# Rymora Android workspace

## What is here

`vendor/koda` is a Git submodule pointing to the existing Koda Android application. Koda is selected because its code already includes YouTube Music search/catalog and audio playback, dedicated music-video playback, local music library and offline cache, audio/video download queue, multiple online lyric providers, local `.ttml`/`.lrc` and embedded lyric reading, word/line timing, metadata/artwork/lyrics writing, Jetpack Compose, Media3 and Android media controls.

Rymora will customize and extend this foundation rather than recreate these systems.

## Checkout and apply Rymora overlay

From the repository root:

```bash
bash scripts/bootstrap-android.sh
```

Open `android/vendor/koda` as the Android Studio project. To build a local debug APK on a machine with the required Android SDK and JDK 21:

```bash
cd android/vendor/koda
./gradlew :app:assembleDebug
```

The bootstrap overlay sets the Rymora application ID, display name, version label and brand palette. It does not replace upstream source code or remove its notices.

## Pinned upstream

- Repository: https://github.com/Ivorisnoob/Koda
- Branch at pin time: `beta`
- Commit: `5a97eccd7702e5aec6f9a443b31077a94e1bd303`
- License: GPL-3.0

Do not move the submodule to a floating branch head without reviewing upstream code, dependencies, behavior and license notices.

## Rymora non-negotiables

1. The player must not automatically open or display lyric text. Lyrics open only after an explicit user action.
2. TTML is the preferred timed-lyrics format when a valid TTML result is available. Enhanced LRC/LRC and plain text are fallbacks.
3. Online and offline listening are first-class modes.
4. Music and music videos are both supported.
5. Metadata, artwork and lyrics should remain attached to local files where the container format supports them.
6. Downloads use a pluggable backend; the target includes a yt-dlp/Python backend.
7. Translation is an online, user-invoked layer with optional local caching; original lyrics remain available.

## Current gaps

The branch contains the upstream and branding bootstrap, not a completed Rymora fork. TTML-first provider selection and TTML payload preservation, yt-dlp backend wiring, tag-editing UI and online translation still need implementation and device testing.
