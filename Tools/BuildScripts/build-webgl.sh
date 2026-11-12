#!/usr/bin/env bash
# Mindscape · build the WebGL game.
#
# Run it from Git Bash on Windows (it also runs in Terminal on a Mac), from anywhere:
#     ./BuildScripts/build-webgl.sh
# Close Unity first: a project can only be open in one Unity at a time.
# Needs Unity 6000.5.8f1 with "Web Build Support" (Unity Hub > Installs > the gear > Add modules).
# Another Unity install: UNITY="/c/path/to/Unity.exe" ./BuildScripts/build-webgl.sh
#
# Result: one file, Builds/<today>/Mindscape-WebGL-<today>.zip
# (the full build stays next to it in Builds/<today>/WebGL/; the log is in Builds/<today>/logs/).
set -uo pipefail

UNITY_VERSION="6000.5.8f1"
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DAY="$(date +%Y-%m-%d)"
OUT="$PROJECT/Builds/$DAY"
LOGS="$OUT/logs"
TARGET="WebGL"            # Unity's -buildTarget
METHOD="CommandLineBuild.WebGL"
MODULE="WebGLSupport"        # PlaybackEngines folder of the build support module
STAGE="$OUT/WebGL/Mindscape"
RESULT="$OUT/Mindscape-WebGL-$DAY.zip"

say()  { printf '\n\033[1;36m%s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31m%s\033[0m\n' "$*" >&2; exit 1; }
win()  { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }

# ---------------------------------------------------------------- find Unity
find_unity() {
  if [ -n "${UNITY:-}" ]; then printf '%s' "$UNITY"; return; fi
  local pf="/c/Program Files"
  if command -v cygpath >/dev/null 2>&1 && [ -n "${PROGRAMFILES:-}" ]; then pf="$(cygpath -u "$PROGRAMFILES")"; fi
  local candidate
  for candidate in \
    "$pf/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe" \
    "/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe" \
    "/d/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe" \
    "/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity"; do
    if [ -f "$candidate" ]; then printf '%s' "$candidate"; return; fi
  done
}
UNITY_EXE="$(find_unity)"
[ -n "$UNITY_EXE" ] && [ -f "$UNITY_EXE" ] || fail "Unity $UNITY_VERSION was not found. Install it from Unity Hub, or run with UNITY=\"/c/path/to/Unity.exe\"."

# The build support module lives beside the editor: Editor/Data/PlaybackEngines on Windows, PlaybackEngines on a Mac.
editor_dir="$(dirname "$UNITY_EXE")"
case "$UNITY_EXE" in
  *.app/Contents/MacOS/Unity) engines="$(cd "$editor_dir/../../.." && pwd)/PlaybackEngines" ;;
  *) engines="$editor_dir/Data/PlaybackEngines" ;;
esac
[ -d "$engines/$MODULE" ] || fail "\"Web Build Support\" is not installed for Unity $UNITY_VERSION. Add it in Unity Hub > Installs > the gear > Add modules."

if [ -f "$PROJECT/Temp/UnityLockfile" ]; then
  echo "Note: Temp/UnityLockfile exists. If Unity has this project open, close it first or the build will stop."
fi

# ---------------------------------------------------------------- build
mkdir -p "$OUT/WebGL" "$LOGS"
LOG="$LOGS/webgl.log"
rm -rf "$STAGE"
say "Building the WebGL game with Unity $UNITY_VERSION"
echo "Project: $PROJECT"
echo "Log:     $LOG"
echo "This takes about 20 to 30 minutes; progress lines appear below."
start=$(date +%s)

"$UNITY_EXE" -batchmode -quit \
  -projectPath "$(win "$PROJECT")" \
  -buildTarget "$TARGET" \
  -executeMethod "$METHOD" \
  -mindscapeOutput "$(win "$STAGE")" \
  -logFile "$(win "$LOG")" &
unity_pid=$!

# Show the important lines of the log while Unity works.
( sleep 3; tail -n +1 -F "$LOG" 2>/dev/null | grep --line-buffered -E "\[CommandLineBuild\]|error CS[0-9]+|Build Finished|Switching to|It looks like another Unity instance" ) &
tail_pid=$!
wait "$unity_pid"; code=$?
kill "$tail_pid" 2>/dev/null; wait "$tail_pid" 2>/dev/null
minutes=$(( ($(date +%s) - start) / 60 ))

if [ "$code" -ne 0 ] || [ ! -e "$STAGE" ]; then
  echo
  grep -E "error CS[0-9]+|\[CommandLineBuild\]|another Unity instance|Error building|BuildFailedException" "$LOG" | tail -n 20
  fail "The WebGL game build failed (exit code $code) after $minutes min. Full log: $LOG"
fi

# ---------------------------------------------------------------- one file to share
make_zip() {   # make_zip <folder that holds it> <file or folder to pack> <zip file>
  local parent="$1" item="$2" archive="$3"
  rm -f "$archive"
  if [ -x /c/Windows/System32/tar.exe ]; then
    # Windows' own tar writes .zip files; Git Bash's tar cannot.
    ( cd "$parent" && /c/Windows/System32/tar.exe -a -c -f "$(win "$archive")" \
        --exclude "*_DoNotShip" --exclude "*_ButDontShipItWithYourGame" "$item" ) || fail "Could not zip $item."
  elif command -v ditto >/dev/null 2>&1; then
    ( cd "$parent" && ditto -c -k --keepParent "$item" "$archive" ) || fail "Could not zip $item."
  else
    ( cd "$parent" && zip -qr "$archive" "$item" -x "*_DoNotShip*" "*_ButDontShipItWithYourGame*" ) || fail "Could not zip $item."
  fi
}
make_zip "$OUT/WebGL" "Mindscape" "$RESULT"

say "Done in $minutes min: $RESULT"
ls -lh "$RESULT"
echo "To publish: upload the files inside WebGL/Mindscape to a web host that serves .br files with Content-Encoding: br (the Builds/webgl-play Vercel setup does)."
