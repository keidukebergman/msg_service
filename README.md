
  

  

  

# Simple Messaging Service

  

  

This service is built in python, using fastapi, pydantic, uvicorn and a set of standard libraries. The main three files are main.py, handling http requests, in_memory_storage.py, acting as an in-memory database, and models.py, which provides the data structure for messages.

  




  

# Fundamentals

  

  

  

The database has a dictionary that stores received messages per-user. When calling the API, I use the custom HTTP header parameter user-id as identification. Users, as identified by this parameter, can only access their own inboxes, and can only POST messages where they are the sender.

  

  

  

  

# Compiling and running the application

  

  

  

The application uses uv, uvicorn, pydantic and fastapi, which all have to be available in order for the system to run. It was developed with python version 3.12 but should be compatible with subsequent versions.

  

  

  

With the dependencies available, the system is simply run by navigating to the osttra_msg_service directory and running

  

  

`uv run uvicorn main:app`

  

  

  

I have personally run the following command during development, but forcing the host address and port are redundant, and as I see it, the reload flag is only useful in active development.

  

  

`uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000`

  

  # Data Structures
  ## MessageCreate (BaseModel):

`sender_id`: (required) string, has to be in an email-format

`recipient_id`: (required) string, has to be in an email-format

`subject`: (default "") string

`contents`: (default "") string

  

## Message (MessageCreate):

`msg_id`: (required) UUID for the message

`received_at`: (required) datetime describing when the message arrived

`has_been_read`: (required) bool describing whether or not the message has been read

(also contains a ModelConfig that sets any instance of the model to be immutable)

  

## MessageDeleteRequest(BaseModel):

`ids`: (required) list[UUID] representing the ids of messages to be removed
  

# API Documentation

  

  

  

## Endpoints

  

  

All endpoints require a `user-id` header containing a valid email address. This is used as a very primitive authentication system. Requests with a missing or malformed `user-id` will receive a `400 Bad Request`.

  

  

  

## POST `/api/send`

  

  

Send a new message.

  

  

  

**Headers**

  

  

-  `user-id` (required): must match the request body's `sender_id` in order to prevent identity theft

  

  

  

**Body** (`MessageCreate`)

  

  

-  `sender_id` (required)

  

  

-  `recipient_id` (required)

  

  

- other message fields as defined by the `MessageCreate` model

  

  

  

**Responses**

  

  

-  `201 Created`: returns the created `Message`

  

  

-  `400 Bad Request`: `sender_id`/`recipient_id` missing, or `user-id` header doesn't match `sender_id`

  

  

  

## GET `/api/messages/{id}`

  

  

Retrieve a single message by ID, scoped to the requesting user.

  

  

  

**Path Parameters**

  

  

-  `id` (UUID, required)

  

  

  

**Headers**

  

  

-  `user-id` (required)

  

  

  

**Responses**

  

  

-  `200 OK`: returns the `Message`

  

  

-  `404 Not Found`: no matching message for this user

  

  

  

## PATCH `/api/messages/{id}/mark_read`

  

  

Mark a message as read.

  

  

  

**Path Parameters**

  

  

-  `id` (UUID, required)

  

  

  

**Headers**

  

  

-  `user-id` (required)

  

  

  

**Responses**

  

  

-  `200 OK`: returns the updated `Message`

  

  

-  `404 Not Found`: no matching message for this user

  

  

  

## DELETE `/api/messages/{id}`

  

  

Delete a single message.

  

  

**Path Parameters**

  

  

-  `id` (UUID, required)

  

  

**Headers**

  

  

-  `user-id` (required)

  

  

**Responses**

  

  

-  `204 No Content`: deleted successfully

  

  

-  `404 Not Found`: no matching message for this use

  

  

  

## DELETE `/api/messages`

Delete multiple messages by ID.

**Headers**

-  `user_id` (required)

-  `Content-Type: application/json`

**Body** (`MessageDeleteRequest`)

-  `ids` (list of UUIDs, required)

Example JSON:

```json

{

"ids": ["87ceefe8-6179-40e8-a523-c6edf24b8300", "f47ac10b-58cc-4372-a567-0e02b2c3d479"]

}

```

**Responses**

