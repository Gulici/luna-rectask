# API Documentation: Hydroponic System API

## Introduction

The **Hydroponic System API** provides endpoints for managing hydroponic systems and tracking environmental measurements such as **pH level, temperature, and TDS**.

This API uses **JWT authentication** and follows **RESTful principles**.

### Authentication

All requests **require authentication** via JWT tokens.
Include the `Authorization: Bearer <your_access_token>` header in all requests.

#### Example Header:

```http
Authorization: Bearer eyJhbGciOiJIUzI...
```

---

## 1. Authentication & Users

### 1.1 Register a New User

```http
POST /api/register/
```

#### Request Body:

```json
{
    "username": "newuser",
    "password": "securepassword"
}
```

#### Response:

```json
{
    "user": {
        "id": 1,
        "username": "newuser"
    },
    "refresh": "eyJhbGciOiJIUz...",
    "access": "eyJhbGciOiJIUz..."
}
```

##### Possible Status Codes:
- `201 Created` - User successfully registered
- `400 Bad Request` - Invalid input data

### 1.2 Obtain JWT Token

```http
POST /api/token/
```

#### Request Body:

```json
{
    "username": "newuser",
    "password": "securepassword"
}
```

#### Response:

```json
{
    "refresh": "eyJhbGciOiJIUz...",
    "access": "eyJhbGciOiJIUz..."
}
```

##### Possible Status Codes:
- `200 OK` - Token successfully generated
- `401 Unauthorized` - Invalid credentials

### 1.3 Refresh JWT Token

```http
POST /api/token/refresh/
```

#### Request Body:

```json
{
    "refresh": "eyJhbGciOiJIUz..."
}
```

#### Response:

```json
{
    "access": "eyJhbGciOiJIUz..."
}
```

##### Possible Status Codes:
- `200 OK` - New access token issued
- `401 Unauthorized` - Invalid or expired refresh token

### 1.4 Get All Users

```http
GET /api/users/
```

#### Response:

```json
[
    {
        "id": 1,
        "username": "testuser"
    },
    {
        "id": 2,
        "username": "anotheruser"
    }
]
```

##### Possible Status Codes:
- `200 OK` - Users retrieved successfully

### 1.5 Get User Details

```http
GET /api/users/{user_id}/
```

##### Possible Status Codes:
- `200 OK` - User data retrieved successfully
- `404 Not Found` - User not found

---

## 2. Hydroponic Systems

### 2.1 Get All Systems

```http
GET /api/systems/
```

#### Query Parameters (Optional):

| Parameter     | Type   | Description                          |
| ------------- | ------ | ------------------------------------ |
| `ordering`    | string | Sort by name or creation date        |
| `date_before` | string | Filter systems created before a date |
| `date_after`  | string | Filter systems created after a date  |

#### Response:

```json
[
    {
        "id": 1,
        "name": "Test System",
        "owner": 1,
        "created_date": "2024-03-05T12:00:00Z"
    },
    {
        "id": 2,
        "name": "Greenhouse System",
        "owner": 1,
        "created_date": "2024-03-10T15:30:00Z"
    }
]
```

##### Possible Status Codes:
- `200 OK` - Systems retrieved successfully

### 2.2 Get System Details (With Last 10 Measurements)

```http
GET /api/systems/{system_id}/
```

#### Response:

```json
{
    "system": {
        "id": 1,
        "name": "My Hydroponic System",
        "owner": 5,
        "created_date": "2024-03-05T12:00:00Z"
    },
    "last_measurements": [
        {
            "id": 15,
            "ph": 6.7,
            "temperature": 23.2,
            "tds": 780,
            "timestamp": "2024-03-12T16:30:00Z"
        }
    ]
}
```

##### Possible Status Codes:
- `200 OK` - System details retrieved successfully
- `404 Not Found` - System not found or unauthorized access

### 2.3 Create a New System

```http
POST /api/systems/
```

#### Request Body:

```json
{
    "name": "My Hydroponic System"
}
```

📌 **Note:** The system is automatically assigned to the authenticated user.

##### Possible Status Codes:
- `201 Created` - System successfully created
- `400 Bad Request` - Invalid input data

### 2.4 Update a System

```http
PUT /api/systems/{system_id}/
```

#### Request Body:

```json
{
    "name": "Updated System Name"
}
```

##### Possible Status Codes:
- `200 OK` - System updated successfully
- `400 Bad Request` - Invalid input data
- `404 Not Found` - System not found or unauthorized access

### 2.5 Partially Update a System

```http
PATCH /api/systems/{system_id}/
```

#### Request Body:

```json
{
    "name": "Updated Name"
}
```

##### Possible Status Codes:
- `200 OK` - System updated successfully
- `400 Bad Request` - Invalid input data
- `404 Not Found` - System not found or unauthorized access

### 2.6 Delete a System

```http
DELETE /api/systems/{system_id}/
```

##### Possible Status Codes:
- `204 No Content` - System successfully deleted
- `404 Not Found` - System not found or unauthorized access

