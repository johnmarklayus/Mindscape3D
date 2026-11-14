using System;
using System.Linq;
using UnityEditor;
using UnityEngine;

/// <summary>
/// The chapter builders (Mindscape › Legacy Builders) generated the episode scenes once. The scenes are now edited by
/// hand in Unity, and a rebuild throws those edits away, so every rebuild asks first. In batch mode a rebuild only runs
/// with the -mindscapeRebuild command-line flag.
/// </summary>
public static class LegacyBuilders
{
    public const string Root = "Mindscape/Legacy Builders/";

    /// <summary>True when the rebuild may go ahead.</summary>
    public static bool ConfirmRebuild(string what)
    {
        if (Application.isBatchMode)
        {
            if (Environment.GetCommandLineArgs().Contains("-mindscapeRebuild")) return true;
            Debug.LogError("[LegacyBuilders] Refused to rebuild " + what + ": the scenes are edited by hand now. Pass -mindscapeRebuild to rebuild anyway.");
            return false;
        }
        return EditorUtility.DisplayDialog(
            "Rebuild " + what + "?",
            "The episode scenes are now edited by hand in Unity.\n\nRebuilding generates " + what + " again from code and REPLACES the episode objects in those scenes: anything moved, added or changed by hand there is lost (Story Markers included).\n\nTo make a new episode, use Mindscape › Story › New Episode instead.",
            "Rebuild anyway", "Cancel");
    }
}
