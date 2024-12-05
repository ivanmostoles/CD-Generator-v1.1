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

# Ensure data is loaded
if not DISCOVERY_MODELS:
    st.error("No discovery models found. Ensure the 'discovery.csv' file exists and contains valid data.")


# Helper to generate unique hash
def generate_unique_hash():
    return hashlib.md5(str(random.random()).encode()).hexdigest()


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


# Function to generate denial records
def generate_denial_record(record_data):
    denial = ET.Element("denial_record")
    ET.SubElement(denial, "date").text = record_data["date"]
    ET.SubElement(denial, "value").text = str(record_data["value"])
    return denial


# Streamlit app
st.title("CD Generator with Extended Parameters")

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
    denial_root = ET.Element("denial_records")
    denial_count = random.randint(range_start, range_end)
    denial_generated = 0

    increment_value = quantity // num_records
    value = increment_value

    record_list = []
    phase = "increment"

    for day_offset in range(total_days):
        current_date = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")

        if phase == "increment":
            # Incremental records
            record_list.append({"record_num": len(record_list) + 1, "value": value, "date": current_date})
            value += increment_value
            if value >= quantity:
                value = quantity
                phase = "denial"
                denial_generated = 0

        elif phase == "denial":
            # Denial and peak records
            if denial_generated < denial_count:
                denial_root.append(generate_denial_record({"date": current_date, "value": increment_value}))
                record_list.append({"record_num": len(record_list) + 1, "value": quantity, "date": current_date})
                denial_generated += 1
            else:
                phase = "decrement"
                value -= increment_value

        elif phase == "decrement":
            # Decremental records
            record_list.append({"record_num": len(record_list) + 1, "value": value, "date": current_date})
            if value <= quantity / 2:
                # Transition back to increment phase, starting from the last valid value
                phase = "increment"
                value += increment_value
            else:
                value -= increment_value

    # Generate Concurrent XML Records
    for record in record_list:
        discovery = random.choice(DISCOVERY_MODELS)
        concurrent_root.append(generate_concurrent_record(record, discovery))

    # Convert XML trees to strings
    concurrent_xml_data = ET.tostring(concurrent_root, encoding="utf-8").decode("utf-8")
    denial_xml_data = ET.tostring(denial_root, encoding="utf-8").decode("utf-8")

    # Store XML data in session state for persistence
    st.session_state["concurrent_xml"] = concurrent_xml_data
    st.session_state["denial_xml"] = denial_xml_data

    st.success("Records Generated Successfully!")

# Helper function to parse Concurrent XML
def parse_concurrent_xml(concurrent_xml_data):
    tree = ET.ElementTree(ET.fromstring(concurrent_xml_data))
    root = tree.getroot()
    dates = []
    values = []
    for record in root.findall("samp_eng_app_concurrent_usage"):
        date = record.find("usage_date").text
        value = int(record.find("concurrent_usage").text)
        dates.append(date)
        values.append(value)
    return dates, values

# Helper function to parse Denial XML
def parse_denial_xml(denial_xml_data):
    tree = ET.ElementTree(ET.fromstring(denial_xml_data))
    root = tree.getroot()
    dates = []
    values = []
    for record in root.findall("denial_record"):
        date = record.find("date").text
        value = int(record.find("value").text)
        dates.append(date)
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

    # Format the x-axis to show dates properly
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
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
