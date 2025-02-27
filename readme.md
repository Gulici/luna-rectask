# Hydroponic System API

## Introduction
Hydroponic System API is a Django-based application that uses PostgreSQL as its database and runs in a Docker environment.

## Prerequisites
Before starting the installation, ensure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- `pip`

## Installation and Setup

### 1. Clone the Repository
```sh
git clone https://github.com/Gulici/luna-rectask.git
cd luna-rectask
```

### 2. Create and Activate a Virtual Environment
Since the repository does not include a `venv`, you need to create one manually:
```sh
python -m venv venv # Linux/macOS
py -m venv venv # Windows
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Start Docker Containers
Start the PostgreSQL database:
```sh
docker-compose up -d
```

### 5. Configure the Database
Run migrations:
```sh
cd hydroponics
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser
```sh
python manage.py createsuperuser
```

### 7. Run the Application
```sh
python manage.py runserver
```
The application will be available at: `http://127.0.0.1:8000/`

## Testing
To run unit tests:
```sh
python manage.py test
```

## Code documentation
Code documentation is generated from docstrings using Sphinx.

The documentation is avaiable at `hydroponics/docs/build/html/index.html`.

## Stop and Remove Containers
```sh
docker-compose down
```

<br><br>

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


## 3. Measurements

### 3.1 Get All Measurements for a System

```http
GET /api/systems/{system_id}/measurements/
```

#### Query Parameters (Optional):

| Parameter          | Type   | Description                                        |
|-------------------|--------|----------------------------------------------------|
| `ordering`       | string | Sort by `ph`, `temperature`, `tds`, or `timestamp` |
| `ph_min`        | float  | Minimum pH value filter                           |
| `ph_max`        | float  | Maximum pH value filter                           |
| `temperature_min` | float  | Minimum temperature value filter                  |
| `temperature_max` | float  | Maximum temperature value filter                  |
| `tds_min`       | int    | Minimum TDS value filter                          |
| `tds_max`       | int    | Maximum TDS value filter                          |
| `timestamp_before` | string | Filter measurements before a specific date (ISO 8601 format) |
| `timestamp_after`  | string | Filter measurements after a specific date (ISO 8601 format)  |

#### Response:

```json
{
    "count": 3,
    "results": [
        {
            "id": 1,
            "ph": 6.5,
            "temperature": 22.3,
            "tds": 800,
            "timestamp": "2024-03-12T16:30:00Z"
        },
        {
            "id": 2,
            "ph": 6.8,
            "temperature": 23.5,
            "tds": 780,
            "timestamp": "2024-03-13T10:15:00Z"
        }
    ]
}
```

##### Possible Status Codes:
- `200 OK` - Measurements retrieved successfully
- `404 Not Found` - System not found or unauthorized access

### 3.2 Get Measurement Details

```http
GET /api/systems/{system_id}/measurements/{measurement_id}/
```

#### Response:

```json
{
    "id": 1,
    "ph": 6.5,
    "temperature": 22.3,
    "tds": 800,
    "timestamp": "2024-03-12T16:30:00Z"
}
```

##### Possible Status Codes:
- `200 OK` - Measurement retrieved successfully
- `404 Not Found` - Measurement not found or unauthorized access

### 3.3 Create a New Measurement

```http
POST /api/systems/{system_id}/measurements/
```

#### Request Body:

```json
{
    "ph": 6.9,
    "temperature": 24.0,
    "tds": 850
}
```

#### Response:

```json
{
    "id": 3,
    "ph": 6.9,
    "temperature": 24.0,
    "tds": 850,
    "timestamp": "2024-03-14T12:45:00Z"
}
```

##### Possible Status Codes:
- `201 Created` - Measurement successfully created
- `400 Bad Request` - Invalid input data
- `403 Forbidden` - User does not have access to the system

### 3.4 Update a Measurement

```http
PUT /api/systems/{system_id}/measurements/{measurement_id}/
```

#### Request Body:

```json
{
    "ph": 7.0,
    "temperature": 25.0,
    "tds": 900
}
```

#### Response:

```json
{
    "id": 1,
    "ph": 7.0,
    "temperature": 25.0,
    "tds": 900,
    "timestamp": "2024-03-12T16:30:00Z"
}
```

##### Possible Status Codes:
- `200 OK` - Measurement updated successfully
- `400 Bad Request` - Invalid input data
- `403 Forbidden` - User does not have access to the system
- `404 Not Found` - Measurement not found

### 3.5 Partially Update a Measurement

```http
PATCH /api/systems/{system_id}/measurements/{measurement_id}/
```

#### Request Body:

```json
{
    "ph": 6.7
}
```

#### Response:

```json
{
    "id": 1,
    "ph": 6.7,
    "temperature": 22.3,
    "tds": 800,
    "timestamp": "2024-03-12T16:30:00Z"
}
```

##### Possible Status Codes:
- `200 OK` - Measurement updated successfully
- `400 Bad Request` - Invalid input data
- `403 Forbidden` - User does not have access to the system
- `404 Not Found` - Measurement not found

### 3.6 Delete a Measurement

```http
DELETE /api/systems/{system_id}/measurements/{measurement_id}/
```

##### Possible Status Codes:
- `204 No Content` - Measurement successfully deleted
- `403 Forbidden` - User does not have access to the system
- `404 Not Found` - Measurement not found


