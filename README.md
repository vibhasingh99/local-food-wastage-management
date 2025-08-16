# 🍽️ Local Food Wastage Management System

## 📌 Project Overview
Food wastage is a significant issue, with many households and restaurants discarding surplus food while others face food insecurity.  
This project provides a **Streamlit-based web app** that connects food providers (restaurants, grocery stores, supermarkets) with receivers (NGOs, individuals, community centers).  

The system:
- Stores food provider, receiver, and claims data in **SQLite**.
- Enables **filtering, CRUD operations, and SQL-powered analysis**.
- Provides **insights into food wastage patterns** through queries and visualizations.

---

## 🛠️ Tech Stack
- **Python**  
- **SQLite (Database)**  
- **Streamlit (Frontend)**  
- **Pandas, Altair, Matplotlib (Data Analysis & Visualization)**  

---

## 📊 Datasets (SQLite Tables)
1. **Providers** → Food providers (restaurants, stores, supermarkets)  
2. **Receivers** → Food receivers (NGOs, individuals)  
3. **Food_Listings** → Available food items  
4. **Claims** → Food claims (Pending / Completed / Cancelled)  

---

## 🔑 Features
✅ User-friendly **Streamlit interface**  
✅ **Filters**: City, provider type, food type, meal type  
✅ **CRUD operations**: Add / Update / Delete food listings and claims  
✅ **SQL Queries (15+)** with insights, e.g.:
- How many food providers/receivers per city?  
- Which provider donates the most food?  
- Which meal type is most claimed?  
- Completed vs Pending vs Cancelled claims ratio  

✅ **Visualizations** using Altair & Matplotlib  
✅ **Contact details** of providers for direct coordination  

---

## 🚀 How to Run Locally
1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/local-food-wastage-management.git
   cd local-food-wastage-management
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

4. Open in browser:
   ```
   http://localhost:8501
   ```

---

## 🌍 Live Demo
Deployed on **Streamlit Cloud** 👉 [Click here to view]
(https://local-food-wastage-management-havbb6hsaarggsmaagudtn.streamlit.app/)

---

## 📈 Future Improvements
- Add **geolocation support** to show nearest food providers on map  
- Enable **SMS/Email alerts** to receivers when new food listings are available  
- Build a **recommendation system** for efficient distribution  

--

## 🏆 Credits
Developed by: **Vibha Chauhan**  
Domain: **Food Management, Waste Reduction, Social Good**  
