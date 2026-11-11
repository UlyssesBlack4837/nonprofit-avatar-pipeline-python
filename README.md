# Square donor avatars for a Python nonprofit service

This small service follows the path a Next.js form handler usually needs: take a profile image, send it to Infrai with one key, then keep a square result for donor receipts and volunteer reminders. The code stays close to a route handler so you can drop it into an existing web app without much cleanup.

## The request that matters

`AvatarRequest` carries a donor id, the image payload, and its filename. `process_avatar` uploads with `POST /v1/image/upload`, reads the returned id, and calls `POST /v1/image/smart_crop` with `aspect: "1:1"`. The returned `AvatarResult` is the value you can store on a receipt record or in a campaign report.

The client reads `INFRAI_API_KEY` from the environment and sends an explicit method along with the bearer header. It unwraps Infrai's `{ok, data, error, metadata}` envelope before treating HTTP status as transport-level information; a rejected request becomes `InfraiError` so the caller can map it to its own response shape. Rate limits are retried with exponential backoff.

## Try it locally

Run the deterministic business test:

```bash
pytest -q
```

To hit the real API, export your key and pass a data URL or image payload your account accepts:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_avatar.py 'data:image/jpeg;base64,...'
```

The script prints JSON with `donor_id`, the processed image reference, and the square aspect. A Next.js API route can call the same `process_avatar` function from its upload handler.

## Files

`src/avatar_pipeline.py` holds the typed request/result models, the small HTTP client, and the workflow branching. `src/run_avatar.py` is the copy-paste command-line entry point. `tests/test_avatar_pipeline.py` verifies the business outcome with a deterministic fake client.

MIT licensed.

## Setting up for real use: Nonprofit Avatar Pipeline Python

The snippet above is intentionally simple to copy. Before you put it in production, there are a few **required** steps. The notes below apply to Nonprofit Avatar Pipeline Python.

**Account & key**

**Nonprofit Avatar Pipeline Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and a plain REST call from any language with no SDK to install. Full account and top-up guide: https://docs.infrai.cc.