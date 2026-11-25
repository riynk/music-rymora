#!/usr/bin/env python3
"""Apply a small, reviewable Rymora overlay to the pinned Koda submodule."""
from pathlib import Path
import sys

def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding='utf-8')
    old_count = text.count(old)
    new_count = text.count(new)
    if new_count == 1:
        return  # already applied
    if old_count == 1:
        path.write_text(text.replace(old, new, 1), encoding='utf-8')
        return
    raise RuntimeError(f'{path}: expected one old or one patched occurrence; old={old_count}, new={new_count}')

def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: apply_rymora_branding.py <koda-submodule-path>', file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not (root / 'app/build.gradle.kts').is_file():
        raise SystemExit(f'Not a Koda Android project: {root}')

    gradle = root / 'app/build.gradle.kts'
    replace_once(gradle, 'applicationId = "com.ivor.ivormusic"', 'applicationId = "com.riynk.rymora"')
    replace_once(gradle, 'versionName = "5.4"', 'versionName = "0.1.0-alpha01"')
    replace_once(gradle, 'manifestPlaceholders["appLabel"] = "Koda Debug"', 'manifestPlaceholders["appLabel"] = "Rymora Debug"')
    replace_once(gradle, '"ivorisnoob/Koda"', '"riynk/music-rymora"')
    replace_once(gradle, '"ivorisnoob"', '"riynk"')

    strings = root / 'app/src/main/res/values/strings.xml'
    replace_once(strings, '<string name="app_name">Koda</string>', '<string name="app_name">Rymora</string>')
    replace_once(strings, '<string name="widget_action_open_app">Open Koda</string>', '<string name="widget_action_open_app">Open Rymora</string>')

    color_file = root / 'app/src/main/java/com/ivor/ivormusic/ui/theme/Color.kt'
    replace_once(color_file, 'val DarkSurfaceVariant = Color(0xFF1E1E1E)', 'val DarkSurfaceVariant = Color(0xFF191919)')
    replace_once(color_file, 'val PrimaryBlue = Color(0xFFB8D4FF)\nval PrimaryBlueContainer = Color(0xFFB8D4FF)\nval OnPrimaryBlue = Color(0xFF000000)', 'val PrimaryBlue = Color(0xFFFF5D72)\nval PrimaryBlueContainer = Color(0xFFFF9BA8)\nval OnPrimaryBlue = Color(0xFF2A1017)')
    replace_once(color_file, 'val SecondaryPurple = Color(0xFFD0BCFF)', 'val SecondaryPurple = Color(0xFFB6F0D2)')
    replace_once(color_file, 'val SecondaryPurpleContainer = Color(0xFF4A4458)', 'val SecondaryPurpleContainer = Color(0xFF29483B)')
    replace_once(color_file, 'val TextSecondary = Color(0xFFB3B3B3)', 'val TextSecondary = Color(0xFFA5A3A1)')

    theme_file = root / 'app/src/main/java/com/ivor/ivormusic/ui/theme/Theme.kt'
    replace_once(theme_file, 'background = Color(0xFF0F0F0F)', 'background = Color(0xFF101010)')
    replace_once(theme_file, 'surface = Color(0xFF1E1E1E)', 'surface = Color(0xFF191919)')
    replace_once(theme_file, 'colorPalette: String = DYNAMIC_PALETTE_ID', 'colorPalette: String = "rymora"')

    palette_file = root / 'app/src/main/java/com/ivor/ivormusic/ui/theme/ColorPalettes.kt'
    replace_once(palette_file, '    // Vibrant\n', '    // Rymora brand\n    AppPalette("rymora", "Rymora", "Brand", Color(0xFFFF5D72), Color(0xFFFF9BA8), Color(0xFFB6F0D2)),\n\n    // Vibrant\n')

    prefs_file = root / 'app/src/main/java/com/ivor/ivormusic/data/ThemePreferences.kt'
    replace_once(prefs_file, 'const val DEFAULT_COLOR_PALETTE = "dynamic"', 'const val DEFAULT_COLOR_PALETTE = "rymora"')

    print(f'Rymora branding applied to {root}')
    print('The lyrics panel remains explicitly opened by the user (Up Next is the default).')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
