# Main menu new

Open `Assets/Scenes/main_menu_new.unity` and enter Play Mode.

The new scene has its own controller, UI Toolkit stylesheet, document, and panel settings. It is appended to Build Settings; the original launch scene and existing scene indices are preserved.

The root UI Toolkit style loads Comic Neue Regular from `Resources/MinigameTheme` for body text. Story Serif remains the heading font.

## Reference mapping

The ten images in `UI/mainmenu` inform Home, Chapter Select, Episodes, Continue, Journal, Options, How to Play, Resources, About Us, and Quit confirmation. Native interactive UI recreates their brass, dark wood, parchment, serif headings, botanical ornaments, and book layouts. Existing game artwork supplies the logo and illustrations.

Every page uses the same background on the shared root: `Assets/Resources/MenuArt/Background.png`. The requested `Assets/Resources/background.png` was not present. The background can also be replaced in the scene controller's Background field.

## Behavior

- New Game opens Chapter Select. Chapter 1 contains the tutorial and first story episode. Later content is explicitly unavailable.
- Continue reads the existing `Mindscape.Chapter` / `Mindscape.Episode` PlayerPrefs convention (episode 1 is the tutorial, episode 2 is the first story episode). The existing game has no checkpoint save system, so Resume restarts the saved episode, as stated on screen.
- Journal reflections persist locally under `Mindscape.Reflection.0` through `.4`. Save explicitly or navigate away to retain edits.
- Options use existing Music, SFX, MobileControls, and KeyBindings settings. Master volume, quality, and menu shade persist separately. English is the only implemented language.
- Exit stops Play Mode in the editor, quits native builds, and displays a close-tab message in WebGL.
- The original game's Pause menu still targets the original MainMenu scene; this new scene does not replace it.

## Verification

- Unity 6000.5.8f1 compiled the new runtime and editor code successfully.
- All eight home actions tested through native UI Toolkit NavigationSubmitEvent.
- All 13 tab selections across Options, How to Play, and Resources tested.
- Journal save/reload, music volume persistence, empty-save state, locked episodes, and gameplay scene availability checked. Verification restored pre-existing save and reflection values.
- Visual checks at 1280×720 and 960×540, with the same full-screen background throughout.
- Existing unrelated invalid GUID warning for `Assets/Resources/MenuArt/Button.png.meta` remains; the new menu does not use that asset.

## Sources

Hotline information: https://quezoncity.gov.ph/national-suicide-prevention-week-4/ (7 September 2026). The Resources page links to the source, NCMH, and Find A Helpline.

The unmodified STIX General font is bundled as `StorySerif.otf`; its original embedded copyright and license notice is included in `Assets/Resources/MainMenuNew/STIX-LICENSE.txt`. Project: https://www.stixfonts.org/.
