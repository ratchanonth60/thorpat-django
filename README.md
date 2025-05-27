# thorpat-django 🚀

Welcome to **thorpat-django**! This is a Django-based API backend project built with Django Ninja, designed for user management and ready for further expansion.

## 📜 Table of Contents

* [thorpat-django 🚀](#thorpat-django-)
  * [📜 Table of Contents](#-table-of-contents)
  * [🌟 Project Overview](#-project-overview)
  * [✨ Key Features](#-key-features)
  * [💻 Tech Stack](#-tech-stack)
  * [🛠️ Prerequisites](#️-prerequisites)
  * [⚙️ Project Setup](#️-project-setup)
    * [1. Clone the Repository](#1-clone-the-repository)
    * [2. Create and Activate a Virtual Environment (Recommended)](#2-create-and-activate-a-virtual-environment-recommended)
    * [3. Install Dependencies](#3-install-dependencies)
    * [4. Configure Environment Variables](#4-configure-environment-variables)
    * [5. Apply Database Migrations](#5-apply-database-migrations)
    * [6. Create a Superuser (Optional)](#6-create-a-superuser-optional)
  * [▶️ Running the Project](#️-running-the-project)
    * [Using the Django Development Server](#using-the-django-development-server)
    * [Using Docker Compose](#using-docker-compose)
  * [📁 Project Structure](#-project-structure)
  * [🔗 API Endpoints](#-api-endpoints)
  * [👤 Custom User Model](#-custom-user-model)
  * [⚠️ Error Handling](#️-error-handling)

## 🌟 Project Overview

`thorpat-django` is a Django application that provides a RESTful API for managing user data. This project leverages `django-ninja` to create fast and developer-friendly APIs. It also includes Docker setup for easy deployment and consistent development environments.

## ✨ Key Features

* **User Management API**: Endpoints for retrieving user data (GET) with pagination and filtering capabilities.
* **Custom User Model**: Features a tailored User model (`thorpat.apps.users.models.User`).
* **Django Ninja Integration**: Utilizes `django-ninja` for modern and efficient API development.
* **Docker Support**: Comes with a `docker-compose.yml` for streamlined development and deployment.
* **PostgreSQL Database**: Configured to use PostgreSQL as the primary database.
* **Environment Variable Configuration**: Project settings are managed via an `.env` file.

## 💻 Tech Stack

This project is built with the following technologies:

<p align="left">
  <a href="https://www.python.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/>
  </a>
  <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-plain.svg" alt="django" width="40" height="40"/>
  </a>
  <a href="https://django-ninja.rest-framework.com/" target="_blank" rel="noreferrer">
    <img src="https://avatars.githubusercontent.com/u/69200898?s=200&v=4" alt="django-ninja" width="40" height="40"/>
  </a>
  <a href="https://www.postgresql.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40"/>
  </a>
  <a href="https://www.docker.com/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="40" height="40"/>
  </a>
</p>

* **Python**: The core programming language.
* **Django**: High-level Python web framework.
* **Django Ninja**: Fast, type-hinted API library for Django.
* **PostgreSQL**: Powerful, open-source object-relational database system.
* **Docker**: Platform for developing, shipping, and running applications in containers.

## 🛠️ Prerequisites

Before you begin, ensure you have the following software installed:

* Python (version 3.8+ recommended)
* Pip (Python package installer)
* Docker (if you plan to run via Docker)
* Docker Compose (if you plan to run via Docker)
* Git

## ⚙️ Project Setup

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd thorpat-django
