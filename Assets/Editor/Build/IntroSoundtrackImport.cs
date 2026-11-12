using UnityEditor;
using UnityEngine;

// The intro's soundtrack (Resources/Intro/IntroSoundtrack.mp3, 90 s) stays compressed in memory instead of being
// decompressed on load (about 15 MB of samples), which matters most in the browser and on phones.
public sealed class IntroSoundtrackImport : AssetPostprocessor
{
    void OnPreprocessAudio()
    {
        if (!assetPath.Contains("Resources/Intro/IntroSoundtrack")) return;
        var importer = (AudioImporter)assetImporter;
        var settings = importer.defaultSampleSettings;
        settings.loadType = AudioClipLoadType.CompressedInMemory;
        settings.compressionFormat = AudioCompressionFormat.Vorbis;
        settings.quality = .6f;
        importer.defaultSampleSettings = settings;
        importer.loadInBackground = true;
    }
}
