# IMPORTING NECESSARY LIBRARIES

import streamlit as st
import easyocr
import mysql.connector
import cv2
import numpy as np
import pandas as pd
from streamlit_option_menu import option_menu
import streamlit_lottie
from streamlit_lottie import st_lottie
import json
import requests
from mysql.connector import Error

# SQL CONNECTION

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    auth_plugin="mysql_native_password"
)

# SQL DATABASE

my_cursor = mydb.cursor()
my_cursor.execute("USE vimin")

# TABLE CREATION

my_cursor.execute(
    "CREATE TABLE IF NOT EXISTS ocr (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), job_title VARCHAR(255), address VARCHAR(255), postcode VARCHAR(255), phone VARCHAR(255), email VARCHAR(255), website VARCHAR(255), company_name VARCHAR(225))")

# OCR CREATION

reader = easyocr.Reader(['en'])


# LOTTIE CREATION

def load_lottieurl(url):

    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_coding = load_lottieurl("https://lottie.host/dbb7f138-041e-4f1b-b2ca-cc3997cf5a5c/X948Jq1JFY.json")

# STREAMLIT PAGE CONFIGURATION

st.set_page_config(page_title="BUSINESS CARD EXTRACTION ",
                   page_icon=":tada",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """YTH"""})

# OPTION MENU

with st.sidebar:
    choice = option_menu(None, ['Home', 'Add', 'View', 'Update', 'Delete'],
                         default_index=0,
                         orientation="vertical",
                         styles={"nav-link": {"font-size": "25px", "text-align": "left", "margin": "10px",
                                              "--hover-color": "grey"},
                                 "container": {"max-width": "3000px"},
                                 "nav-link-selected": {"background-color": "grey"}})


# STREAMLIT BACKGROUND

st.markdown(
    f"""
         <style>
         .stApp {{
             background: #313866;
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
    unsafe_allow_html=True

)

# HOME PAGE

if choice == 'Home':
    with st.container():
        st.title(":white[Extracting Business Card Data with OCR]")
    with st.container():
        st.header(""":white[Overview]""")
    with st.container():
        st.write("""This Streamlit application that allows users to upload
        an image of a business card and extract relevant information from it using easyOCR.
        The extracted information would include the company name, card holder name,
        designation, mobile number, email address, website URL, area, city, state, and pincode.
        The extracted information would then be displayed in the application's graphical user interface (GUI).""")
    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.header(":white[Technologies Used]")
            st.write("Python , MySQL ,OCR , Streamlit")
        with right_column:
            st_lottie(lottie_coding, height=300, key="coding")


# ADD PAGE

if choice == 'Add':
    uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # IMAGE READING

        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)

        # UPLOADED IMAGE

        st.image(image, caption='Uploaded business card image', use_column_width=True)

        # EXTRACTION OF THE IMAGE

        if st.button('Extract Information'):
            bounds = reader.readtext(image, detail=0)
            text = "\n".join(bounds)
            sql = "INSERT INTO ocr(name, job_title, address, postcode, phone, email, website, company_name) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5], bounds[6], bounds[7])
            my_cursor.execute(sql, val)
            mydb.commit()

            st.success("Business card information added to database.")

# VIEW PAGE

elif choice == 'View':
    st.title("View the details in the database")
    my_cursor.execute("SELECT * FROM ocr")
    result = my_cursor.fetchall()
    df = pd.DataFrame(result, columns=['id', 'name', 'job_title', 'address', 'postcode', 'phone', 'email', 'website',
                                       'company_name'])
    st.dataframe(df)

# UPDATE PAGE

elif choice == 'Update':
    st.title("Update the required field")
    my_cursor.execute("SELECT id, name FROM ocr")
    result = my_cursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[1]] = row[0]
    selected_card_name = st.selectbox("Select a business card to update", list(business_cards.keys()))

    my_cursor.execute("SELECT * FROM ocr WHERE name=%s", (selected_card_name,))
    result = my_cursor.fetchone()

    # GIVEN INFORMATION

    st.write("Name:", result[1])
    st.write("Job Title:", result[2])
    st.write("Address:", result[3])
    st.write("Postcode:", result[4])
    st.write("Phone:", result[5])
    st.write("Email:", result[6])
    st.write("Website:", result[7])
    st.write("company_name:", result[8])

    # NEW INFORMATION

    name = st.text_input("Name", result[1])
    job_title = st.text_input("Job Title", result[2])
    address = st.text_input("Address", result[3])
    postcode = st.text_input("Postcode", result[4])
    phone = st.text_input("Phone", result[5])
    email = st.text_input("Email", result[6])
    website = st.text_input("Website", result[7])
    company_name = st.text_input("Company Name", result[8])

    # UPDATE

    if st.button("Update Business Card"):
        my_cursor.execute(
            "UPDATE ocr SET name=%s, job_title=%s, address=%s, postcode=%s, phone=%s, email=%s, website=%s, company_name=%s WHERE name=%s",
            (name, job_title, address, postcode, phone, email, website, company_name, selected_card_name))
        mydb.commit()
        st.success("Business card information updated in database.")

# DELETE PAGE

elif choice == 'Delete':
    st.title("Delete the record")
    my_cursor.execute("SELECT id, name FROM ocr")
    result = my_cursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[1]
    selected_card_id = st.selectbox("Select a business card to delete", list(business_cards.keys()),
                                    format_func=lambda x: business_cards[x])

    # SELECTION

    my_cursor.execute("SELECT name FROM ocr WHERE id=%s", (selected_card_id,))
    result = my_cursor.fetchone()
    selected_card_name = result[0]

    st.write("Name:", selected_card_name)

    if st.button("Delete Business Card"):
        my_cursor.execute("DELETE FROM ocr WHERE name=%s", (selected_card_name,))
        mydb.commit()
        st.success("Business card information deleted from database.")
