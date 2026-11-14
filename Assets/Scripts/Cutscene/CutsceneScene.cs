using System.Collections;
using Mindscape.Data;
using UnityEngine;

namespace Mindscape.Cutscenes
{
    /// <summary>
    /// A scene that only plays a cutscene, then opens the cutscene's Next Scene (through the loading screen) or the
    /// main menu. Made by Mindscape › Story › New Cutscene… with "As a scene of its own".
    /// </summary>
    [AddComponentMenu("Mindscape/Cutscene Scene")]
    public class CutsceneScene : MonoBehaviour
    {
        [Tooltip("The cutscene to play.")]
        public CutsceneAsset cutscene;
        [Tooltip("The episode number the loading screen shows for the next scene (chapters made in the editor know their own).")]
        public int nextEpisodeNumber = 1;

        IEnumerator Start()
        {
            yield return CutscenePlayback.Play(cutscene);
            string next = cutscene != null ? cutscene.nextScene : "";
            if (string.IsNullOrEmpty(next) || !Application.CanStreamedLevelBeLoaded(next)) { MusicManager.LoadSceneFaded("main_menu_new"); yield break; }
            if (StoryChapters.Find(next, out int chapter, out int episode)) EpisodeLoadingScreen.Load(next, episode, chapter);
            else EpisodeLoadingScreen.Load(next, nextEpisodeNumber);
        }
    }
}
