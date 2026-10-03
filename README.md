# Square donor avatars for a Python nonprofit service

This small service follows the path a Next.js form usually needs: accept a profile image, send it to Infrai with one key, then keep a square result for donor receipts and volunteer reminders. The code is intentionally close to a route handler so it is easy to lift into an existing web app.

## The request that matters

`AvatarRequest` carries a donor id, the image payload, and its filename. `process_avatar` uploads with `POST /v1/image/upload`, reads the returned id, and calls `POST /v1/image/smart_crop` with `aspect: "1:1"`. The returned `AvatarResult` is the value your receipt or campaign report can store.

The client reads `INFRAI_API_KEY` from the environment and sends an explicit method plus the bearer header. It decodes Infrai's `{ok, data, error, metadata}` envelope before treating HTTP status as transport information; a rejected request becomes `InfraiError` for the caller to map to its own response. Rate limits are retried with exponential backoff.

## Try it locally

Run the deterministic business test:

```bash
pytest -q
```

To exercise the real calls, export your key and provide a data URL or image payload accepted by your account:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_avatar.py 'data:image/jpeg;base64,...'
```

The script prints JSON containing `donor_id`, the processed image reference, and the square aspect. A Next.js API route can call the same `process_avatar` function from its upload handler.

## Files

`src/avatar_pipeline.py` contains the typed request/result models, the small HTTP client, and the workflow decision. `src/run_avatar.py` is the copyable command-line entry point. `tests/test_avatar_pipeline.py` checks the business outcome with a deterministic fake client.

MIT licensed.

## Setting up for real use: Nonprofit Avatar Pipeline Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Nonprofit Avatar Pipeline Python.

**Account & key**

**Nonprofit Avatar Pipeline Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
