# Banking File Processor with AI  

## Overview  
This project is a **Streamlit-based application** designed to process banking files using AI (a Naive Bayes classifier).  
It is fully functional but also **highly adaptable** and easy to extend to meet individual requirements.

## How to Run  

1. **Install Dependencies**:  
   The primary dependencies are listed in `requirements.in`. To generate the actual `requirements.txt` file:  
   ```bash
   pip-compile requirements.in
   ```  
   This command resolves and includes all secondary dependencies, ensuring compatibility.  

2. **Set Up Environment**:  
   - Create a new virtual environment:  
     ```bash
     python -m venv venv
     ```  
   - Activate the virtual environment:  
     - On Windows:  
       ```bash
       venv\Scripts\activate
       ```  
     - On macOS/Linux:  
       ```bash
       source venv/bin/activate
       ```  

   - Install the dependencies:  
     ```bash
     pip install -r requirements.txt
     ```  

3. **Run the Application**:  
   Start the Streamlit application with:  
   ```bash
   streamlit run app.py
   ```  

## Data Management  

The application uses a **local SQLite3 database** to manage data.  
- **Database Initialization**: On the first run, the database is automatically created in the root directory alongside `app.py`, if it doesn't already exist.  
- **External Integration**: The SQLite3 database can be connected to external reporting tools like Power BI for additional analysis and visualization.

## Backend  

All core data processing logic resides in the backend.  

- **API Design**: While this version uses an SQLite3 API for local data storage, the structure mimics the **Google Cloud API**.  
- **Cloud Compatibility**: This local version is a simplified adaptation of a larger application designed for Google Cloud Run and BigQuery. The local setup allows users to run the app in their environment with minimal modifications.

## Customization  

**Adding Pages**:  
Streamlit’s modular nature makes it easy to add new pages. Simply follow the structure in `app.py` and create additional APIs as needed.  

## Machine Learning Model  

This project represents the **fourth iteration** of my banking file processor.  

- **Model Selection**: After experimenting with various algorithms, **Naive Bayes** proved the most effective for this application.  
  - It performs well with limited and highly variable data, which is typical for banking transaction files.  
  - Alternatives such as Random Forests, Boosted Trees, and Neural Networks showed minimal benefits while adding unnecessary complexity.  

---

Feel free to fork, modify, and extend this project for your own use!  
