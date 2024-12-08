import argparse
import logging
from pathlib import Path
from aiofiles import os as async_os
from aiofiles import open as async_open
from asyncio import run


async def read_folder(path: Path, output: Path) -> None:
    """Рекурсивно читає всі файли у вихідній папці та її підпапках."""
    entries = await async_os.scandir(path)  # Отримуємо ітератор
    for entry in entries:  # Використовуємо звичайний for
        if await async_os.path.isdir(entry.path):  # Перевірка на директорію
            await read_folder(Path(entry.path), output)
        elif await async_os.path.isfile(entry.path):  # Перевірка на файл
            await copy_file(Path(entry.path), output)


async def copy_file(file: Path, output: Path) -> None:
    """
    Копіює файл у відповідну підпапку у цільовій папці на основі розширення.
    """
    extension_name = file.suffix[1:] if file.suffix else "no_extension"  # Додаємо перевірку
    extension_folder = output / extension_name

    # Створюємо папку для розширення, якщо її ще немає
    await async_os.makedirs(extension_folder, exist_ok=True)

    # Копіюємо файл
    destination = extension_folder / file.name
    async with async_open(file, "rb") as src, async_open(destination, "wb") as dest:
        await dest.write(await src.read())

    logging.info(f"Скопійовано файл {file} до {destination}")


if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    # Парсинг аргументів командного рядка
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширеннями.")
    parser.add_argument("--source", required=True, help="Шлях до вихідної папки.")
    parser.add_argument("--output", required=True, help="Шлях до цільової папки.")
    args = parser.parse_args()

    # Створюємо шляхи
    source = Path(args.source)
    output = Path(args.output)

    # Перевірка шляхів
    if not source.exists():
        logging.error(f"Вихідна папка {source} не існує.")
        exit(1)

    output.mkdir(parents=True, exist_ok=True)

    # Запускаємо основну функцію
    run(read_folder(source, output))
