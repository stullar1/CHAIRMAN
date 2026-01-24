"""
Generate app icons for CHAIRMAN
Creates .ico (Windows) and .icns (macOS) from a base image

To use with a custom icon:
1. Replace 'icon_base.png' with your 1024x1024 PNG image
2. Run this script: python generate_icons.py
"""

import struct
import zlib
from pathlib import Path


def create_simple_icon_png(size: int = 256) -> bytes:
    """Create a simple colored square PNG as placeholder icon."""
    # Dark purple/blue gradient-like color (#5865F2 - Discord-like blue)
    r, g, b = 88, 101, 242

    # PNG header
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (image header)
    width = size
    height = size
    bit_depth = 8
    color_type = 2  # RGB
    ihdr_data = struct.pack('>IIBBBBB', width, height, bit_depth, color_type, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # IDAT chunk (image data)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filter byte (none)
        for x in range(width):
            # Create a simple gradient/rounded effect
            cx, cy = width // 2, height // 2
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            max_dist = (cx ** 2 + cy ** 2) ** 0.5

            # Rounded rectangle effect
            margin = size // 8
            if x < margin or x >= width - margin or y < margin or y >= height - margin:
                # Transparent-ish edge (darker)
                raw_data += bytes([r // 2, g // 2, b // 2])
            else:
                # Main color with slight gradient
                factor = 1.0 - (dist / max_dist) * 0.2
                raw_data += bytes([int(r * factor), int(g * factor), int(b * factor)])

    compressed = zlib.compress(raw_data, 9)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)

    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

    return signature + ihdr_chunk + idat_chunk + iend_chunk


def create_ico(sizes: list[int] = None) -> bytes:
    """Create a Windows .ico file with multiple sizes."""
    if sizes is None:
        sizes = [16, 32, 48, 256]

    images = []
    for size in sizes:
        png_data = create_simple_icon_png(size)
        images.append((size, png_data))

    # ICO header
    ico_header = struct.pack('<HHH', 0, 1, len(images))  # Reserved, Type (1=ICO), Count

    # Calculate offsets
    header_size = 6 + len(images) * 16
    offset = header_size

    # Directory entries and image data
    directory = b''
    image_data = b''

    for size, png_data in images:
        # Directory entry (16 bytes each)
        width = size if size < 256 else 0
        height = size if size < 256 else 0
        directory += struct.pack(
            '<BBBBHHII',
            width,      # Width (0 = 256)
            height,     # Height (0 = 256)
            0,          # Color palette
            0,          # Reserved
            1,          # Color planes
            32,         # Bits per pixel
            len(png_data),  # Size of image data
            offset      # Offset to image data
        )
        image_data += png_data
        offset += len(png_data)

    return ico_header + directory + image_data


def create_icns(sizes: list[int] = None) -> bytes:
    """Create a macOS .icns file with multiple sizes."""
    if sizes is None:
        sizes = [16, 32, 128, 256, 512]

    # ICNS type codes for different sizes
    type_codes = {
        16: b'icp4',   # 16x16 PNG
        32: b'icp5',   # 32x32 PNG
        64: b'icp6',   # 64x64 PNG
        128: b'ic07',  # 128x128 PNG
        256: b'ic08',  # 256x256 PNG
        512: b'ic09',  # 512x512 PNG
        1024: b'ic10', # 1024x1024 PNG
    }

    icons_data = b''
    for size in sizes:
        if size in type_codes:
            png_data = create_simple_icon_png(size)
            type_code = type_codes[size]
            # Each icon: type (4 bytes) + length (4 bytes) + data
            icons_data += type_code + struct.pack('>I', len(png_data) + 8) + png_data

    # ICNS header: 'icns' + total length
    total_length = 8 + len(icons_data)
    return b'icns' + struct.pack('>I', total_length) + icons_data


def main():
    """Generate icon files."""
    icons_dir = Path(__file__).parent

    # Generate Windows ICO
    ico_path = icons_dir / 'app_icon.ico'
    ico_data = create_ico([16, 32, 48, 256])
    with open(ico_path, 'wb') as f:
        f.write(ico_data)
    print(f"Created: {ico_path}")

    # Generate macOS ICNS
    icns_path = icons_dir / 'app_icon.icns'
    icns_data = create_icns([16, 32, 128, 256, 512])
    with open(icns_path, 'wb') as f:
        f.write(icns_data)
    print(f"Created: {icns_path}")

    print("\nPlaceholder icons created!")
    print("To use custom icons, replace these files with your own .ico and .icns files.")


if __name__ == '__main__':
    main()
