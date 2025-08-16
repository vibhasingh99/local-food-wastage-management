import sqlite3
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

DB_PATH = r"C:\Users\admin\food_waste.db"
st.set_page_config(page_title="Local Food Wastage System", layout="wide")

@st.cache_data
def run_query(sql: str):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)

def write_table(df: pd.DataFrame, key=None):
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, file_name=(key or "export") + ".csv")

def execute_sql(sql: str, params: tuple = ()):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()

def insert_food_listing(values: dict):
    sql = """
        INSERT INTO Food_Listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_sql(sql, (
        values.get("Food_ID"),
        values.get("Food_Name"),
        values.get("Quantity"),
        values.get("Expiry_Date"),
        values.get("Provider_ID"),
        values.get("Provider_Type"),
        values.get("Location"),
        values.get("Food_Type"),
        values.get("Meal_Type"),
    ))

def update_food_listing(food_id: int, updates: dict):
    sets = []
    params = []
    for k, v in updates.items():
        sets.append(f"{k} = ?")
        params.append(v)
    params.append(food_id)
    sql = f"UPDATE Food_Listings SET {', '.join(sets)} WHERE Food_ID = ?"
    execute_sql(sql, tuple(params))

def delete_food_listing(food_id: int):
    execute_sql("DELETE FROM Food_Listings WHERE Food_ID = ?", (food_id,))

def insert_claim(values: dict):
    sql = """
        INSERT INTO Claims (Claim_ID, Food_ID, Receiver_ID, Status, Timestamp)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_sql(sql, (
        values.get("Claim_ID"),
        values.get("Food_ID"),
        values.get("Receiver_ID"),
        values.get("Status"),
        values.get("Timestamp"),
    ))

def update_claim(claim_id: int, updates: dict):
    sets = []
    params = []
    for k, v in updates.items():
        sets.append(f"{k} = ?")
        params.append(v)
    params.append(claim_id)
    sql = f"UPDATE Claims SET {', '.join(sets)} WHERE Claim_ID = ?"
    execute_sql(sql, tuple(params))

def delete_claim(claim_id: int):
    execute_sql("DELETE FROM Claims WHERE Claim_ID = ?", (claim_id,))

st.title("Local Food Wastage Management System")
st.markdown("**Dataset:** Providers, Receivers, Food_Listings, Claims (SQLite). Use filters on left panel.")

st.sidebar.header("Filters & Quick Actions")
city_filter = st.sidebar.text_input("Filter by City / Location (leave blank = all)")
provider_filter = st.sidebar.text_input("Filter by Provider name (partial)")
food_type_filter = st.sidebar.selectbox("Food Type (All/choose)", options=["All", "Vegetarian", "Non-Vegetarian", "Vegan", "Other"], index=0)
meal_type_filter = st.sidebar.selectbox("Meal Type (All/choose)", options=["All", "Breakfast", "Lunch", "Dinner", "Snacks", "Other"], index=0)
st.sidebar.markdown("---")
if st.sidebar.button("Refresh cached queries"):
    st.cache_data.clear()
    st.experimental_rerun()

queries = {
    "Citywise_Providers": "SELECT City, COUNT(*) AS Providers_Count FROM Providers GROUP BY City",
    "Citywise_Receivers": "SELECT City, COUNT(*) AS Receivers_Count FROM Receivers GROUP BY City",
    "Provider_Type_Most_Food": "SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM Food_Listings GROUP BY Provider_Type ORDER BY Total_Quantity DESC",
    "Provider_Contacts": "SELECT City, Name, Contact, Type AS Provider_Type FROM Providers ORDER BY City, Name",
    "Top_Receivers_By_Claims": "SELECT r.Name, r.Type, COUNT(c.Claim_ID) AS Total_Claims FROM Receivers r LEFT JOIN Claims c ON r.Receiver_ID = c.Receiver_ID GROUP BY r.Name, r.Type ORDER BY Total_Claims DESC, r.Name",
    "Total_Quantity_Available": "SELECT SUM(Quantity) AS Total_Quantity FROM Food_Listings",
    "City_With_Most_Listings": "SELECT Location AS City, COUNT(*) AS Listings_Count FROM Food_Listings GROUP BY Location ORDER BY Listings_Count DESC, City",
    "Common_Food_Types": "SELECT Food_Type, COUNT(*) AS Items_Count FROM Food_Listings GROUP BY Food_Type ORDER BY Items_Count DESC, Food_Type",
    "Claims_Per_Food_Item": "SELECT Food_ID, COUNT(*) AS Claims_Count FROM Claims GROUP BY Food_ID ORDER BY Claims_Count DESC, Food_ID",
    "Provider_Most_Completed_Claims": "SELECT p.Name, COUNT(*) AS Completed_Claims FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID JOIN Providers p ON f.Provider_ID = p.Provider_ID WHERE c.Status = 'Completed' GROUP BY p.Name ORDER BY Completed_Claims DESC, p.Name",
    "Claim_Status_Percentage": "SELECT Status, COUNT(*) AS Count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM Claims), 2) AS Percentage FROM Claims GROUP BY Status ORDER BY Percentage DESC",
    "Avg_Qty_Per_Receiver": "SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity FROM Claims c JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID JOIN Food_Listings f ON c.Food_ID = f.Food_ID GROUP BY r.Name ORDER BY Avg_Quantity DESC, r.Name",
    "Most_Claimed_Meal_Type": "SELECT f.Meal_Type, COUNT(*) AS Claims_Count FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID GROUP BY f.Meal_Type ORDER BY Claims_Count DESC, f.Meal_Type",
    "Total_Qty_By_Provider": "SELECT p.Name, COALESCE(SUM(f.Quantity), 0) AS Total_Quantity FROM Providers p LEFT JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID GROUP BY p.Name ORDER BY Total_Quantity DESC, p.Name",
    "Top_Cities_Completed_Claims": "SELECT f.Location AS City, COUNT(*) AS Completed_Claims FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID WHERE c.Status = 'Completed' GROUP BY f.Location ORDER BY Completed_Claims DESC, City"
}

