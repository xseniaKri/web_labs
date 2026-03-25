from flask import Flask, render_template, request, make_response
import re

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/request-info", methods=["GET", "POST"])
def request_info():

    url_params = request.args
    headers = request.headers
    cookies = request.cookies
    form_data = request.form

    response = make_response(
        render_template(
            "request_info.html",
            url_params=url_params,
            headers=headers,
            cookies=cookies,
            form_data=form_data
        )
    )

    response.set_cookie("example_cookie", "HelloCookie")

    return response


@app.route("/phone", methods=["GET", "POST"])
def phone():

    error = None
    phone_formatted = None
    phone_input = ""

    if request.method == "POST":

        phone_input = request.form.get("phone")

        if not re.fullmatch(r"[0-9+\-\s().]+", phone_input):
            error = (
                "Недопустимый ввод. "
                "В номере телефона встречаются "
                "недопустимые символы."
            )

        else:
            digits = re.sub(r"\D", "", phone_input)

            if phone_input.startswith("+7") or phone_input.startswith("8"):

                if len(digits) != 11:
                    error = (
                        "Недопустимый ввод. "
                        "Неверное количество цифр."
                    )

            else:

                if len(digits) != 10:
                    error = (
                        "Недопустимый ввод. "
                        "Неверное количество цифр."
                    )

            if not error:

                if len(digits) == 10:
                    digits = "8" + digits

                phone_formatted = (
                    f"8-{digits[1:4]}-"
                    f"{digits[4:7]}-"
                    f"{digits[7:9]}-"
                    f"{digits[9:11]}"
                )

    return render_template(
        "phone.html",
        error=error,
        phone_formatted=phone_formatted,
        phone_input=phone_input
    )


if __name__ == "__main__":
    app.run(debug=True)