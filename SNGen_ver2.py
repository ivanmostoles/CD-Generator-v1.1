import streamlit as st
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import pandas as pd
import hashlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Helper function to load data from CSV
def load_data_from_csv(file_name):
    try:
        data = pd.read_csv(file_name)
        return data.to_dict(orient="records")
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        st.error(f"Error loading CSV file: {e}")
        return []

# Load data from predefined CSV files
DISCOVERY_MODELS = load_data_from_csv("discovery.csv")
USER_NAMES = load_data_from_csv("user.csv")
GROUP_NAMES = load_data_from_csv("group.csv")
LICENSE_SERVER_VALUES = load_data_from_csv("license_server.csv")
LICENSE_TYPE_VALUES = load_data_from_csv("license_type.csv")

# Ensure data is loaded
if not DISCOVERY_MODELS:
    st.error("No discovery models found. Ensure the 'discovery.csv' file exists and contains valid data.")
if not USER_NAMES:
    st.error("No user names found. Ensure the 'user.csv' file exists and contains valid data.")
if not GROUP_NAMES:
    st.error("No group names found. Ensure the 'group.csv' file exists and contains valid data.")
if not LICENSE_SERVER_VALUES:
    st.error("No license server found. Ensure the 'license_server.csv' file exists and contains valid data.")
if not LICENSE_TYPE_VALUES:
    st.error("No license type found. Ensure the 'license_type.csv' file exists and contains valid data.")

# Helper to generate unique hash
def generate_unique_hash():
    return hashlib.md5(str(random.random()).encode()).hexdigest()

# Function to generate three distinct numbers with constraints
def generate_distinct_numbers_with_constraints(total_sum, max_gap=5):
    if total_sum < 3:
        raise ValueError("The total sum must be at least 3 to generate three distinct numbers.")
    
    while True:
        num1 = random.randint(1, total_sum - 2)
        num2 = random.randint(1, total_sum - num1 - 1)
        num3 = total_sum - num1 - num2
        numbers = [num1, num2, num3]
        numbers.sort()
        if (len(set(numbers)) == 3 and all(n > 0 for n in numbers) and 
            numbers[2] - numbers[0] <= max_gap):
            return tuple(numbers)
        
# Function to generate a license XML record
def generate_license_xml(discovery, quantity):
    user = random.choice(USER_NAMES)
    group = random.choice(GROUP_NAMES)
    license_server = random.choice(LICENSE_SERVER_VALUES)
    license_type = random.choice(LICENSE_TYPE_VALUES)
    
    incremented_date = datetime.now().replace(year=datetime.now().year + 10)
    version_raw = discovery.get("version", "Unknown")
    try:
        # Convert to float and then int if it's a whole number
        version = str(int(float(version_raw))) if float(version_raw).is_integer() else str(version_raw)
    except ValueError:
        # If conversion fails, use the raw value as a fallback
        version = str(version_raw)

    license = ET.Element("samp_eng_app_license", action="INSERT_OR_UPDATE")
    ET.SubElement(license, "active").text = "true"
    ET.SubElement(license, "end_date").text = incremented_date.strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(license, "eng_software_install", display_value=discovery["software_install"]).text = discovery["software_install_sys_id"]
    ET.SubElement(license, "is_product_normalized").text = "true"
    ET.SubElement(license, "license_id").text = generate_unique_hash()
    ET.SubElement(license, "license_server", display_value=license_server["license_server"]).text = license_server["license_server_sys_id"]
    ET.SubElement(license, "license_type", display_value=license_type["license_type"]).text = license_type["license_type_sys_id"]
    ET.SubElement(license, "norm_product", display_value=discovery["norm_product"]).text = discovery["norm_product_sys_id"]
    ET.SubElement(license, "norm_publisher", display_value=discovery["norm_publisher"]).text = discovery["norm_publisher_sys_id"]
    ET.SubElement(license, "parent_id").text = ""
    ET.SubElement(license, "product").text = discovery["product"]
    ET.SubElement(license, "publisher").text = discovery["publisher"]
    ET.SubElement(license, "quantity").text = str(int(quantity))   #change
    ET.SubElement(license, "source").text = "OpeniT"
    ET.SubElement(license, "start_date").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(license, "sys_created_by").text = "admin"
    ET.SubElement(license, "sys_created_on").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(license, "sys_domain").text = generate_unique_hash()
    ET.SubElement(license, "sys_domain_path").text = "/"
    ET.SubElement(license, "sys_id").text = generate_unique_hash()
    ET.SubElement(license, "sys_mod_count").text = str(random.randint(1, 100))
    ET.SubElement(license, "sys_updated_by").text = "admin"
    ET.SubElement(license, "sys_updated_on").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(license, "version").text = version
    return license

