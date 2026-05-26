#!/usr/bin/env python3
"""Remove image backgrounds using rembg (U2-Net). Supports PNG, JPG, WebP, AVIF, and more."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}

OUTPUT_EXTENSIONS = {".avif", ".jpeg", ".jpg", ".png", ".webp"}


def _register_avif_plugin() -> None:
    try:
        import pillow_avif  # noqa: F401
    except ImportError:
        pass


def _load_image(path: Path):
    from PIL import Image

    _register_avif_plugin()
    with Image.open(path) as img:
        if img.mode in ("RGBA", "RGB"):
            return img.convert("RGBA")
        return img.convert("RGBA")


def _save_image(image, path: Path) -> None:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        rgb = image.convert("RGB")
        rgb.save(path, "JPEG", quality=95, optimize=True)
    elif ext == ".webp":
        image.save(path, "WEBP", lossless=True, method=6)
    elif ext == ".avif":
        image.save(path, "AVIF", quality=90)
    else:
        image.save(path, "PNG", optimize=True)


def _default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_nobg.png")


def remove_background(input_path: Path, output_path: Path | None = None) -> Path:
    from rembg import remove

    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{input_path.suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if output_path is None:
        output_path = _default_output_path(input_path)
    else:
        output_path = Path(output_path)
        if output_path.suffix.lower() not in OUTPUT_EXTENSIONS:
            raise ValueError(
                f"Unsupported output format '{output_path.suffix}'. "
                f"Use: {', '.join(sorted(OUTPUT_EXTENSIONS))}"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = _load_image(input_path)
    result = remove(image)
    _save_image(result, output_path)
    return output_path


def _show_message(title: str, message: str, error: bool = False) -> None:
    if sys.platform == "win32":
        import ctypes

        icon = 0x10 if error else 0x40  # MB_ICONERROR / MB_ICONINFORMATION
        ctypes.windll.user32.MessageBoxW(0, message, title, icon)
    else:
        stream = sys.stderr if error else sys.stdout
        print(f"{title}: {message}", file=stream)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove background from images (PNG, JPG, WebP, AVIF, etc.)."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="One or more image file paths",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (only valid for a single input file)",
    )
    parser.add_argument(
        "--format",
        choices=sorted(ext.lstrip(".") for ext in OUTPUT_EXTENSIONS),
        default="png",
        help="Output format when --output is not set (default: png)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress popup notifications",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    inputs = [Path(p) for p in args.inputs]

    if args.output and len(inputs) > 1:
        _show_message("Remove Background", "--output works with a single input file only.", error=True)
        return 1

    succeeded: list[Path] = []
    failed: list[tuple[Path, str]] = []

    for input_path in inputs:
        try:
            if not input_path.is_file():
                raise FileNotFoundError(f"File not found: {input_path}")

            if args.output:
                output_path = Path(args.output)
            elif len(inputs) == 1:
                output_path = input_path.with_name(
                    f"{input_path.stem}_nobg.{args.format}"
                )
            else:
                output_path = input_path.with_name(
                    f"{input_path.stem}_nobg.{args.format}"
                )

            result = remove_background(input_path, output_path)
            succeeded.append(result)
        except Exception as exc:  # noqa: BLE001 - surface errors to the user
            failed.append((input_path, str(exc)))

    if not args.quiet:
        if failed and not succeeded:
            _show_message(
                "Remove Background",
                "Failed:\n" + "\n".join(f"{p.name}: {err}" for p, err in failed),
                error=True,
            )
        elif failed:
            _show_message(
                "Remove Background",
                f"Done {len(succeeded)} file(s).\n"
                f"Failed {len(failed)} file(s):\n"
                + "\n".join(f"{p.name}: {err}" for p, err in failed),
                error=True,
            )
        else:
            if len(succeeded) == 1:
                _show_message(
                    "Remove Background",
                    f"Saved:\n{succeeded[0]}",
                )
            else:
                _show_message(
                    "Remove Background",
                    f"Saved {len(succeeded)} file(s) with '_nobg' suffix.",
                )

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
