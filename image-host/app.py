import os
import validators
import requests
from pathlib import Path
from flask import (
    Flask,
    request,
    send_from_directory,
    render_template,
    redirect,
    url_for,
)
from util import random_str, get_ext

app = Flask(__name__, static_folder="./static", template_folder="./templates")
IMAGES_PATH = "./static/images"


@app.get("/")
def index():
    return redirect(url_for("list_images"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html", error=None)
    elif request.method == "POST":
        url = request.form.get("url")
        file = request.files.get("file")

        if not validators.url(url) and not file:
            return render_template(
                "upload.html", error="You need to provide a proper file or a URL."
            )

        if file:
            filename = f"{random_str()}.{get_ext(file.filename)}"
            filepath = Path(IMAGES_PATH)
            filepath /= filename

            file.save(str(filepath))

        if url:
            response = requests.get(url)
            if not response.ok:
                return render_template("upload.html", error="Couldn't download image.")

            filename = f"{random_str()}.{get_ext(url)}"
            filepath = Path(IMAGES_PATH)
            filepath /= filename

            with open(str(filepath), "wb+") as file:
                file.write(response.content)

        return redirect(url_for("list_images"))

    else:
        return "Invaid Method", 405


@app.get("/list")
def list_images():
    images = os.listdir(IMAGES_PATH)
    return render_template("list.html", images=images)


@app.get("/delete/<filename>")
def delete_image(filename: str):
    filepath = Path(IMAGES_PATH)
    filepath /= filename

    if not filepath.exists():
        return "Not Found", 404

    os.remove(str(filepath))

    return redirect(url_for("list_images"))


@app.get("/images/<filename>")
def images(filename: str):
    return send_from_directory(IMAGES_PATH, filename)


if __name__ == "__main__":
    print(random_str())
    app.run("localhost", 6969, debug=True)
