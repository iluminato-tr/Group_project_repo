Getting Started

1. Installation

#Clone the GitHub repository

Clone the GitHub repository of the web application to your local machine. This will create a local copy of the project repository on your machine, allowing you to access and modify the application's source code.

#Install required dependencies

Install the required Python dependencies listed in the requirments.txt file using the pip package manager. Navigate to the project directory in your terminal and install all the necessary Python packages and libraries specified in the requirements.txt file, ensuring that the application has all the required dependencies to run smoothly.

#Install the RDBMS 

Download the SQL installer of your choice (SQLite, MySQL) but we've provided the details for PostgreSQL here: 

Visit the official PostgreSQL download page at https://www.postgresql.org/download/
Choose the appropriate installer based on your operating system, run and complete the installation. 
Once the installation is complete, you might need to initialize the database cluster. This is typically done automatically, but if not, you can find an option for it in the PostgreSQL start menu folder.
PostgreSQL is installed as a service. You can start and stop it using the Services application or the pgAdmin tool (graphical client for easier databse management).
You can visit the official pgAdmin download page at https://www.pgadmin.org/download/

#Running SQL queries

You can create a new database or excute the queries in an existing database. 
Open your database client and connect to the database server. Open the SQL file provided in the project (tables.sql) using the database client and execute them. Verify the database to ensure the the queries were executed successfulyy and gave the expected results.  

Ensure that the database connection details (e.g., database URL, username, password) are correctly configured in the application's configuration files to establish a connection between the web application and the database.

#Run the application server

Run the application server to start the population genetics web application. This will launch the Flask development server, which hosts the web application locally on your machine. You will see the output in the terminal indicating that the server is running.

2. Usage

Accessing the Web Application

Access the web application through a web browser by entering the provided URL in the address bar. This URL corresponds to the local address where the Flask development server is running (e.g., http://127.0.0.1:5000).

Alternatively, if the application is deployed to a remote server, access it by entering the appropriate URL in the address bar of your web browser.

Navigating the Application

Use the navigation menu provided on the web application's interface to access different features and functionalities. The navigation menu typically includes options such as "Population Analysis," "SNP Analysis," and "Analysis Results," among others.

Click on the respective menu items to navigate to the desired section of the application and access the corresponding features and tools.

Performing Analysis

Follow the instructions provided on each page to input parameters, select populations, and visualize results for each analysis. The application typically provides input fields, dropdown menus, and buttons to facilitate user interaction and input.

Refer to the documentation, tooltips, or help sections provided within the application for additional guidance on how to use specific features and tools effectively.

Explore the various analysis options and functionalities available in the application to gain insights into population genetics data and interpret analysis results accurately.
