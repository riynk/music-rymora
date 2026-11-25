# music-rymora

**Rymora Music** — responsive music discovery interface inspired by the dark, immersive feel of YouTube Music, with an original Rymora visual identity.

## UI foundation
- Responsive sidebar, search, mood tiles, album cards and track rows
- Bottom playback bar: play/pause, previous/next, shuffle, repeat, like, seek and volume
- Animated equalizer mark, orbit rings, spinning vinyl and twinkling accents
- Dark charcoal palette, coral-pink accent, soft mint status color
- Mobile menu + reduced-motion accessibility preference

## Run locally
No build step required:
```bash
python3 -m http.server 8000
```
Open http://localhost:8000.

## Sources
- **Design reference:** YouTube Music (inspiration only; no copied brand assets)
- **Typography:** Google Fonts — DM Sans, Space Grotesk
- **Placeholder album art:** Unsplash image URLs
- **Music search & preview source (planned integration):** Apple iTunes Search API, which returns track metadata, artwork and preview URLs. Preview clips only; not full streaming.

## Next
- Wire iTunes search results and preview playback into the UI
- Persist favorites and playlists locally
- Authorized full-stream provider integration, if available