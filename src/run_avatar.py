import json
import sys

from avatar_pipeline import AvatarRequest, InfraiClient, process_avatar


def main() -> None:
    image = sys.argv[1] if len(sys.argv) > 1 else "data:image/jpeg;base64,REPLACE_WITH_IMAGE"
    result = process_avatar(AvatarRequest("donor-42", image, "donor-42.jpg"), InfraiClient())
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
