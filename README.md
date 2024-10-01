# Project Title

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

This project provides a minimalist version of Aslin, an AI-powered proposal assessment system, that can be used for rapid prototyping and experimentation. It implements the same concepts of dynamic Personas and Rubrics, but doesn't inlude the production UI or additional cloud-native architecture implementation.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need the following things installed on your system:

- git
- python 3.9 or later

You will also need an AWS account with access to Amazon Bedrock and the **Anthropic Claude 3 Haiku** model.

### Installing

1. Clone the repo to your local machine.

```bash
git clone git@ssh.gitlab.aws.dev:gsi-solutions-team/aslin-streamlit.git
```

2. Change into the root directory and create a virtual environment

```bash
cd aslin-streamlit && python3 -m venv .venv
```

3. Install required dependencies

```bash
.venv/bin/pip install -r requirements.txt
```

You're all set and ready to run the app!

## Usage <a name = "usage"></a>

The start the application, ensure you have valid credentials for your AWS account and run this command in the root directory of the project to start the Streamlit server:

```bash
./venv/bin/streamlit run Home.py
```

The application should automatically open in your default web browser at `http://localhost:8501`
