# TODO - Vulnerability fix + Vercel deploy readiness

## Step 1: Implement secure pickle loading (backward compatible)
- Update `src/cloud_storage/aws_storage.py`
- Keep compatibility with existing S3 models by still supporting pickle *only after safety checks*
- Add explicit trust gate via env var (e.g., `MODEL_TRUSTED=1`) to avoid silent RCE in untrusted environments
- Add clearer error messaging for untrusted runtime

## Step 2: Vercel/runtime verification
- Verify model prediction path still works with trusted gate enabled
- Ensure no behavior changes in the happy path

## Step 3: Tests
- Run `pytest`
- Run a minimal import/smoke check for the FastAPI app

## Step 4: GitHub push
- Create branch `vulnfix-vercel`
- Commit changes
- Push to GitHub

## Step 5: Vercel deployment notes
- Confirm `vercel.json` entrypoint and routing
- Provide required Vercel env vars list

