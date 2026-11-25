# Rymora

**Rymora** is an Android music app concept combining music discovery and playback inspired by YouTube Music with synchronized lyrics and lyric tools inspired by Musixmatch—unified in an original, atmospheric dark UI.

## Product direction

### Music experience
- Discover music through search, recommendations, moods, artists, albums and playlists
- Now Playing screen with artwork, queue, playback controls, shuffle, repeat and favorites
- Background playback, Android notification and lock-screen controls
- Library: liked songs, playlists, albums and listening history

### Lyrics experience
- Timed/synchronized lyrics while audio plays
- Full-screen lyrics view and compact lyrics panel
- Lyrics search and song/artist matching
- Translation and lyric display customization (where supported)
- Optional floating lyrics overlay, subject to Android permissions and platform limitations

## Android technology plan
- **Kotlin + Jetpack Compose** — native UI and animations
- **AndroidX Media3 (ExoPlayer)** — audio playback, media session and background playback
- **Room** — local library, favorites, playlists and cached metadata
- **DataStore** — preferences
- Backend/API integration for catalog and lyrics, using licensed/authorized providers

## Visual identity
- Background: `#101010`
- Surface: `#191919`
- Coral accent: `#FF5D72`
- Soft pink: `#FF9BA8`
- Mint: `#B6F0D2`
- Typography direction: DM Sans + Space Grotesk

## Prototype
The current branch includes a responsive HTML/CSS/JavaScript concept for exploring the Rymora visual design. It is **not an Android APK yet**. Native Android implementation is the intended next stage.

## Content and rights
Music streaming, lyrics, lyric translations and floating lyric overlays depend on provider APIs, licensing, and Android platform permissions. The app will use authorized sources and will not re-host copyrighted music or lyrics without permission.

## Roadmap
1. Native Android project scaffold and Compose navigation
2. Home, Search, Library and Now Playing screens
3. Media3 playback and background media controls
4. Lyrics screen with synchronized timing
5. Provider integration, local favorites and playlists
6. Build, test and distribute APK