st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Providers", int(run_query("SELECT COUNT(*) AS c FROM Providers")["c"][0]))
col2.metric("Receivers", int(run_query("SELECT COUNT(*) AS c FROM Receivers")["c"][0]))
col3.metric("Food Listings", int(run_query("SELECT COUNT(*) AS c FROM Food_Listings")["c"][0]))
col4.metric("Claims", int(run_query("SELECT COUNT(*) AS c FROM Claims")["c"][0]))

st.markdown("---")
st.sidebar.header("Query Explorer")
query_choice = st.sidebar.selectbox("Pick a query to view", options=list(queries.keys()))
st.header("Query: " + query_choice.replace("_", " "))
df_q = run_query(queries[query_choice])
if not df_q.empty:
    st.write(df_q)
    if df_q.shape[1] == 2:
        st.altair_chart(alt.Chart(df_q).mark_bar().encode(
            x=alt.X(df_q.columns[0], sort='-y'),
            y=df_q.columns[1],
            tooltip=list(df_q.columns)
        ), use_container_width=True)
else:
    st.info("No data for this query.")

st.markdown("---")
st.subheader("Tables")
for name in ["Providers", "Receivers", "Food_Listings", "Claims"]:
    st.write(f"**{name}**")
    df = run_query(f"SELECT * FROM {name}")
    write_table(df, key=name)

st.markdown("---")
st.subheader("Notes (Project Deliverables)")
st.markdown(f"""
* This app uses the local SQLite DB file: `{DB_PATH}`  
* All 15 SQL queries from the project doc are available in the Query Explorer (left).  
* Charts shown are simple, use for quick analysis.  
* CRUD operations for Food_Listings and Claims are provided for demo/test.
""")

st.markdown("### How to run (summary)")
st.code("""
1) Save this file as app.py
2) Install: pip install pandas streamlit altair matplotlib sqlalchemy openpyxl
3) Run: streamlit run app.py
4) Open browser at the URL shown by Streamlit (usually http://localhost:8501)
""")

st.info("If something fails, copy the error message and paste in chat — I will fix it.")

st.markdown("---")
st.subheader("📊 All Charts Dashboard")

if st.checkbox("Show all charts for all queries"):
    for qname, qsql in queries.items():
        st.markdown(f"### {qname.replace('_', ' ')}")
        try:
            df_chart = run_query(qsql)
            if df_chart.empty:
                st.info("No data for this query.")
                continue

            st.dataframe(df_chart, use_container_width=True)

            
            if df_chart.shape[1] == 2:
                x = df_chart.columns[0]
                y = df_chart.columns[1]
                chart = alt.Chart(df_chart).mark_bar().encode(
                    x=alt.X(x, sort='-y'),
                    y=y,
                    tooltip=list(df_chart.columns)
                )
                st.altair_chart(chart, use_container_width=True)

            
            elif any("percentage" in col.lower() for col in df_chart.columns):
                fig, ax = plt.subplots()
                ax.pie(df_chart[df_chart.columns[1]],
                       labels=df_chart[df_chart.columns[0]],
                       autopct='%1.1f%%')
                st.pyplot(fig)

            else:
                x = df_chart.columns[0]
                y = df_chart.columns[1]
                chart = alt.Chart(df_chart).mark_line(point=True).encode(
                    x=x,
                    y=y,
                    tooltip=list(df_chart.columns)
                )
                st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Error in {qname}: {e}")

st.markdown("---")
st.subheader("Manage Food Listings (Add / Update / Delete)")

