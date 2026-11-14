---
id: release-checklist
group: Build & Deploy
nav: Release checklist
---

# Release Checklist

Go through this list for every release.

- [ ] All tester-list items for this release are fixed and re-tested
- [ ] Console has no errors; all 22 scenes are enabled in Build Profiles
- [ ] Version and Android version code raised
- [ ] Unity closed → four builds run → each log ends with `Build Finished, Result: Success`
- [ ] APK installed on a phone; macOS and Windows builds launched once
- [ ] WebGL synced to `Builds/webgl-play` → `vercel --prod` → `.br` headers checked
- [ ] Native downloads uploaded; website links updated; `Site/` redeployed
- [ ] Supabase migrations and the `account` function up to date (if the backend changed)
- [ ] Documentation pages updated for anything that changed
- [ ] Changes committed and pushed (builds stay out of git)
