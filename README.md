[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/CdC-SI/eak-copilot)


# EAK-Copilot

Welcome to the official repository of the EAK-Copilot challenge, developed as part of the [Innovation Fellowship 2024](https://www.innovationfellowship.ch/). This project is designed to enhance workplace efficiency and foster innovation by providing AI-supported tools that assist employees in their daily tasks.

This repository serves as a proof of concept (PoC), which is slated to conclude in February 2025. However, we are optimistic that the momentum generated by this innovative challenge will attract continued support and development beyond this timeframe.

## Challenge Vision

COMING SOON: a detailed overview of our project's vision and strategic alignment.

## Features

- **Automation of Routine Tasks:** Reduces monotonous research tasks and the finding of information, allowing employees to focus on more important tasks.
- **Decision Support:** Provides real-time assistance in decision-making through advanced algorithms.

## Getting Started

Here you will find instructions for installing and setting up EAK-Copilot:

### Prerequisites

Before starting, ensure you have the following software installed on your computer:
- **Git**: Needed for source code management. Install from [here](https://git-scm.com/downloads).
- **Docker**: Required for running containers. Install from [here](https://docs.docker.com/get-docker/).
- **Docker Compose**: Necessary for managing multi-container Docker applications. Install from [here](https://docs.docker.com/compose/install/).

Linux users may need to prepend `sudo` to Docker commands depending on their Docker configuration.

### Installation Instructions

### Installation

1. **Clone the Repository**

   Begin by cloning the EAK-Copilot repository to your local machine to get the necessary project files.

   ```bash
   git clone https://github.com/CdC-SI/eak-copilot.git
   ```

   ```bash
   cd eak-copilot
   ```

2. **Build Docker Images**

    Build the Docker images using the Docker Compose configuration. This step compiles and prepares your Docker environment.

   ```bash docker
    docker-compose build
    docker-compose up -d
    ```
2. **Verifying the Installation**

    Check the status of the containers to confirm everything is running as expected:
    ```bash
    docker-compose ps
    ```
    After the containers are successfully started, verify that the application is running correctly by accessing it through your web browser. Navigate to http://localhost:3000, replacing PORT with the port number specified in your docker-compose.yml.