# Function to generate a concurrent record with extended parameters
def generate_concurrent_record(record_data, discovery):
    concurrent_usage = ET.Element("samp_eng_app_concurrent_usage", action="INSERT_OR_UPDATE")
    ET.SubElement(concurrent_usage, "conc_usage_id").text = f"Con Usage {record_data['record_num']}"
    ET.SubElement(concurrent_usage, "concurrent_usage").text = str(record_data["value"])
    ET.SubElement(concurrent_usage, "license", display_value=discovery["norm_product"]).text = discovery["license_sys_id"]
    ET.SubElement(concurrent_usage, "source").text = "OpeniT"
    ET.SubElement(concurrent_usage, "sys_created_by").text = "admin"
    ET.SubElement(concurrent_usage, "sys_created_on").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(concurrent_usage, "sys_domain").text = generate_unique_hash()
    ET.SubElement(concurrent_usage, "sys_domain_path").text = "/"
    ET.SubElement(concurrent_usage, "sys_id").text = generate_unique_hash()
    ET.SubElement(concurrent_usage, "sys_mod_count").text = str(random.randint(1, 100))
    ET.SubElement(concurrent_usage, "sys_updated_by").text = "admin"
    ET.SubElement(concurrent_usage, "sys_updated_on").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(concurrent_usage, "usage_date").text = record_data["date"]
    return concurrent_usage

# Extended function to generate denial records
def generate_denial_record_extended(record_data, discovery, user, group, license_server, license_type):
    denial = ET.Element("samp_eng_app_denial", action="INSERT_OR_UPDATE")
    ET.SubElement(denial, "additional_key")
    ET.SubElement(denial, "computer", display_value=user["computer_name"]).text = user["computer_sys_id"]
    ET.SubElement(denial, "denial_date").text = record_data["date"]  # Use "date" as "denial_date"
    ET.SubElement(denial, "denial_id").text = f"Denial {record_data['record_num']}"  # Unique denial ID
    ET.SubElement(denial, "discovery_model", display_value=discovery["discovery_model"]).text = discovery["discovery_sys_id"]
    ET.SubElement(denial, "group", display_value=group["group"]).text = group["group_sys_id"]
    ET.SubElement(denial, "is_product_normalized").text = "true"
    ET.SubElement(denial, "last_denial_time").text = datetime.now().strftime("%Y-%m-%d %H:%M")
    ET.SubElement(denial, "license_server", display_value=license_server["license_server"]).text = license_server["license_server_sys_id"]
    ET.SubElement(denial, "license_type", display_value=license_type["license_type"]).text = license_type["license_type_sys_id"]
    ET.SubElement(denial, "norm_product", display_value=discovery["norm_product"]).text = discovery["norm_product_sys_id"]
    ET.SubElement(denial, "norm_publisher", display_value=discovery["norm_publisher"]).text = discovery["norm_publisher_sys_id"]
    ET.SubElement(denial, "product").text = discovery["product"]
    ET.SubElement(denial, "publisher").text = discovery["publisher"]
    ET.SubElement(denial, "source").text = "OpeniT"
    ET.SubElement(denial, "sys_created_by").text = "admin"
    ET.SubElement(denial, "sys_created_on").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(denial, "sys_domain").text = generate_unique_hash()
    ET.SubElement(denial, "sys_domain_path").text = "/"
    ET.SubElement(denial, "sys_id").text = generate_unique_hash()
    ET.SubElement(denial, "sys_mod_count").text = str(random.randint(1, 100))
    ET.SubElement(denial, "sys_updated_by").text = "admin"
    ET.SubElement(denial, "sys_updated_on").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(denial, "total_denial_count").text = str(record_data["value"])  # Use "value" as "total_denial_count"
    ET.SubElement(denial, "user", display_value=user["user"]).text = user["user_sys_id"]
    ET.SubElement(denial, "version").text = "2020"
    ET.SubElement(denial, "workstation", display_value=user["workstation"]).text = user["workstation_sys_id"]
    return denial

