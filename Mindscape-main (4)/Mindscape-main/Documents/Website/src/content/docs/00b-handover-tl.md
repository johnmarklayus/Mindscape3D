---
id: handover-tl
group: Handover
nav: Gabay sa Handover (Tagalog)
---

# Gabay sa Handover

Kung bago sa Unity at programming, unahin ang [Beginner Start Here](#beginner-guide). Ipinapaliwanag nito ang ligtas na pagbabago, pag-test, pag-undo, at kung kailan kailangan ng programmer.

Maikling gabay para kayo na mismo ang makapagbago ng project. May link ang bawat seksyon papunta sa mas detalyadong pahina (English). **English:** [Handover Guide](#handover).

## 1. Buksan ang project

1. I-install ang **Unity 6000.5.8f1** gamit ang Unity Hub (idagdag ang *Android*, *WebGL* at *Windows/Mac Build Support* kung magbi-build kayo para sa mga ito).
2. Unity Hub ▸ **Add** ▸ piliin ang folder na `mindscape-3d`. Matagal ang unang bukas (ilang minuto) dahil ini-import lahat.
3. Buksan ang `Assets/Scenes/Intro.unity` at pindutin ang **Play**. Magsisimula ito gaya ng totoong laro: intro → main menu.

> [!TIP] Laruin agad ang isang episode
>
> Buksan ang kahit anong `Assets/Scenes/Chapter N - Episode N.unity` at pindutin ang Play. Diretso itong magsisimula sa episode na iyon.

## 2. Saan nakalagay ang mga bagay

| Folder | Laman |
| --- | --- |
| `Assets/Scripts/` | Mga shared script: `Player/`, `UI/` (menu, pause, loading), `Mobile/`, `Audio/`, `Cutscene/`, `Core/` (pinto, graphics, tutorial) |
| `Assets/AcademicPressure/` | Mga episode ng Chapter 1 **at** ang `AcademicEpisode.cs`, ang base ng lahat ng story episode |
| `Assets/FamilyExpectations/`, `Assets/FamilyFinale/` | Mga episode ng Chapter 2 |
| `Assets/SocialDynamics/` | Chapter 3 (iisang script para sa 8 episode, kasama ang `SocialDynamicsChapter.cs`) |
| `Assets/Database/` | Save data (SQLite / local storage) at Supabase cloud sync |
| `Assets/Editor/` | Mga menu tool na gumagawa ng scene at prefab (hindi kasama sa laro mismo) |
| `Assets/UI Toolkit/` | Layout (`.uxml`) at style (`.uss`) ng bawat screen |
| `Assets/Scenes/` | Lahat ng scene. Nasa `Prototypes/` ang mga lumang hindi na ginagamit |
| `supabase/` | Database migrations at ang `account` edge function |
| `Documents/Website/` | Ang site na ito |

Buong listahan: [Project Structure](#structure).

## 3. I-configure ang Supabase connection

Nasa **iisang file** lang ang koneksyon sa Supabase: `Assets/Scripts/Data/MindscapeCloud.cs`, linya 21-23.

```csharp
const string RpcUrl        = "https://<PROJECT_REF>.supabase.co/rest/v1/rpc/";
const string AccountUrl    = "https://<PROJECT_REF>.supabase.co/functions/v1/account";
const string PublishableKey = "sb_publishable_...";
```

**Para gumamit ng sarili ninyong Supabase project:**

1. Gumawa ng project sa [supabase.com](https://supabase.com). Kopyahin ang **Project ref** (Settings ▸ General) at ang **Publishable key** (Settings ▸ API Keys).
2. I-install ang [Supabase CLI](https://supabase.com/docs/guides/cli), tapos sa loob ng folder na `mindscape-3d`, patakbuhin:

   ```sh
   supabase login
   supabase init                                      # isang beses lang kung wala pang supabase/config.toml
   supabase link --project-ref <PROJECT_REF>
   supabase db push --dry-run --remote                # i-preview ang pending migrations
   supabase db push --remote                          # gagawin/i-update ang tables at functions
   supabase functions deploy account --no-verify-jwt  # ang gateway ng login / sign-up
   supabase secrets set RESEND_API_KEY=<key> MAIL_FROM="Mindscape <no-reply@yourdomain.com>"
   ```

   (Para lang sa email na "na-delete ang account" ang `RESEND_API_KEY` / `MAIL_FROM`, galing sa [Resend](https://resend.com). Kung wala ito, gagana pa rin ang pag-delete, wala lang email.)
3. Sa Supabase dashboard:
   - **Authentication ▸ Sign In / Providers ▸ Email**: i-ON ang **Confirm email**.
   - **Authentication ▸ Email Templates**: sa *Confirm signup* at *Reset password*, ilagay ang `{{ .Token }}` sa mensahe (ito ang 6-digit code na itina-type ng player).
   - **Authentication ▸ SMTP Settings**: maglagay ng sariling SMTP bago gamitin ng totoong players. Ang built-in mailer ay para lamang sa team members at mahigpit ang rate limit.
   - Para sa Google login, sundin ang provider at dalawang redirect setting sa [Supabase Connection Setup and Settings](#workflow-supabase).
4. Ilagay ang bagong ref at key sa tatlong linya ng `MindscapeCloud.cs`, i-save, at i-build ulit ang laro.

> [!WARN] Huwag ilagay ang secret key sa laro
>
> **Publishable** key lang ang ilalagay sa `MindscapeCloud.cs`. Ang service role / secret key ay nasa Supabase lang (kusang binabasa ng edge function).

**Kung ayaw ng online accounts:** puwedeng piliin ng player ang *Play offline*. Sa device lang mase-save ang lahat.

**Para makita ang data ng players:** Supabase dashboard ▸ Table Editor: `players`, `episode_progress`, `journal_entries`, `assessments`, `episode_records`. Ang mga na-delete na account ay may `status = archived` at tuluyang mabubura pagkalipas ng 30 araw. Higit pa: [Accounts, Progress & Saves](#system-accounts).

## 4. Mag-edit ng scene

1. Buksan ang scene mula sa `Assets/Scenes/`.
2. Pumili ng object sa **Hierarchy**, galawin gamit ang **W** (move), **E** (rotate), **R** (scale), at baguhin ang values sa **Inspector**.
3. **Ctrl/Cmd + S** para i-save. Pindutin ang Play para i-test.

| Gusto kong... | Gawin ito |
| --- | --- |
| Ilipat ang tao, item o marker | Piliin sa Hierarchy (nasa `NPC System` ang mga NPC o nakapangalan sa tao) at ilipat |
| Ilipat kung saan nagsisimula ang player | Ilipat ang object na `Player` |
| Baguhin ang city, bahay o school model | I-edit sa Blender, i-export ulit sa parehong file, tapos patakbuhin ang `Mindscape ▸ World / House / School ▸ Sync...` ([Editor Menu Items](#ref-menu-items)) |
| Magdagdag ng NPC | `GameObject ▸ NPC` ([Create an NPC](#workflow-npc)) |
| Magdagdag ng pickup | `GameObject ▸ Collectible` ([Create a Collectible](#workflow-collectible)) |
| Magdagdag ng pinto | `Mindscape ▸ Doors ▸ Apply Doors to Open Scene` ([Doors](#workflow-door)) |

> [!WARN] Binubuo ulit ng Builder menus ang scene
>
> Ang `Mindscape ▸ Chapter N ▸ Build ...` ay gumagawa ulit ng scene mula sa code. **Mawawala lahat ng manual na inilagay ninyo sa scene na iyon.** Kapag nag-edit na kayo ng scene nang manual, huwag nang patakbuhin ulit ang Build menu nito (o gawin ang pagbabago sa builder script sa `Assets/Editor/`). Laging mag-commit sa git muna.

## 5. Baguhin ang kwento, timer at choices

Ang mga story episode ay nakasulat **sa code**, hindi sa scene. Buksan ang script ng episode sa kahit anong editor (VS Code, Rider o Visual Studio):

| Chapter | Mga episode script |
| --- | --- |
| 1 | `Scripts/Chapters/Chapter 1 - Academic Pressure/HouseEpisode.cs`, `ClassroomEpisode.cs`, `CafeteriaEpisode.cs`, `DormitoryEpisode.cs` |
| 2 | `Scripts/Chapters/Chapter 2 - Family Expectations/FamilyAfterSchoolEpisode.cs`, `FamilyMorningEpisode.cs`, `FamilyExamEpisode.cs`, `Scripts/Chapters/Chapter 2 - Family Expectations/FamilyFinaleEpisode.cs` |
| 3 | `Scripts/Chapters/Chapter 3 - Social Dynamics/SocialDynamicsEpisode.cs` (titles/goals sa `SocialDynamicsChapter.cs`) |

- **Linya ng dialogue:** hanapin ang pangungusap sa script at palitan ang text sa loob ng `Say("Pangalan", "text")`, `Me("text")` o `Think("text")`. Sundin ang [Writing Guidelines](#story-tone) (kalmado, hindi nakaka-trigger).
- **Title at briefing ng episode:** `AcademicPressureChapter.cs`, `Scripts/Chapters/Chapter 2 - Family Expectations/FamilyEpisode.cs` (`FamilyExpectationsChapter.Titles`), `SocialDynamicsChapter.cs`.
- **Time limit:** `protected override float TimeLimit => 720;` sa itaas ng bawat episode script (seconds). Default ay 600 sa `AcademicEpisode.cs`.
- **Pagbabago ng stress:** ang mga numero sa `AddStress(...)` / `EaseStress(...)`.

I-save ang file; kusang magre-recompile ang Unity. Tingnan ang **Console** kung may pulang error.

## 6. I-configure ang scripts sa Inspector

Karamihan ng settings ay field ng component: piliin ang object, baguhin ang value sa **Inspector**, i-save ang scene.

| Setting | Saan |
| --- | --- |
| Bilis ng lakad / takbo, camera | object na `Player` ▸ `PlayerMovement` (`moveSpeed`, `runSpeed`) |
| Simulang stress, max stress | `Player` ▸ `PlayerControls` (`stressLevel`, `stressMax`) |
| Pangalan ng NPC, dialogue, stress kada choice | ang NPC ▸ `NPC` ([NPC Dialogue](#system-npc)) |
| Quest goals at timer (prototype scenes) | ang object na `Quest` ([Create a Quest](#workflow-quest)) |
| Anong music sa bawat scene | `Assets/Resources/SceneMusicMap.asset` |
| Music playlist | `Assets/Resources/Music/` ([Music & SFX](#system-audio)) |
| Key bindings | `Assets/Resources/GameControls.inputactions` (i-double-click) |
| Layout ng screen, kulay, font | ang `.uxml` / `.uss` sa `Assets/UI Toolkit/`, buksan sa **Window ▸ UI Toolkit ▸ UI Builder** ([Episode Screens](#system-episode-ui), [UI Theme](#system-theme)) |
| Graphics quality | `Assets/Settings/PC_RPAsset.asset` at `Mobile_RPAsset.asset` |
| Pangalan ng app, version, icon | `Edit ▸ Project Settings ▸ Player` |

May comment sa simula ng bawat script na nagsasabi kung ano ang ginagawa nito. Listahan: [Script Index](#ref-scripts).

## 7. Magdagdag o magtanggal ng episode

Kumpletong checklist: [Create an Episode or Chapter](#workflow-episode-chapter).

1. I-duplicate ang pinakamalapit na episode scene, pangalanang `Chapter N - Episode N`.
2. Kopyahin ang episode script nito, palitan ang pangalan ng class, at baguhin ang text.
3. Idagdag ang pangalan ng scene sa listahan ng chapter (`AcademicPressureChapter.Scenes` at `Titles`, `FamilyExpectationsChapter.Scenes` sa `FamilyEpisode.cs`; sa Chapter 3, `EpisodeCount` at `Titles` sa `SocialDynamicsChapter.cs`) para lumabas sa main menu.
4. Idagdag ang scene sa **File ▸ Build Profiles ▸ Scene List**.

Detalye: [Create a Gameplay Scene](#workflow-scene).

## 8. Mag-build at mag-publish

| Target | Paano |
| --- | --- |
| Android APK | `File ▸ Build Profiles ▸ Android ▸ Switch Platform`, tapos **Build** |
| Web (WebGL) | Ganoon din sa **Web**. I-upload ang output folder sa kahit anong static host (nasa Vercel ito ngayon) |
| Windows / Mac | Ganoon din sa **Windows** / **macOS** |

Bago i-release sa Play Store: palitan ang package name (template pa ngayon, `com.UnityTechnologies...`) at gumawa ng release keystore sa **Project Settings ▸ Player ▸ Publishing Settings**.

Docs site: `cd docs && npm install && npm run dev` para i-preview, `npm run build` para sa production, at `vercel --prod` para i-deploy. Ang mga pahina ay Markdown files sa `Documents/Website/src/content/docs/`.

## 9. Kapag may sira

| Problema | Ayos |
| --- | --- |
| Pink ang materials | Maling render pipeline: tingnan kung URP asset sa `Assets/Settings/` ang gamit sa `Edit ▸ Project Settings ▸ Graphics` |
| "Missing script" sa object | Na-rename ang script o nawala ang `.meta` file. I-restore mula sa git |
| Login: "email not confirmed" | Kailangang ilagay ng player ang 6-digit code. Siguraduhing may `{{ .Token }}` ang email template |
| Walang dumarating na sign-up email | Limit ng built-in mailer: maglagay ng custom SMTP (step 3) |
| Nawala ang binago sa scene | Nabuo ulit ng Build menu (babala sa step 4). I-restore mula sa git |
| Build: "scripts are compiling" | Hintaying tumigil ang spinner (kanang ibaba) pagkatapos mag-switch platform, tapos mag-build ulit |

> [!TIP] Tandaan
>
> Mag-commit sa git bago ang bawat malaking pagbabago. Kung kailangang maglipat ng file, ilipat **sa loob ng Unity** (Project window), hindi sa Finder, para sumama ang `.meta` file nito.
