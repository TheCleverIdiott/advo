from flask import jsonify

## Default message response
def message(status_code: int, message: str):
    data = {
        "status_code": status_code,
        "message": message,        
    }

    return jsonify(data), status_code

## Error Message response
def message_error(status_code: int, error: str, message: str):
    data = {
        "status_code": status_code,
        "message": message,
        "error": error,        
    }
    return jsonify(data), status_code

## Custom Message response
def message_custom(data: dict, status_code: int, message: str):
    data['status_code'] = status_code
    data['message'] = message

    return jsonify(data), status_code