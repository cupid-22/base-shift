<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://cupid-22.github.io/base-shift/only-menu/architecture.html#system-architecture-overview">
    <img src="/docs/source/_static/images/logo.png" alt="Logo" width="230" height="180">
  </a>

  <h3 align="center">Only Menus</h3>

[![Build and Deploy Sphinx Docs](https://github.com/cupid-22/base-shift/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/cupid-22/base-shift/actions/workflows/deploy-docs.yml)
  <p align="center">
    A Django-based platform for crowd-sourced restaurant menus
    <br />
    <a href="https://cupid-22.github.io/base-shift/only-menu/index.html"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/cupid-22/only-menus/issues">Report Bug</a>
    ·
    <a href="https://github.com/cupid-22/only-menus/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#key-features">Key Features</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#user-journey">User Journey</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

[![Product Name Screen Shot](/docs/source/_static/images/colorful_data_flow_compnent.png)](./docs/source/_static/images/colorful_data_flow_compnent.png)

Only-Menus is a Django-based platform designed to crowdsource menus from various establishments. It provides an API-first approach to manage menus, allowing contributors to submit and update menu items while consumers can browse and search for menus of their choice. The platform uses AI-powered image processing to extract menu information and implements a reward system to incentivize high-quality contributions.

<p align="right">(<a href="#top">back to top</a>)</p>

## Key Features

- Crowdsourced menu collection and updates
- AI-powered menu information extraction using OCR and NLP
- Quality-based reward system for contributors
- API-first approach for seamless integration
- Progressive Web App (PWA) for cross-platform accessibility
- Robust data storage for future product development

<p align="right">(<a href="#top">back to top</a>)</p>

## Architecture

Only-Menus follows a microservices architecture with the following components:

1. Frontend: Progressive Web App (PWA)
2. Backend: Django with Flask/FastAPI for API endpoints
3. AI Processing: OCR and NLP models for menu extraction
4. Data Storage: MongoDB for menu data, PostgreSQL/ElasticSearch for user and system data
5. Reward System: Points calculation and notification system

For a detailed architecture diagram, please refer to the [documentation](https://cupid-22.github.io/base-shift/only-menu/architecture.html).

<p align="right">(<a href="#top">back to top</a>)</p>

## User Journey

1. User Registration: Users sign up through the PWA interface.
2. Menu Upload: Contributors upload menu images via the app.
3. AI Processing: The system processes the image using OCR and NLP techniques.
4. Quality Assessment: The extracted information is evaluated for completeness and uniqueness.
5. Reward Allocation: Points are awarded based on the quality of the contribution.
6. Menu Browsing: Users can search and browse the crowdsourced menu database.
7. Redemption: Accumulated points can be converted to rewards or monetary value.

<p align="right">(<a href="#top">back to top</a>)</p>

## Built With

- [Django](https://www.djangoproject.com/) - Backend framework
- [Django Rest Framework](https://www.django-rest-framework.org/) - API development
- [React](https://reactjs.org/) - Frontend framework for PWA
- [PyTorch](https://pytorch.org/) - AI model development
- [MongoDB](https://www.mongodb.com/) - Menu data storage
- [PostgreSQL](https://www.postgresql.org/) - User and system data storage
- [Docker](https://www.docker.com/) - Containerization

<p align="right">(<a href="#top">back to top</a>)</p>

## Getting Started

To get a local copy up and running, follow these steps:

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Node.js and npm

### Installation

1. **Clone the repository:**
   `git clone https://github.com/cupid-22/only-menus.git`

2. **Navigate to the project directory:**
   `cd only-menus`

3. **Create a virtual environment and activate it:**
   - Run `python -m venv venv`
   - On Unix or macOS, activate it with `source venv/bin/activate`. On Windows, use `venv\Scripts\activate`

4. **Install Python dependencies:**
   `pip install -r requirements.txt`

5. **Install frontend dependencies:**
   - Navigate to the frontend directory: `cd frontend`
   - Install dependencies with `npm install`

6. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in the required values.

7. **Run the development servers:**
   - Start Docker containers with `docker-compose up -d`
   - Run the Django development server with `python manage.py runserver`
   - Start the frontend server with `cd frontend && npm start`

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

For detailed usage instructions, API documentation, and development guidelines, please refer to our [official documentation](https://cupid-22.github.io/base-shift/only-menu/index.html).

<p align="right">(<a href="#top">back to top</a>)</p>

## Roadmap

- [x] Basic project setup
- [x] User authentication system
- [ ] Menu upload and processing pipeline
- [ ] AI model integration for OCR and NLP
- [ ] Reward system implementation
- [ ] PWA development
- [ ] API documentation
- [ ] Beta testing and feedback collection

See the [open issues](https://github.com/cupid-22/only-menus/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#top">back to top</a>)</p>

## Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and suggest improvements.

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

Gaurav Mishra - [gaurav.mishra.cx@gmail.com](mailto:gaurav.mishra.cx@gmail.com)

Project Link: [https://github.com/cupid-22/only-menus](https://github.com/cupid-22/only-menus)

<p align="right">(<a href="#top">back to top</a>)</p>

## Acknowledgments

- [OpenAI](https://openai.com/) for AI model inspiration
- [Google Vision API](https://cloud.google.com/vision) for OCR techniques
- [Django community](https://www.djangoproject.com/community/) for their excellent documentation and support

<p align="right">(<a href="#top">back to top</a>)</p>
