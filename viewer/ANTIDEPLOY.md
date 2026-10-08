# Antideploy deployment — walkthrough preview

This remains an **engineering preview**, not a completed property walkthrough. Targeted collision/material repairs are described in `ASSET_REPAIRS.md`; exact Blender parity and physical-device performance testing are still required. Hosting the preview does not bypass the customer-release gate.

## Build and runtime

Upload the `viewer` directory as the project root. Antideploy can recognize the existing Next.js package scripts without a custom Dockerfile:

- Install: `npm ci`
- Build: `npm run build`
- Runtime: `npm start` (`next start --hostname 0.0.0.0` honors the platform's `PORT` environment variable)
- Node.js: 22+; locally tested with Node 24
- Required secrets: **none**
- Required database: **none**
- Do not enable `NEXT_PUBLIC_ENABLE_DEBUG` on the publicly hosted preview.

For a future GitHub-connected monorepo application, set Antideploy `rootDirectory` to `viewer`. A directory-archive application already uploads `viewer` as its root and needs no monorepo setting. Directory uploads do not automatically establish a GitHub deployment integration.

## Large assets: verified build-time retrieval

Antideploy's public API advertises a maximum upload total and file size of **29,360,128 bytes (28 MiB)**. The original visual GLB is **129,077,104 bytes**, so uploading the exported assets with the source is not supported.

`npm run build` invokes `prebuild`, which runs `scripts/ensure-assets.mjs` followed by `scripts/derive-assets.mjs`:

1. Read `scripts/asset-manifest.json`, pinned to export commit `309f90e525a28975980f043c259c57ce773a2976`.
2. Reuse only files whose size and SHA-256 match the approved manifest.
3. Fetch missing visual GLB from GitHub's LFS media endpoint, and the collision GLB/room/spawn JSON from the corresponding pinned raw GitHub commit.
4. Stream each response to a temporary file, enforce its expected size, verify SHA-256, then atomically rename it into `.asset-cache`.
5. Fail the build if a download or verification fails. No placeholder files, geometry simplification, guessed model URL, or silent version mixing.

After source verification, derivation restores source palette fallbacks, box-projects existing images lacking UVs, caps embedded images at 1024px, and creates separate corrected structural collision geometry. It writes the runtime size/SHA manifest before Next compilation.

The deployed Next server serves these derived assets locally under `/assets/`. Asset retrieval requires outbound access to `media.githubusercontent.com` and `raw.githubusercontent.com` on the Antideploy build worker. No GitHub token is needed for this public repository. A future approved export replacement must update the manifest's commit/size/checksum together; the script intentionally rejects unapproved local replacements.

## Safe archive

```sh
cd viewer
npm run deploy:package
```

This writes `/tmp/farmhouse-antideploy.tar.gz`, or use an explicit destination:

```sh
node scripts/package-antideploy.mjs /tmp/farmhouse-preview.tar.gz
```

Excludes `node_modules`, `.next`, `.git`, generated `public/assets`, `.asset-cache`, browser screenshots, `.env*` and TypeScript incremental build files. The source archive is far below the upload limit. The complete built asset payload will be larger; platform build/static-serving limits must be verified by the actual deployment, not inferred from source-upload acceptance.

## Connection and deployment

Follow https://antideploy.com/agent.md and the current API reference at https://antideploy.com/api/v1.

- Connect with the device approval flow. An OpenRouter AI key is not an Antideploy account token and is not needed by this viewer.
- Store the granted Antideploy account token only in `~/.antideploy/config.json`, file mode `0600`; never put it in Git, the deployment archive, terminal output or browser code.
- Create/read the intended application using that authorization. Save its non-secret `applicationId` as `.antideploy.json` only after the application actually exists.
- Confirm the public subdomain with the owner before first deployment, check availability, and configure it on the application.
- Upload the source archive with `POST /api/v1/deploy?applicationId=<id>` as multipart field `archive`.
- Watch the returned task until it succeeds or fails. A queued upload is not a live deployment.
- If failed, inspect `error`, `failedStep`, build/runtime logs and fix the cause before retrying. Do not repeatedly redeploy unchanged code or ignore account/plan restrictions.
- After success, verify the site and all four `/assets/` responses, confirm the public viewer works, and read the automatic security result. Report the live URL **and the connected account**, and disclose any security findings.

No unnecessary database, AI key, storage bucket or paid service is provisioned by this configuration. This document is deployment preparation—not evidence of a successful live deployment. Final deployment status is reported separately after account approval and live verification.


## Current preview deployment

URL: https://rewari-farmhouse-5bhk.antideploy.app

Application ID: `b2abee02-cb3c-4c40-81da-5d77ee573582`. Deployment task: `a2fa54f2-c0b7-456f-b053-12fb94048b6b`. Platform status: **succeeded**. This is a directory-upload deployment, not automatic deployment on GitHub pushes.

The public HTML and all four original asset files returned HTTP 200 with checksum/size verification. Cloudflare rejected the Python-default user agent with error 1010; browser-identifying HTTP requests succeeded. The initial check reached the public interface but did not visually verify live 3D interaction. Canvas fallback text in DOM extraction was not reliable evidence of graphics availability; subsequent hotfix verification rendered the actual scene successfully. Earlier local software-WebGL tests remain documented separately.

Automatic platform scan found no blocking public-security issues and one low-severity missing-security-headers finding. Security-header hardening is a follow-up, not silently reported as fixed. The original asset release blockers and real-device performance acceptance remain pending. See `reports/antideploy-deployment.json`.


## Loading hotfix — live

Deployment task `00ed7d74-82c2-40c6-a25f-c71ec6c6b73a` succeeded at the same public URL. The live browser showed the download advancing through 76% / 109.6 MB, completed loading, rendered the 3D entrance, acquired pointer lock and accepted W movement and mouse-look without page errors. Screenshots of the entrance and changed exploration view were inspected. Versioned asset responses return `Cache-Control: public, max-age=31536000, immutable`. The original full-property/device acceptance blockers are unchanged.
