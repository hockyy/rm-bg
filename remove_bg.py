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
OUTPUT_SUFFIX = "_rm_bg"


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


def _save_image(image, path: Path) -> Path:
    ext = path.suffix.lower()
    try:
        if ext in (".jpg", ".jpeg"):
            rgb = image.convert("RGB")
            rgb.save(path, "JPEG", quality=95, optimize=True)
        elif ext == ".webp":
            image.save(path, "WEBP", lossless=True, method=6)
        elif ext == ".avif":
            image.save(path, "AVIF", quality=90)
        else:
            image.save(path, "PNG", optimize=True)
    except Exception:
        if ext == ".png":
            raise
        fallback = path.with_suffix(".png")
        image.save(fallback, "PNG", optimize=True)
        return fallback
    return path


def _output_extension(input_path: Path, format_override: str | None) -> str:
    if format_override:
        return f".{format_override.lstrip('.')}"
    ext = input_path.suffix.lower()
    if ext in OUTPUT_EXTENSIONS:
        return ext
    return ".png"


def _default_output_path(input_path: Path, format_override: str | None = None) -> Path:
    ext = _output_extension(input_path, format_override)
    return input_path.with_name(f"{input_path.stem}{OUTPUT_SUFFIX}{ext}")


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
    saved_path = _save_image(result, output_path)
    return saved_path


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
        default=None,
        help="Output format when --output is not set (default: same as input)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress popup notifications",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    raw_argv = argv if argv is not None else sys.argv[1:]
    if not raw_argv:
        _show_message(
            "Remove Background",
            "No image file was provided.\n\n"
            "Re-run register_context_menu.bat if this keeps happening.",
            error=True,
        )
        return 1

    try:
        args = _parse_args(raw_argv)
    except SystemExit:
        _show_message(
            "Remove Background",
            "Invalid arguments.\n\nUsage: remove_bg.py image1 [image2 ...]",
            error=True,
        )
        return 1

    inputs = [Path(p.strip('"')) for p in args.inputs]

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
            else:
                output_path = _default_output_path(input_path, args.format)

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
                    f"Saved {len(succeeded)} file(s) with '{OUTPUT_SUFFIX}' suffix.",
                )

    return 0 if not failed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        _show_message("Remove Background", f"Unexpected error:\n{exc}", error=True)
        raise SystemExit(1)
