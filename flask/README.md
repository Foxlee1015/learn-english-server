---
created: 2020-04-12T13:19:52.701Z
modified: 2020-05-11T11:14:44.140Z
---

# Learn English API

### HTTP RESPONSE STATUS CODES

##### 200 - The request has succeeded

- 200
  - GET
- 201
  - Created
  - POST
- 202
  - Accepted(for batch processing, etc: send emails)
- 204
  - No content(no need to send data in body, etc: large data and no need to send to client)
  - PUT(replace) or PACTH(partial update)

**[200 vs 204 vs 400]**

- GET /**[users]?name=daehan** return [] => 200 (it could include other params to filter like name)
- **"[resource identifier]"** is actually the resource path without the query part
- Do not use 400 for empty lists
- 200 > 204 why? 204 could be possible since the server will not return any data, but it's better to use more common status code

##### 400 - Client error responses

- 400
  - Bad request(invalid params)
- 401
  - Unauthorized(no session, expirted session)
- 403
  - Forbidden(only for admin)
- 404
  - Not Found

##### 500 - Sever error responses

- 500
  - Internal Server Error

[HTTP RESPONSE STATUS CODES](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
[200 NOT 400 when returning empty list for GET request](https://apihandyman.io/empty-lists-http-status-code-200-vs-204-vs-404/)
