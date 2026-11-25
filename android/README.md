# Rymora Android workspace

## What is here

`vendor/koda` is a Git submodule pointing to the existing Koda Android application. Koda is selected because its code already includes:

- YouTube Music search/catalog and audio playback
- A dedicated video mode and video playback
- Local music library, offline cache and download queue
- Music and video downloads, including playlist downloads
- Multiple online lyric providers
- Local `.ttml`, `.lrc`, and embedded lyric reading
- Word-timed and line-timed lyric rendering
- Metadata/artwork/lyrics writing for completed audio downloads
- Jetpack Compose, Media3 and Android media controls

Rymora will customize and extend this foundation rather than recreate these systems.

## Checkout

From the repository root:

```bash
git submodule update --init --recursive
```

Open `android/vendor/koda` as the Android Studio project. To build a local debug APK on a machine with the required Android SDK and JDK installed:

```bash
cd android/vendor/koda
./gradlew :app:assembleDebug
```

The upstream debug build still has Koda's debug application ID and branding until Rymora branding and package configuration are applied.

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

This is an upstream source pin and integration workspace, not a completed Rymora fork. Branding, TTML-first provider selection and payload preservation, yt-dlp backend wiring, tag-editing UI and online translation still need implementation and device testing.
