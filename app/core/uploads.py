from __future__ import annotations

import mimetypes
import time
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.errors import DomainError


# ---------------- КОНФИГУРАЦИЯ ----------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_ROOT = BASE_DIR / "uploads"
UPLOAD_ROOT.mkdir(exist_ok=True, parents=True)

# Карта логических типов в подкаталоги (если захочешь использовать)
UPLOAD_PATH_MAP: dict[str, str] = {
    "logos": "logos",
    "company_logos": "company_logos",
    "project_gallery": "project_gallery",
    "user_avatars": "user_avatars",
}

ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_PDF_TYPES: set[str] = {"application/pdf"}

IMAGE_MAX_MB = 2
PDF_MAX_MB = 10

CHUNK_SIZE = 1024 * 64  # 64 КБ


# ---------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------------


def _validate_mime_type(upload_file: UploadFile) -> str:
    """
    Определяет и валидирует MIME-тип файла по расширению.
    Возвращает строку MIME-типа или кидает DomainError при неверном типе.
    """
    mime_type, _ = mimetypes.guess_type(upload_file.filename)

    allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES
    if not mime_type or mime_type not in allowed_types:
        raise DomainError(
            code="invalid_file_type",
            message=(
                f"Недопустимый формат файла ({mime_type or 'неизвестен'}). "
                f"Разрешены: {', '.join(sorted(allowed_types))}"
            ),
            status=400,
        )

    return mime_type


def _validate_file_size(file_size: int, max_mb: int) -> None:
    """
    Повторная проверка размера после записи. Перестраховка.
    """
    max_bytes = max_mb * 1024 * 1024
    if file_size > max_bytes:
        size_mb = file_size / 1024 / 1024
        raise DomainError(
            code="file_too_large",
            message=f"Файл слишком большой ({size_mb:.2f} МБ). Максимум {max_mb} МБ",
            status=413,
        )


async def _save_file_streaming(
    upload_file: UploadFile,
    destination: Path,
    max_mb: int,
) -> int:
    """
    Потоковая запись файла на диск с контролем размера.
    Возвращает итоговый размер в байтах.
    При превышении лимита удаляет файл и кидает DomainError.
    """
    total_size = 0
    max_bytes = max_mb * 1024 * 1024

    # На случай, если кто-то уже читал из файла
    upload_file.file.seek(0)

    async with aiofiles.open(destination, "wb") as buffer:
        while True:
            chunk = await upload_file.read(CHUNK_SIZE)
            if not chunk:
                break

            total_size += len(chunk)
            if total_size > max_bytes:
                # удаляем недописанный файл и падаем
                try:
                    await buffer.flush()
                finally:
                    try:
                        destination.unlink(missing_ok=True)
                    except Exception:
                        # Логирование оставим на внешний слой
                        pass

                size_mb = total_size / 1024 / 1024
                raise DomainError(
                    code="file_too_large",
                    message=f"Файл слишком большой ({size_mb:.2f} МБ). Максимум {max_mb} МБ",
                    status=413,
                )

            await buffer.write(chunk)

    return total_size


def _resolve_subdir(sub_dir: str) -> Path:
    """
    Преобразует логический sub_dir в реальный подкаталог.
    Если sub_dir есть в карте, используем её значение,
    иначе — берем как есть.
    """
    mapped = UPLOAD_PATH_MAP.get(sub_dir, sub_dir)
    path = UPLOAD_ROOT / mapped
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------- ОСНОВНЫЕ ОПЕРАЦИИ ----------------


async def save_uploaded_file(
    upload_file: UploadFile,
    sub_dir: str,
    max_mb: int = IMAGE_MAX_MB,
) -> str:
    """
    Сохраняет один файл и возвращает относительный путь (от BASE_DIR).
    - валидирует MIME-тип
    - пишет файл на диск потоково
    - контролирует размер
    """
    if upload_file is None:
        raise DomainError(
            code="file_missing",
            message="Файл не передан.",
            status=400,
        )

    mime_type = _validate_mime_type(upload_file)

    # Если PDF — используем свой лимит, иначе тот, что пришёл/по умолчанию
    effective_max_mb = max_mb
    if mime_type in ALLOWED_PDF_TYPES and max_mb == IMAGE_MAX_MB:
        effective_max_mb = PDF_MAX_MB

    upload_path = _resolve_subdir(sub_dir)

    file_ext = Path(upload_file.filename).suffix or ".dat"
    unix_time_ms = int(time.time() * 1000)
    unique_filename = f"{unix_time_ms}{file_ext}"
    file_path = upload_path / unique_filename

    file_size = await _save_file_streaming(upload_file, file_path, effective_max_mb)

    # Дополнительная проверка на всякий случай
    _validate_file_size(file_size, effective_max_mb)

    # Возвращаем относительный путь от BASE_DIR (как и раньше)
    return str(file_path.relative_to(BASE_DIR))


async def save_uploaded_files(
    upload_files: list[UploadFile],
    sub_dir: str,
    max_mb: int = IMAGE_MAX_MB,
    rollback_on_error: bool = False,
) -> list[str]:
    """
    Сохраняет массив файлов последовательно и возвращает список относительных путей.
    rollback_on_error=True — удаляет уже сохранённые при любой ошибке.
    """
    if not upload_files:
        return []

    saved_paths: list[str] = []

    try:
        for f in upload_files:
            path = await save_uploaded_file(f, sub_dir=sub_dir, max_mb=max_mb)
            saved_paths.append(path)
        return saved_paths
    except Exception:
        if rollback_on_error:
            for path in saved_paths:
                try:
                    await delete_uploaded_file(path)
                except Exception:
                    # Логировать можно на внешнем уровне
                    pass
        raise


async def delete_uploaded_file(file_url: str | None) -> None:
    """
    Безопасно удаляет файл по относительному пути от BASE_DIR.
    Ничего не кидает, если файл не существует.
    """
    if not file_url:
        return

    file_path = BASE_DIR / file_url

    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except Exception:
            # Логи — на внешний уровень
            pass


async def replace_uploaded_file(
    old_file_url: str | None,
    new_file: UploadFile | None,
    sub_dir: str,
    max_mb: int = IMAGE_MAX_MB,
) -> str | None:
    """
    Заменяет старый файл новым:
    - если new_file is None → просто возвращает старый путь как есть
    - если новый успешно сохранён → старый удаляется
    - если при сохранении нового файла ошибка → старый остаётся на месте
    """
    if new_file is None:
        return old_file_url

    new_path = await save_uploaded_file(new_file, sub_dir=sub_dir, max_mb=max_mb)

    if old_file_url:
        await delete_uploaded_file(old_file_url)

    return new_path
