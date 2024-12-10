import streamlit as st
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
import pandas as pd
import random


def load_data_from_csv(file_name):
    try:
        data = pd.read_csv(file_name)
        return data.to_dict(orient="records")
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        st.error(f"Error loading CSV file: {e}")
        return []

current_date = datetime.now()
incremented_date = current_date.replace(year=current_date.year + 10)

# Usage:
USER_NAMES = load_data_from_csv("user.csv")
DISCOVERY_MODELS = load_data_from_csv("discovery.csv")
GROUP_NAMES = load_data_from_csv("group.csv")
LICENSE_SERVER_VALUES = load_data_from_csv("license_server.csv")
LICENSE_TYPE_VALUES = load_data_from_csv("license_type.csv")
SOFTWARE_INSTALL = load_data_from_csv("software_install.csv")


if not USER_NAMES:
    st.error("No user names found. Ensure the 'user.csv' file exists and contains valid data.")
if not DISCOVERY_MODELS:
    st.error("No discovery models found. Ensure the 'discovery.csv' file exists and contains valid data.")
if not GROUP_NAMES:
    st.error("No group names found. Ensure the 'group.csv' file exists and contains valid data.")
if not LICENSE_SERVER_VALUES:
    st.error("No license server found. Ensure the 'license_server.csv' file exists and contains valid data.")
if not LICENSE_TYPE_VALUES:
    st.error("No license type found. Ensure the 'license_type.csv' file exists and contains valid data.")


def generate_unique_hash():
    """Generates a unique hash value to ensure each XML field requiring a hash is unique and randomized."""
    return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()


def generate_distinct_numbers_with_constraints(total_sum, max_gap=5):
    """
    Generate three distinct numbers that sum up to the total_sum.
    Ensures:
    1. Numbers are distinct.
    2. No number is zero.
    3. The difference (gap) between any two numbers does not exceed max_gap.
    """
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


def generate_xml_record(discovery, quantity):
    # Randomly select other values
    user = random.choice(USER_NAMES)
    group = random.choice(GROUP_NAMES)
    license_server = random.choice(LICENSE_SERVER_VALUES)
    license_type = random.choice(LICENSE_TYPE_VALUES)

    version_raw = discovery.get("version", "Unknown")
    try:
        # Convert to float and then int if it's a whole number
        version = str(int(float(version_raw))) if float(version_raw).is_integer() else str(version_raw)
    except ValueError:
        # If conversion fails, use the raw value as a fallback
        version = str(version_raw)
    

    # Create the <samp_eng_app_license> element with "INSERT_OR_UPDATE" action
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


st.title("XML Record Generator with Quantity Distribution")

# Input for the total sum of the quantity
total_sum_input = st.text_input("Enter the total sum of the quantity", value="")

if st.button("Generate XML"):
    if not DISCOVERY_MODELS or len(DISCOVERY_MODELS) < 3:
        st.error("Discovery models data must have at least 3 entries.")
    elif not total_sum_input.isdigit():
        st.error("Please enter a valid numeric total sum.")
    else:
        total_sum = int(total_sum_input)

        try:
            quantities = generate_distinct_numbers_with_constraints(total_sum, max_gap=5)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        root = ET.Element("unload")
        root.set("unload_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Generate records using DISCOVERY_MODELS[0], [1], [2] and assign quantities
        for i in range(3):
            record = generate_xml_record(DISCOVERY_MODELS[i], quantities[i])
            root.append(record)

        xml_data = ET.tostring(root, encoding="utf-8").decode("utf-8")
        st.code(xml_data, language="xml")
        st.download_button(
            label="Download XML",
            data=xml_data,
            file_name="samp_eng_app_license.xml",
            mime="application/xml"
        )
