from src.avatar_pipeline import AvatarRequest, InfraiClient, process_avatar


class FakeClient:
    def __init__(self):
        self.deleted = []

    def upload(self, image, filename):
        assert filename.endswith(".jpg")
        return {"image_id": "uploaded-1"}

    def smart_crop(self, image, aspect):
        assert image == "uploaded-1"
        assert aspect == "1:1"
        return {"url": "cropped-1", "image_id": "transient-1"}

    def delete(self, image_id):
        self.deleted.append(image_id)


def test_donor_avatar_is_square_after_processing():
    client = FakeClient()
    result = process_avatar(AvatarRequest("donor-7", "data:image", "avatar.jpg"), client)
    assert result.donor_id == "donor-7"
    assert result.image == "cropped-1"
    assert result.aspect == "1:1"
    assert client.deleted == ["uploaded-1"]


def test_upload_is_deleted_when_crop_fails():
    class FailingClient(FakeClient):
        def smart_crop(self, image, aspect):
            raise ValueError("crop failed")

    client = FailingClient()
    try:
        process_avatar(AvatarRequest("donor-7", "data:image", "avatar.jpg"), client)
    except ValueError:
        pass
    else:
        raise AssertionError("crop should fail")
    assert client.deleted == ["uploaded-1"]


def test_crop_sends_image_reference():
    client = InfraiClient(api_key="test-key")
    calls = []
    client._post = lambda path, payload: calls.append((path, payload)) or {}
    client.smart_crop("uploaded-1", "1:1")
    assert calls == [("/v1/image/smart_crop", {"image": {"image_id": "uploaded-1"}, "aspect": "1:1"})]
