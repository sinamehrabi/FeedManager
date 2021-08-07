from typing import List

from pydantic import BaseModel


class HttpErrorSchema(BaseModel):
    detail: str
    error_code: int


class ValidationErrorSchema(BaseModel):
    loc: List[str]
    msg: str
    type: str


class HttpValidationErrorSchema(BaseModel):
    detail: List[ValidationErrorSchema]
    error_code: int


responses = {
    400: {"description": "Bad Request",
          "model": HttpErrorSchema,
          "content": {
              "application/json": {
                  "example": {"detail": "error occurred", "error_code": 1001}
              }
          }},
    401: {"description": "Not Authenticate",
          "model": HttpErrorSchema,
          "content": {
              "application/json": {
                  "example": {"detail": "error occurred", "error_code": 1002}
              }
          }},
    403: {"description": "Forbidden",
          "model": HttpErrorSchema,
          "content": {
              "application/json": {
                  "example": {"detail": "error occurred", "error_code": 1003}
              }
          }},
    422: {"description": "Validation Error",
          "model": HttpValidationErrorSchema,
          "content": {
              "application/json": {
                  "example": {"detail": [
                      {
                          "loc": [
                              "string"
                          ],
                          "msg": "string",
                          "type": "string"
                      }
                  ], "error_code": 1000}
              }
          }
          }}