# Streamlit app
st.title("CD Generator")

# Input Section
st.header("Input Parameters")
date_range = st.date_input("Select Date Range", [datetime.today(), datetime.today()])
quantity = st.number_input("Enter Quantity (Threshold/Peak Value)", min_value=1, step=1)
num_records = st.number_input("Enter Total Number of Records (Concurrent Usage)", min_value=1, step=1)
range_start = st.number_input("Overpeak Range Start", min_value=1, step=1)
range_end = st.number_input("Overpeak Range End", min_value=range_start, step=1)
generate_button = st.button("Generate Records")

# Generate Records
if generate_button:
    start_date = date_range[0]
    end_date = date_range[1]
    total_days = (end_date - start_date).days + 1

    # Concurrent Records
    concurrent_root = ET.Element("unload")
    concurrent_root.set("unload_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Denial Records
    denial_root = ET.Element("unload")
    denial_root.set("unload_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # License Records
    license_root = ET.Element("unload")
    license_root.set("unload_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    increment_value = quantity // num_records
    value = increment_value
    record_list = []
    phase = "increment"
    denial_generated = 0

    for day_offset in range(total_days):
        current_date = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

        if phase == "increment":
            record_list.append({"record_num": len(record_list) + 1, "value": value, "date": current_date})
            value += increment_value
            if value >= quantity:
                value = quantity
                phase = "denial"
                denial_generated = 0

        elif phase == "denial":
            if denial_generated == 0:
                denial_count = random.randint(range_start, range_end)

            if denial_generated < denial_count:
                discovery = random.choice(DISCOVERY_MODELS)
                user = random.choice(USER_NAMES)
                group = random.choice(GROUP_NAMES)
                license_server = random.choice(LICENSE_SERVER_VALUES)
                license_type = random.choice(LICENSE_TYPE_VALUES)

                denial_root.append(generate_denial_record_extended(
                    {"date": current_date, "value": increment_value, "record_num": len(record_list) + 1},
                    discovery, user, group, license_server, license_type
                ))

                record_list.append({"record_num": len(record_list) + 1, "value": quantity, "date": current_date})
                denial_generated += 1

                if denial_generated >= denial_count:
                    phase = "decrement"
                    value -= increment_value
                else:
                    # Increment the date only if still in the denial phase
                    current_date = (datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

        elif phase == "decrement":
            record_list.append({"record_num": len(record_list) + 1, "value": value, "date": current_date})
            if value <= quantity / 2:
                phase = "increment"
                value += increment_value
            else:
                value -= increment_value
                current_date = (datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    # Generate Concurrent XML Records
    for record in record_list:
        total_usage = record["value"]
        base_usage = total_usage // 3
        remainder = total_usage % 3

        # Distribute the remainder randomly among the three products
        distributed_usage = [base_usage] * 3
        for _ in range(remainder):
            distributed_usage[random.randint(0, 2)] += 1

        # Generate records for each product
        for i, product in enumerate(["AutoCAD Architecture", "ArcGIS 3D Analyst", "Advanced Meshing"]):
            # Find the correct discovery model for the product from the CSV
            discovery = next((model for model in DISCOVERY_MODELS if model["norm_product"] == product), None)

            if discovery:
                # Update record value for each product
                product_record = record.copy()
                product_record["value"] = distributed_usage[i]
                concurrent_root.append(generate_concurrent_record(product_record, discovery))
            else:
                st.error(f"Discovery model not found for product: {product}")
    
    # Generate License XML Records
    st.header("Generating License XML")
    try:
        license_quantities = generate_distinct_numbers_with_constraints(quantity, max_gap=5)
    except ValueError as e:
        st.error(f"Error generating license quantities: {str(e)}")
        st.stop()

    for i, qty in enumerate(license_quantities):
        if i < len(DISCOVERY_MODELS):
            discovery = DISCOVERY_MODELS[i]
            license_record = generate_license_xml(discovery, qty)
            license_root.append(license_record)

    # Convert XML trees to strings
    license_xml_data = ET.tostring(license_root, encoding="utf-8").decode("utf-8")
    concurrent_xml_data = ET.tostring(concurrent_root, encoding="utf-8").decode("utf-8")
    denial_xml_data = ET.tostring(denial_root, encoding="utf-8").decode("utf-8")

    st.session_state["concurrent_xml"] = concurrent_xml_data
    st.session_state["denial_xml"] = denial_xml_data
    st.session_state["license_xml"] = license_xml_data

    st.success("Records Generated Successfully!")


def parse_concurrent_xml(concurrent_xml_data):
    tree = ET.ElementTree(ET.fromstring(concurrent_xml_data))
    root = tree.getroot()
    daily_usage = {}

    for record in root.findall("samp_eng_app_concurrent_usage"):
        date_str = record.find("usage_date").text
        value = int(record.find("concurrent_usage").text)

        # Aggregate usage for the same date
        if date_str in daily_usage:
            daily_usage[date_str] += value
        else:
            daily_usage[date_str] = value

    # Sort dates and convert to lists
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in sorted(daily_usage.keys())]
    values = [daily_usage[date.strftime("%Y-%m-%d")] for date in dates]
    return dates, values

# Helper function to parse Denial XML
def parse_denial_xml(denial_xml_data):
    tree = ET.ElementTree(ET.fromstring(denial_xml_data))
    root = tree.getroot()
    dates = []
    values = []
    for record in root.findall("samp_eng_app_denial"):
        date_str = record.find("denial_date").text
        value = int(record.find("total_denial_count").text)
        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))  # Convert to datetime object
        values.append(value)
    return dates, values

# Generate the graph
if "concurrent_xml" in st.session_state and "denial_xml" in st.session_state:
    st.header("Graphical Representation of Records")

    # Parse the Concurrent XML
    concurrent_dates, concurrent_values = parse_concurrent_xml(st.session_state["concurrent_xml"])

    # Parse the Denial XML
    denial_dates, denial_values = parse_denial_xml(st.session_state["denial_xml"])

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the Concurrent Records (Line Graph)
    ax.plot(concurrent_dates, concurrent_values, label="Concurrent Records", color="blue", marker="o")

    # Plot the Denial Records (Bar Graph)
    ax.bar(denial_dates, denial_values, label="Denial Records", color="red", alpha=0.6)

    # Add a threshold line for the peak value (e.g., 100)
    threshold_value = max(concurrent_values)  # Assuming the threshold is the peak value
    ax.axhline(y=threshold_value, color="orange", linestyle="--", linewidth=2, label=f"Peak ({threshold_value})")

    # Format the x-axis to show dates properly
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Adjust interval as needed
    plt.xticks(rotation=45, ha="right")

    # Add labels, title, and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.set_title("Concurrent and Denial Records")
    ax.legend()

    # Display the graph in Streamlit
    st.pyplot(fig)


# Display Concurrent XML
if "concurrent_xml" in st.session_state:
    st.subheader("Concurrent XML")
    st.code(st.session_state["concurrent_xml"], language="xml")
    st.download_button(
        label="Download Concurrent XML",
        data=st.session_state["concurrent_xml"],
        file_name="concurrent_records.xml",
        mime="application/xml"
    )

# Display Denial XML
if "denial_xml" in st.session_state:
    st.subheader("Denial XML")
    st.code(st.session_state["denial_xml"], language="xml")
    st.download_button(
        label="Download Denial XML",
        data=st.session_state["denial_xml"],
        file_name="denial_records.xml",
        mime="application/xml"
    )

# Display License XML
if "license_xml" in st.session_state:
    st.subheader("License XML")
    st.code(st.session_state["license_xml"], language="xml")
    st.download_button(
        label="Download License XML",
        data=st.session_state["license_xml"],
        file_name="license_records.xml",
        mime="application/xml"
    )
