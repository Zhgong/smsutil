from bottle import route, run


@route("/",method=["GET"])
def index():
    return "It works"


if __name__=="__main__":
    run(host="0.0.0.0",port=8080)