
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.dimensions import dimensions_loader


def main():

    print("\n========================================")
    print("  DIMENSIONS LOADER TEST")
    print("========================================")

    platforms = dimensions_loader.get_all_platforms()

    print("\nAvailable Platforms:")

    for platform, details in platforms.items():
        print(f"\n{details['display_name']}")

        for placement, data in details["placements"].items():
            print(
                f"  {placement}: "
                f"{data['width']}x{data['height']}"
            )

    print("\nTesting individual placement...")

    placement = dimensions_loader.get_placement(
        platform="instagram",
        placement="story",
    )

    print("\nSelected Placement:")
    print(placement)

    print("\nTotal Placements:",
          len(dimensions_loader.get_all_placements()))

    print("\nDIMENSIONS LOADER TEST SUCCESSFUL")


if __name__ == "__main__":
    main()