with st.expander("Add new food listing"):
    with st.form("add_food_form", clear_on_submit=True):
        new_id = st.number_input("Food_ID (unique int)", min_value=1, step=1, value=1)
        name = st.text_input("Food Name")
        qty = st.number_input("Quantity", min_value=0, step=1, value=1)
        exp = st.date_input("Expiry Date (optional)")
        provider_id = st.number_input("Provider_ID", min_value=0, step=1, value=0)
        provider_type = st.text_input("Provider_Type")
        location = st.text_input("Location / City")
        food_type = st.text_input("Food_Type (Vegetarian/Non-Vegetarian/Vegan)")
        meal_type = st.text_input("Meal_Type (Breakfast/Lunch/Dinner/Snacks)")
        submitted = st.form_submit_button("Add Food Listing")
        if submitted:
            exp_val = exp.strftime("%Y-%m-%d") if exp else None
            try:
                insert_food_listing({
                    "Food_ID": int(new_id) if new_id != 0 else None,
                    "Food_Name": name,
                    "Quantity": int(qty),
                    "Expiry_Date": exp_val,
                    "Provider_ID": int(provider_id) if provider_id != 0 else None,
                    "Provider_Type": provider_type,
                    "Location": location,
                    "Food_Type": food_type,
                    "Meal_Type": meal_type
                })
                st.success("New food listing added successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error("Insert failed: " + str(e))

with st.expander("Update / Delete food listing"):
    df_food = run_query("SELECT Food_ID, Food_Name, Quantity FROM Food_Listings")
    if not df_food.empty:
        chosen_f = st.selectbox("Pick Food_ID", options=df_food["Food_ID"].tolist())
        if chosen_f:
            frow = df_food[df_food["Food_ID"] == chosen_f].iloc[0]
            st.write(frow.to_dict())
            with st.form(f"update_food_{chosen_f}"):
                new_qty = st.number_input("New Quantity", value=int(frow["Quantity"]))
                btn_upf = st.form_submit_button("Update Quantity")
                btn_delf = st.form_submit_button("Delete Listing")
                if btn_upf:
                    try:
                        update_food_listing(int(chosen_f), {"Quantity": int(new_qty)})
                        st.success("Food listing updated.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Update failed: " + str(e))
                if btn_delf:
                    try:
                        delete_food_listing(int(chosen_f))
                        st.success("Food listing deleted.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Delete failed: " + str(e))
    else:
        st.info("No food listings available.")

st.markdown("---")
st.subheader("Manage Claims (Add / Update / Delete)")

with st.expander("Add new claim"):
    with st.form("add_claim_form", clear_on_submit=True):
        claim_id = st.number_input("Claim_ID (unique int)", min_value=1, step=1, value=1)
        f_id = st.number_input("Food_ID (to claim)", min_value=1, step=1, value=1)
        r_id = st.number_input("Receiver_ID", min_value=1, step=1, value=1)
        status = st.selectbox("Status", options=["Pending", "Completed", "Cancelled"])

        date_val = st.date_input("Date", value=datetime.today())
        time_val = st.time_input("Time", value=datetime.now().time())
        timestamp = datetime.combine(date_val, time_val)

        submitted = st.form_submit_button("Add Claim")
        if submitted:
            try:
                insert_claim({
                    "Claim_ID": int(claim_id) if claim_id != 0 else None,
                    "Food_ID": int(f_id),
                    "Receiver_ID": int(r_id),
                    "Status": status,
                    "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Claim added.")
                st.experimental_rerun()
            except Exception as e:
                st.error("Insert claim failed: " + str(e))

with st.expander("Update / Delete claim"):
    df_claims = run_query("SELECT Claim_ID, Food_ID, Receiver_ID, Status FROM Claims")
    if not df_claims.empty:
        chosen_c = st.selectbox("Pick Claim_ID", options=df_claims["Claim_ID"].tolist())
        if chosen_c:
            crow = df_claims[df_claims["Claim_ID"] == chosen_c].iloc[0]
            st.write(crow.to_dict())
            with st.form(f"update_claim_{chosen_c}"):
                new_status = st.selectbox(
                    "Status",
                    options=["Pending", "Completed", "Cancelled"],
                    index=["Pending","Completed","Cancelled"].index(crow["Status"]) if crow["Status"] in ["Pending","Completed","Cancelled"] else 0
                )
                btn_upc = st.form_submit_button("Update Claim")
                btn_delc = st.form_submit_button("Delete Claim")
                if btn_upc:
                    try:
                        update_claim(int(chosen_c), {"Status": new_status})
                        st.success("Claim updated.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Update failed: " + str(e))
                if btn_delc:
                    try:
                        delete_claim(int(chosen_c))
                        st.success("Claim deleted.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Delete failed: " + str(e))
    else:
        st.info("No claims available.")
