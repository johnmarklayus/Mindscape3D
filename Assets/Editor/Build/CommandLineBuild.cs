using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

// Builds for the command line (Tools/BuildScripts/*.sh): Unity is started in batch mode with
//   -executeMethod CommandLineBuild.Android | .Mac | .Windows | .WebGL   -mindscapeOutput <path>
// It builds the enabled scenes in File > Build Profiles, with the project's own Player Settings, and quits with exit
// code 0 on success, 1 on failure (the script reads it).
public static class CommandLineBuild
{
    public static void Android()
    {
        EditorUserBuildSettings.buildAppBundle = false;   // an .apk, not an .aab
        Build(BuildTarget.Android, BuildTargetGroup.Android, "Builds/Android/Mindscape.apk");
    }

    public static void Mac() => Build(BuildTarget.StandaloneOSX, BuildTargetGroup.Standalone, "Builds/macOS/Mindscape.app");
    public static void Windows() => Build(BuildTarget.StandaloneWindows64, BuildTargetGroup.Standalone, "Builds/Windows/Mindscape.exe");
    public static void WebGL() => Build(BuildTarget.WebGL, BuildTargetGroup.WebGL, "Builds/WebGL");

    static void Build(BuildTarget target, BuildTargetGroup group, string fallbackOutput)
    {
        int code = 1;
        try
        {
            string output = Argument("-mindscapeOutput") ?? fallbackOutput;
            string[] scenes = EditorBuildSettings.scenes.Where(s => s.enabled && File.Exists(s.path)).Select(s => s.path).ToArray();
            if (scenes.Length == 0) throw new InvalidOperationException("No scenes are enabled in File > Build Profiles.");
            if (EditorUserBuildSettings.activeBuildTarget != target && !EditorUserBuildSettings.SwitchActiveBuildTarget(group, target))
                throw new InvalidOperationException("Could not switch to " + target + ". Is its Build Support module installed in Unity Hub?");
            string folder = target == BuildTarget.WebGL ? output : Path.GetDirectoryName(output);
            if (!string.IsNullOrEmpty(folder)) Directory.CreateDirectory(folder);

            Debug.Log("[CommandLineBuild] " + target + " -> " + output + " (" + scenes.Length + " scenes)");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = scenes, locationPathName = output, target = target, targetGroup = group, options = BuildOptions.None
            });
            var summary = report.summary;
            Debug.Log("[CommandLineBuild] " + summary.result + " in " + summary.totalTime + ", " + (summary.totalSize / 1048576) + " MB, " + summary.totalErrors + " errors");
            code = summary.result == BuildResult.Succeeded ? 0 : 1;
        }
        catch (Exception e)
        {
            Debug.LogError("[CommandLineBuild] " + e.Message);
        }
        EditorApplication.Exit(code);
    }

    static string Argument(string name)
    {
        var args = Environment.GetCommandLineArgs();
        int i = Array.IndexOf(args, name);
        return i >= 0 && i + 1 < args.Length ? args[i + 1] : null;
    }
}
