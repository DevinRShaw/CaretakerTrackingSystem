# FastAPI Wellness Form Application

This FastAPI application provides a web interface for patient wellness reporting, processes submitted data, and interacts with a MongoDB database to validate patient records and provide guidance based on prior reports.

---

## Table of Contents

1. [Application Overview](#application-overview)
2. [Endpoints](#endpoints)

   * [`GET /`](#get-)
   * [`POST /submit_form`](#post-submit_form)
3. [Database Integration](#database-integration)
4. [Form Processing](#form-processing)
5. [Planned Features](#planned-features)
6. [Usage](#usage)

---

## Application Overview

* **Framework:** FastAPI

* **Template Engine:** Jinja2

* **Database:** MongoDB (accessed via async client)

* **Purpose:**

  1. Serve a wellness form to patients.
  2. Validate patient IDs against existing database records.
  3. Process submitted wellness data asynchronously.
  4. Generate caregiver guidance based on prior wellness reports and patient-specific medical history.

* **Directory Structure Example:**

```
/app
 ├─ main.py           # FastAPI application
 ├─ templates/
 │   └─ form.html     # Jinja2 template for patient form
```

---

## Endpoints

### `GET /`

* **Description:** Serves the patient wellness form.
* **Response:** HTML page rendered from `form.html`.
* **Usage Example:**

```python
import requests

response = requests.get("http://localhost:8000/")
print(response.text)  # HTML content of the wellness form
```

---

### `POST /submit_form`

* **Description:** Receives form submission from patients and processes the data.

* **Request Body:** URL-encoded form data containing fields such as `patientID` and `freeResponse`.

* **Validation:**

  * Raises HTTP 404 if `patientID` is missing.
  * Raises HTTP 409 if `patientID` does not exist in the database.

* **Processing:**

  * Decodes `freeResponse` input.
  * Passes all submitted data to `process_form` for asynchronous handling.

* **Example Request (cURL):**

```bash
curl -X POST http://localhost:8000/submit_form \
     -d "patientID=12345&freeResponse=Feeling+good"
```

---

## Database Integration
### Database Schema Design

<img width="802" height="562" alt="Untitled Diagram drawio (5)" src="https://github.com/user-attachments/assets/b2c185cf-a896-479b-bccc-9d58faaf5a1a" />

* **MongoDB URI:** `mongodb://db:27017/` (Docker container name `db`)
* **Database:** `caregiver_app`
* **Collection:** `patient_cases`
* **Usage:**
  * Track patient case details
  * Keep a record of past record submittals
  * Track warning flags triggered by form processing

---

## Form Processing (`process_form`)

* **Purpose:**

  1. Validate patient existence.
  2. Retrieve patient wellness history.
  3. Apply rules based on post-operation healing periods.
  4. Identify warnings or flags for the caregiver.
  5. Prepare structured prompts for an AI model (`tinyllama1.1b`) to generate guidance.
     
### Processing Design
<img width="768" height="724" alt="Form Analysis and Flagging drawio" src="https://github.com/user-attachments/assets/924cb133-615c-4b3e-b9aa-ed53ad39425e" />


