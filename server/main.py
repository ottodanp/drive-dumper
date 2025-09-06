from os import makedirs
from os.path import isfile, join, splitext
from urllib.parse import unquote

from quart import Quart, request

app = Quart(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 ** 6
ALLOWED_DIRECTORIES = ["uploads"]


def format_target_file_path(target_directory: str, filename: str) -> str:
    name, ext = splitext(filename)
    target_path = join(target_directory, filename)

    copy_number = 0
    while isfile(target_path):
        copy_number += 1
        candidate = f"{name}_{copy_number}{ext}"
        target_path = join(target_directory, candidate)

    return target_path


@app.route("/upload", methods=["POST"])
async def upload_file():
    target_directory = request.args.get("target_directory")
    if target_directory is None:
        target_directory = ALLOWED_DIRECTORIES[0]

    target_directory = unquote(target_directory)

    if "/" in target_directory:
        base_directory = target_directory.split("/")[0]
    else:
        base_directory = ALLOWED_DIRECTORIES[0]
        target_directory = f"{base_directory}/{target_directory}"

    if base_directory not in ALLOWED_DIRECTORIES:
        return {"status": "invalid directory"}, 403

    makedirs(target_directory, exist_ok=True)

    file = (await request.files).get("file")
    if not file:
        return {"status": "invalid file"}, 400

    print(file.filename)
    target_path = format_target_file_path(target_directory, file.filename)
    with open(target_path, "wb") as f:
        f.write(file.read())

    return {"status": "success", "target_path": target_path}, 200


if __name__ == "__main__":
    app.run()
