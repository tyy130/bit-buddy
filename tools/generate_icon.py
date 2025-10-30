#!/usr/bin/env python3
"""
Simple icon generator for Bit Buddy
Creates a basic placeholder icon with personality
"""

from PIL import Image, ImageDraw
import os


def create_buddy_icon(output_path, size=256, personality="curious"):
    """Create a Bit Buddy icon based on personality type"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Personality-based color schemes
    colors = {
        "curious": {"bg": (52, 152, 219), "accent": (41, 128, 185)},
        "playful": {"bg": (155, 89, 182), "accent": (142, 68, 173)},
        "organized": {"bg": (46, 204, 113), "accent": (39, 174, 96)},
        "wise": {"bg": (230, 126, 34), "accent": (211, 84, 0)},
    }

    scheme = colors.get(personality, colors["curious"])

    # Background circle with gradient effect
    margin = size // 8
    for i in range(5):
        offset = margin + i * size // 40
        color = (
            scheme["bg"][0],
            scheme["bg"][1],
            scheme["bg"][2],
            255 - i * 30,
        )
        draw.ellipse(
            [offset, offset, size - offset, size - offset], fill=color
        )

    # Inner accent circle
    inner_margin = margin * 2
    draw.ellipse(
        [
            inner_margin,
            inner_margin,
            size - inner_margin,
            size - inner_margin,
        ],
        fill=(
            scheme["accent"][0],
            scheme["accent"][1],
            scheme["accent"][2],
            100,
        ),  # noqa: E501
    )

    # Eyes (simple dots)
    eye_y = size // 3
    eye_size = size // 20
    for x_pos in [size // 3, 2 * size // 3]:
        draw.ellipse(
            [
                x_pos - eye_size,
                eye_y,
                x_pos + eye_size,
                eye_y + eye_size * 2,
            ],
            fill=(255, 255, 255, 255),
        )
        # Pupils
        pupil_offset = eye_size // 2
        draw.ellipse(
            [
                x_pos - pupil_offset,
                eye_y + pupil_offset,
                x_pos + pupil_offset,
                eye_y + pupil_offset + eye_size,
            ],
            fill=(0, 0, 0, 255),
        )

    # Smile (personality-dependent)
    mouth_y = size // 2
    mouth_width = size // 3
    mouth_height = size // 6
    if personality == "playful":
        # Wide grin
        draw.arc(
            [
                size // 3,
                mouth_y,
                2 * size // 3,
                mouth_y + mouth_height,
            ],
            0,
            180,
            fill=(255, 255, 255, 255),
            width=size // 32,
        )
    elif personality == "wise":
        # Gentle smile
        draw.arc(
            [
                size // 3 + mouth_width // 4,
                mouth_y,
                2 * size // 3 - mouth_width // 4,
                mouth_y + mouth_height // 2,
            ],
            0,
            180,
            fill=(255, 255, 255, 255),
            width=size // 40,
        )
    else:
        # Regular smile
        draw.arc(
            [
                size // 3,
                mouth_y,
                2 * size // 3,
                mouth_y + mouth_height // 2,
            ],
            0,
            180,
            fill=(255, 255, 255, 255),
            width=size // 35,
        )

    # Digital accent (sparkle for curious)
    if personality == "curious":
        sparkle_size = size // 16
        sparkle_pos = [
            (size // 6, size // 6),
            (5 * size // 6, size // 6),
            (size // 6, 5 * size // 6),
        ]
        for x, y in sparkle_pos:
            draw.line(
                [x - sparkle_size, y, x + sparkle_size, y],
                fill=(255, 255, 255, 200),
                width=size // 80,
            )
            draw.line(
                [x, y - sparkle_size, x, y + sparkle_size],
                fill=(255, 255, 255, 200),
                width=size // 80,
            )

    img.save(output_path, "PNG")
    return img


def main():
    """Generate all required icon sizes"""
    os.makedirs("assets", exist_ok=True)

    print("🎨 Generating Bit Buddy icons...")

    # Create base 256x256 icon (curious personality by default)
    base_icon = create_buddy_icon("assets/buddy_icon.png", 256, "curious")
    print("✅ Created assets/buddy_icon.png (256x256)")

    # Create additional sizes for multi-size .ico
    sizes = [16, 32, 48, 64, 128, 256]
    icon_images = []

    for size in sizes:
        img = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        icon_images.append(img)

    # Save as multi-size ICO (Windows)
    try:
        icon_images[0].save(
            "assets/buddy_icon.ico",
            format="ICO",
            sizes=[(s, s) for s in sizes],
        )
        print("✅ Created assets/buddy_icon.ico (multi-size)")
    except Exception as e:
        print(f"⚠️  Could not create .ico: {e}")
        print("   Please use an online converter or Windows tool")

    # For macOS, create iconset (requires iconutil to convert to .icns)
    iconset_dir = "assets/buddy_icon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)

    icns_sizes = [
        (16, "16x16"),
        (32, "16x16@2x"),
        (32, "32x32"),
        (64, "32x32@2x"),
        (128, "128x128"),
        (256, "128x128@2x"),
        (256, "256x256"),
        (512, "256x256@2x"),
        (512, "512x512"),
        (1024, "512x512@2x"),
    ]

    for size, name in icns_sizes:
        img = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        img.save(f"{iconset_dir}/icon_{name}.png", "PNG")

    print(f"✅ Created iconset directory: {iconset_dir}")
    print(
        "   Run 'iconutil -c icns assets/buddy_icon.iconset' "
        "on macOS to create .icns"
    )

    # Summary
    print("\n📋 Icon Summary:")
    print("   - buddy_icon.png: Base 256x256 icon (all platforms)")
    print("   - buddy_icon.ico: Windows multi-size icon (if created)")
    print("   - buddy_icon.iconset/: macOS iconset " "(convert with iconutil)")

    print("\n🎯 Next Steps:")
    print("   1. Review the generated icon")
    print("   2. Customize colors/style in this script if desired")
    print(
        "   3. Convert iconset to .icns on macOS: "
        "iconutil -c icns assets/buddy_icon.iconset"
    )
    print("   4. Build executable: pyinstaller buddy.spec")


if __name__ == "__main__":
    main()
