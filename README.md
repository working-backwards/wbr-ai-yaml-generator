# Generate the WBR yaml using AI

## Overview

This project is mainly built to help you generate yaml files for any large datasets. The yaml generator scripts takes your csv data and builds a config that will work with the WBR App. 
To accomplish this we have used OpenAI's GPT-4o model to generate the config for you. 

## Prerequisites

You need to create a OpenAI account for yourself and generate a API keys. You can do so by following the documentation https://platform.openai.com/docs/quickstart.

## Installing steps

- Clone the project.
- Run the command `python -m build`
- After a successful build you will see a `/dist` directory being created
- Copy either of built files from the `/dist` directory to the main WBR project https://github.com/working-backwards/wbr-app
- Run the command `pip install <path-to-yaml-generator-lib>/wbryamlgenerator-0.1.tar.gz`
- Configure the OpenAI environment variables. You can follow the same quickstart documentation by OpenAI to configure you environment variables
- Now you are ready to generate the yaml configuration for your csv data using AI.