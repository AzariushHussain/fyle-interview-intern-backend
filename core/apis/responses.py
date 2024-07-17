from flask import Response, jsonify, make_response


class APIResponse(Response):
    @classmethod
    def respond(cls, data):
        return make_response(jsonify(data=data))
    
    @classmethod
    def error(cls, data,status_code):
        return make_response(jsonify(data=data),status_code)
