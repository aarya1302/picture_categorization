# Running Image Query Web App

This guide will walk you through setting up and running the Image Query Web App using Docker and Node.js.

## Prerequisites

Before you begin, ensure your system meets the following requirements:

1. **Docker**: If not already installed, download and install Docker from [docker.com](https://www.docker.com/).
   
2. **Node.js**: Ensure Node.js is installed on your computer. If not, download and install it from [nodejs.org](https://nodejs.org/en/download/).

## Setup Instructions

Follow these steps to set up and run the web app:

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd <repository-directory>
```
Step 2: Set up Docker Containers
In the root directory of the project, use Docker Compose to set up Weaviate containers:

```bash
docker-compose up -d
```
This command will start the necessary containers for Weaviate.

Step 3: Install Node.js Dependencies
Install the required Node.js dependencies for the web app:

```bash

npm install
```
Step 4: Run the Web App
Start the web app by running:

```bash

node app.js
```
The web app should now be running locally.

Accessing the Web App
Open your web browser and go to http://localhost:<port> where <port> is the port specified in your app.js or docker-compose.yml file.

Additional Notes
Make sure Docker is running and configured correctly before starting.
Ensure all dependencies are installed using npm install before running node app.js.
Adjust any configuration settings as needed in app.js or docker-compose.yml before starting the containers or app.
