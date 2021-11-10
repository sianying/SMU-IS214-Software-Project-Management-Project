# Backend Flask App & Setup Guide

## 1. Install Dependencies
Use command `pip install -r requirements.txt` in current directory to install

## 2. Add AWS Credentials
Create a file called aws_credentials with your access and secret keys add it to current directory.<br>
Add the file to .gitignore if not already in it

## 3. Run Application
Use command `python main.py` in current directory to start backend Flask App on localhost

## Directories
* ./modules - Contains all Manager Modules with the Class and DAO script for the App
* ./routes - Contains all Routing Files for each of the Endpoints available on our Flask App
* ./test - Contains all the Test Files for the Modules