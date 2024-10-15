=======================
System Components
=======================

This section details the individual components involved in the Only Menu system.

**User Interface (PWA)**

- **Framework**: React.js/Vue.js
- **Description**: The entry point for users to interact with the system. Provides a minimalist and intuitive interface for uploading menu images and tracking rewards.
- **Customer Facing**: This component is directly used by the customers to upload images and view rewards.

**Image Upload Component**

- **Framework**: React Dropzone or custom file upload handler
- **Description**: Allows users to upload menu images to be processed by the backend.

**Backend API**

- **Framework**: FastAPI/Flask for Python backends, or Express.js for Node.js backends
- **Description**: Handles API requests from the PWA, processes images, and interacts with the AI model and database.
- **Role**: Acts as the intermediary between the user interface and the backend processing components.

**Image Processing (OCR & NLP)**

- **Framework**: TensorFlow, Tesseract for OCR, custom NLP models
- **Description**: Extracts text and relevant information from uploaded menu images for further processing.

**AI Model Training**

- **Framework**: TensorFlow/PyTorch
- **Description**: Continuously trains and refines the AI model using data collected from user uploads.
- **Objective**: Improve the model’s ability to extract and rank information accurately.

**Data Storage**

- **Framework**: PostgreSQL for relational data, Elasticsearch for fast search capabilities
- **Description**: Manages storage of user data, processed menu information, and AI ranking results.

**Notification & Reward System**

- **Framework**: Django Celery or Node.js Bull for job scheduling
- **Description**: Manages user notifications, rewards, and the redemption process.
- **External Service Integration**: This component may integrate with third-party services for sending notifications.

