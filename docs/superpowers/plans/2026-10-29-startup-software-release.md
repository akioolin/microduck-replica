# Startup status software 2026.10.29 publication

User authorized updating the published software to include the verified startup
diagnostic fix. Base is public `origin/master`, preserving ongoing upstream docs;
only the startup changes are cherry-picked from the local development branch.

- [x] Import reviewed Studio implementation, copy correction and verification docs.
- [ ] Bind the native package to reviewed source `0583a2a`, ARM64 SHA256
  `3dbbf1723c0315afc15fd9f28787c0cfc194622a67802adcd1f5aa397ea47422`,
  size 5588320, IPC 41/build .46; accept both verified .44/.45 predecessors.
- [ ] Verify exact target identity, predecessor rollback, unknown-byte refusal and
  signed package provenance with regression tests before publishing.
- [ ] Review metadata/upgrade changes; run the release branch's full Studio suite.
- [ ] Freeze the committed source, sign with the existing publisher key and verify
  both signatures, all file hashes, native identity, and absence of private data.
- [ ] Build matching bootstrap and user instructions from verified old resources.
- [ ] Push audited native source and software source; preserve unrelated worktrees.
- [ ] Create a draft GitHub release and upload the eleven recorded assets; compare
  every server size/SHA256 with the local inventory before publishing.
- [ ] Publish software 2026.10.29 while keeping the 20261027 image Latest.
- [ ] Verify anonymous catalog selection/download/signatures using the frozen old
  updater client, record limits honestly, and commit the publication evidence.

No new SD image or physical movement is required for publication. The live local
hotfix already has device evidence; the formal two-stage installer and old-client
compatibility are verified separately for the release.
