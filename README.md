# Rymora — Android music experience

Rymora is a native Android music app combining YouTube Music-style discovery, streaming and music video playback with Musixmatch-style lyrics, local music management, downloads, metadata editing and online translation.

## Android foundation

The `android-foundation` branch uses **Koda** as its Android application foundation through a pinned Git submodule. This deliberately reuses an existing app instead of recreating the music/video client.

- Android foundation: [Koda](https://github.com/Ivorisnoob/Koda), pinned at commit `5a97eccd7702e5aec6f9a443b31077a94e1bd303` on its `beta` branch.
- Downloader direction: integrate a yt-dlp/Python-capable Android backend using existing work such as [YTDLnis](https://github.com/deniscerri/ytdlnis) and [youtubedl-android](https://github.com/yausername/youtubedl-android), after runtime and license review.
- Metadata/tag editing: reuse the jaudiotagger dependency already present in Koda; add Rymora's editing UI and safe MediaStore/SAF write-back.
- Lyrics: retain Koda's multi-provider pipeline and TTML/LRC parser. Lyrics remain closed by default and open only after the user taps Lyrics.

See `android/README.md`, `android/UPSTREAMS.md`, and `android/IMPLEMENTATION_PLAN.md`.

## Get the Android source

```bash
git clone --branch android-foundation https://github.com/riynk/music-rymora.git
cd music-rymora
bash scripts/bootstrap-android.sh
```

Open `android/vendor/koda` in Android Studio. The bootstrap script initializes the pinned upstream and applies the Rymora app ID, app label and palette overlay.

**Status:** the branch contains a pinned Android upstream, a Rymora branding overlay and a CI build workflow. It is not yet a compiled or device-tested Rymora APK. The earlier HTML/CSS/JS concept remains in branch `RY` as a visual prototype.

## Licensing

The Koda upstream is GPL-3.0. Before distributing a modified combined application, preserve copyright and license notices and comply with applicable source-code and redistribution obligations. Third-party components retain their own licenses. Finalize Rymora's top-level licensing and notices before publishing a distributable build.

## Technical audit

See [the full Rymora technical audit](android/AUDIT.md) for verified upstream capability, integration gaps, CI findings, licensing checks and release acceptance criteria. The Android workflow now installs only the supported SDK packages and runs JVM unit tests before assembling the debug APK; a successful run and physical-device validation are still required before calling this an installable Rymora build.
