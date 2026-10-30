# Apply the screenshot-style profile

This version follows the supplied reference: monochrome hands banner, centered introduction, animated typing line, About Me with an astronaut, social icons, two rows of technology icons, selected projects, contribution stats, an activity graph, and an animated contribution calendar.

## Upload

1. Extract the ZIP.
2. Open https://github.com/yedmahos/yedmahos.
3. Choose Add file, then Upload files.
4. Upload README.md and the complete assets folder. Commit the changes. These replace the earlier README and graphics.
5. Open https://github.com/yedmahos to view the profile.

The README follows your visitor's GitHub appearance. To view the whole page like the dark screenshot on your own account, select a dark theme under GitHub Settings → Appearance.

## Automatic stats updates

The included cards already contain real data captured from your public contribution calendar. To refresh them daily:

1. Upload the scripts folder.
2. In your repository, use Add file → Create new file and enter `.github/workflows/profile-stats.yml` as the filename. Copy the contents of the matching file in this ZIP, then commit. This avoids Windows hiding the `.github` folder during upload.
3. Open the Actions tab. If GitHub asks to enable workflows, enable them.
4. Select Refresh profile stats, then Run workflow to verify the first update. Scheduled runs use the default branch and can run later than their scheduled time.

The workflow uses the repository's standard GITHUB_TOKEN through checkout to commit updated cards. No personal access token or third-party card service is required. If repository rules prevent automated pushes, permit this workflow or run `python3 scripts/update_stats.py --user yedmahos` locally and commit the resulting assets yourself.

Cards show the public calendar, not private contributions that GitHub withholds. Current streak accepts activity today or yesterday in UTC; longest streak is measured within the displayed calendar year, not account lifetime. The line graph covers the last 30 days. A failed refresh leaves the last successful cards available.

## Contents

- README.md: profile content.
- assets/: original reference artwork, local icons, animation, contribution data and cards.
- scripts/update_stats.py: fetches the public GitHub calendar and redraws the cards.
- .github/workflows/profile-stats.yml: daily update workflow.
- Preview.png: a rendered preview. You do not need to upload it.
- SETUP.md: this guide. You do not need to upload it.

All five selected projects are linked to your repositories: Dharitri, Exam Portal SE, Limitu, SIH / Trinetraa, and Portfolio. The bio uses details supported by your repositories and does not copy the reference author's education or backend experience claims. GitHub, LinkedIn and email links use your existing public profile details.

Artwork and layout reference: https://github.com/midnightshady/midnightshady. Skill Icons attribution and license are preserved in assets/icons/LICENSE.