-  `204 No Content` — request processed

-  `400 Bad Request` — no IDs provided

**Note:** Invalid or non-existent IDs are silently skipped rather than raising an error.

  

  

## GET `/api/messages`

  

  

List messages for the requesting user, with optional filtering for unread messages and a crude pagination system.

  

  

**Query Parameters**

  

-  `only_unread` (bool, default `false`): return only unread messages

  

-  `start_index` (int, optional): start of range (inclusive, ≥ 0)

  

-  `end_index` (int, optional): end of range (inclusive, ≥ start_index)

  

  

  

**Headers**

  

-  `user-id` (required)

  

  

**Responses**

  

-  `200 OK`: returns a list of `Message` objects

  

-  `400 Bad Request`: negative indices, or `start_index` greater than `end_index`

  

  

  

## GET `/api/message_count`

  

  

Return the total number of messages associated with the requesting user. Intended primarily for debugging.

  

  

  

**Headers**

  

  

-  `user-id` (required)

  

  

**Responses**

  

  

-  `200 OK`: returns an integer count

  

  

  

## Error Handling

  

  

Any unhandled exception returns a generic...

  

  

```json

  

  

{ "detail": "An unexpected error occurred" }

  

  

```

  

  

...with status code `500 Internal Server Error`.

  

  

# Example calls

  

  

  

Supposing the server is active on localhost with port 8000, some example calls could look like this:

  

  

  

  

**Sending a message:**

  

`curl -s -X POST http://localhost:8000/api/send -H "Content-Type: application/json" -H "user-id: alice@example.se" -d '{"sender_id": "alice@example.se", "recipient_id": "bertil@example.se", "subject":"This is the subject", "contents": "This is the main message"}'`

  

  

**Getting a single message by ID**

`curl -s http://localhost:8000/api/messages/87ceefe8-6179-40e8-a523-c6edf24b8300 -H "user-id: bertil@example.se"`

  

**Marking a message as read**

  

`curl -s -X PATCH http://localhost:8000/api/messages/96950cd7-ae57-4df1-b93e-d2a16af0b81d/mark_read -H "user-id: bertil@example.se"`

  

**Retreival of entire inbox**

`curl -s http://localhost:8000/api/messages -H "user-id: bertil@example.se"`

  
  

**Retreival of unread messages**

`curl -s http://localhost:8000/api/messages?only_unread=true -H "user-id: bertil@example.se"`

  

  

**Retreival of messages between indices 0 and 2 (inclusive)**

  

`curl -s "http://localhost:8000/api/messages?start_index=0&end_index=2" -H "user-id: bertil@example.se"`

  
  
  

**Deletion of single message**

  

`curl -s -X DELETE http://localhost:8000/api/messages/96950cd7-ae57-4df1-b93e-d2a16af0b81d -H "user-id: bertil@example.se"`

  

  

**Deletion of multiple messages**

`curl -s -X DELETE "http://localhost:8000/api/messages" -H "user-id: bertil@example.se" -H "Content-Type: application/json" -d '{"ids": ["eabf8666-339b-4c81-8c77-800d7859a530", "f6e3ebfa-dd83-4d11-9c8e-e49ad410a7ae"]}'`

  

  

# How to improve the system

In order to address some of the concerns and improve scalability and redundancy, there are some weaknesses that should be solved ASAP. First and foremost, I would use a better system for data storage. The current system is neither thread-safe, scalable or redundant. The Dict system I use could probably be configured to allow for concurrent reads and writes with some semaphores, but SQL would allow for built-in concurrency control and has standardized methods to allow for redundancy and horizontal scalability. It is also worth mentioning that the JSON-based structure I use right now is vastly inferior in its flexibility compared to a relational database.

There is also the matter of authentication, which is currently quite easily spoofable, given that every username is passed unencrypted via headers. This is ok for this task, but for an actual application it goes without saying that this should be resolved. 

Finally, there is the issue of silent errors. I have commented this in the code, but the bulk deletion system used in this application does not provide an error code of one or more of the ids are incorrect. For my purposes it does not matter too much, but for the system to be transparent, it is better to pre-process the ids, check for missing entries and throw an error before deleting messages, terminating the process before any changes can be made. 
