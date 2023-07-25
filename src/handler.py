"""
Lambda entrypoint module defining handlers that will be invoked when calling
the lambda functions.
"""
import json
from module.example import foo
from module import bar


def handle(event, context):
    """Lambda handler"""
    print(f"Received event: \n{json.dumps(event)}")
    print(f"With context: \n{context}")
    foo("Hello")
    bar("World")
    return {"statusCode": 200, "body": "Success"}
