# Estonian Text Simplification with OpenNMT

This project provides a Dockerized application for Estonian text simplification using an OpenNMT-based model. It includes a web interface and a RabbitMQ-based worker architecture for efficient processing.

---

## Features
- **Text Simplification**: Simplifies Estonian text using a pre-trained OpenNMT model.
- **Web Interface**: User-friendly interface for entering and simplifying text.
- **RabbitMQ Integration**: Decouples the worker process from the web server for scalable processing.
- **Dockerized**: Fully containerized for easy deployment.
- **Baseline**: The simplification here should be considered a baseline. See the paper below for details.

---

## Prerequisites
1. **Docker**: Ensure Docker and Docker Compose are installed.
   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)
2. **Model File**: Download the OpenNMT model from [Hugging Face](https://huggingface.co/datasets/vulturuldemare/Estonian-Text-Simplification).
   - The trained model is `openNMT-SimplificationModel.pt`.
   - Place the model under `OpenNMT/models/`.
   - Edit the configuration file `OpenNMT/models/nmt_config.yaml` to point to the model.

---

## Installation

1. Clone the repository:
   
   git clone https://github.com/SoimulPatriei/webapp-opennmt
   cd webapp-opennmt
   
 2. Build and run the application:  
   docker-compose up --build
   
 3. Access the server in your browser on port 5000:  
   You can access the server in your browser on the port 5000 (e.g. http://localhost:5000/)
   
   ![Estonian Text Simplification Interface](interface.png)

   

## Credits
    Interface Programming: Eduard Barbu
    Training of the OpenNMT Model: Sten Marcus Malva
    This software was created as part of the EKTB55 project "Teksti lihtsustamine eesti keeles".


## Paper
If you use this interface or want to learn more, please consult the paper:
Improving Estonian Text Simplification through Pretrained Language Models and Custom Datasets
by Eduard Barbu, Meeri-Ly Muru, Sten Marcus Malva
https://arxiv.org/abs/2501.15624

