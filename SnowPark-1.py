from snowflake.snowpark import Session
import streamlit as st
import pandas as pd
import datetime
import toml

# Load credentials from the TOML file
config = toml.load("Snowflake-TOML.txt")
pars = config["connection"]

tab1, tab2 = st.tabs(["Employee Data", "Employee Charts"])

with tab1:
    st.title("Snowflake Streamlit App")
    st.header("Snowflake Employee Data")



session = Session.builder.configs(pars).create()

df = session.sql("select * from employees")



st.dataframe(df)

rows = df.collect()
dfp = df.to_pandas().copy()
print(dfp)

# Initialize the toggle in session_state
if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

# Button to toggle the form
if st.button("New Employee Submission"):
    st.session_state["show_form"] = not st.session_state["show_form"]

if st.session_state["show_form"]:
    with st.form("add_employee_form"):
        new_employee_name = st.text_input("Employee Name", 
                                          )
        new_manager_name = st.text_input("Manager Name", key="new_manager_name")
        new_employee_id = st.text_input("Employee ID", key="new_employee_id")
        new_manager_id = st.text_input("Manager ID", key="new_manager_id")
        new_phone_number = st.text_input("Phone Number", key="new_phone_number")
        new_hire_date = st.date_input("Hire Date", key="new_hire_date")
        new_salary = st.number_input("Salary", min_value=0, key="new_salary")
        new_job = st.text_input("Job", key="new_job")
        new_department = st.selectbox(
            "Department",
            ["SALES", "FINANCE", "PRESIDENCE", "IT", "ANALYTICS", "DOCUMENTATION"],
            key="new_department"
        )
        submitted = st.form_submit_button("Add Employee")
    if submitted:
        # Create a new row as a dictionary
        new_row = {
            "EMPLOYEE_NAME": new_employee_name,
            "MANAGER_NAME": new_manager_name,
            "EMPLOYEE_ID": new_employee_id,
            "MANAGER_ID": new_manager_id,
            "PHONE_NUMBER": new_phone_number,
            "HIRE_DATE": new_hire_date,
            "SALARY": new_salary,
            "JOB": new_job,
            "DEPARTMENT": new_department
        }
        # Append the new row to the DataFrame
        #dfp = dfp.append(new_row, ignore_index=True)
        dfp = pd.concat([dfp, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Employee added!")

        # Append the new row to the Snowflake table
        snowpark_new_row = session.create_dataframe([new_row])
        snowpark_new_row.write.save_as_table("EMPLOYEES", mode="append")

        # Reset fields
                # Reset fields
       

        st.rerun()  # This will reset the form fields



# Let user select an employee by Employee ID
employee_names = dfp["EMPLOYEE_NAME"].tolist()
selected_name = st.selectbox("Select Employee to Edit", employee_names)

# Get the selected row
selected_row = dfp[dfp["EMPLOYEE_NAME"] == selected_name].iloc[0]

with st.form("edit_employee_form"):
    edit_employee_name = st.text_input("Employee Name", value=selected_row["EMPLOYEE_NAME"])
    edit_manager_name = st.text_input("Manager Name", value=selected_row["MANAGER_NAME"])
    edit_manager_id = st.text_input("Manager ID", value=selected_row["MANAGER_ID"])
    edit_phone_number = st.text_input("Phone Number", value=selected_row["PHONE_NUMBER"])
    edit_hire_date = st.date_input("Hire Date", value=selected_row["HIRE_DATE"])
    edit_salary = st.number_input("Salary", min_value=0, value=int(selected_row["SALARY"]))
    edit_job = st.text_input("Job", value=selected_row["JOB"])
    edit_department = st.selectbox(
        "Department",
        ["SALES", "FINANCE", "Finance", "PRESIDENCE", "IT", "ANALYTICS", "DOCUMENTATION"],
        index=["SALES", "FINANCE", "Finance", "PRESIDENCE", "IT", "ANALYTICS", "DOCUMENTATION"].index(selected_row["DEPARTMENT"])
    )
    submitted_edit = st.form_submit_button("Update Employee")

if submitted_edit:
    # Update DataFrame
    dfp.loc[dfp["EMPLOYEE_NAME"] == selected_name, [
        "EMPLOYEE_NAME", "MANAGER_NAME", "MANAGER_ID", "PHONE_NUMBER", "HIRE_DATE", "SALARY", "JOB", "DEPARTMENT"
    ]] = [
        edit_employee_name, edit_manager_name, edit_manager_id, edit_phone_number, edit_hire_date, edit_salary, edit_job, edit_department
    ]
    st.success("Employee updated in local DataFrame.")

    # Update Snowflake
    update_sql = f"""
        UPDATE EMPLOYEES
        SET
            EMPLOYEE_NAME = '{edit_employee_name}',
            MANAGER_NAME = '{edit_manager_name}',
            MANAGER_ID = '{edit_manager_id}',
            PHONE_NUMBER = '{edit_phone_number}',
            HIRE_DATE = '{edit_hire_date}',
            SALARY = {edit_salary},
            JOB = '{edit_job}',
            DEPARTMENT = '{edit_department}'
        WHERE EMPLOYEE_NAME = '{selected_name}'
    """
    session.sql(update_sql).collect()
    st.success("Employee updated in Snowflake.")
# Show the updated DataFrame
st.header("Updated DataFrame")
st.dataframe(dfp)

with tab2:
    st.header("Average Salary by Department")
    if not dfp.empty:
        avg_salary_by_department = dfp.groupby("DEPARTMENT")["SALARY"].mean().reset_index()
        st.bar_chart(data=avg_salary_by_department, x="DEPARTMENT", y="SALARY")
    else:
        st.write("No data available to display chart.")
