import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
import pymongo
from bson.objectid import ObjectId
import plotly.graph_objects as go

# # Set Streamlit theme configuration
st.set_page_config(page_title="BuildTogether", page_icon="", layout="wide", initial_sidebar_state="auto")

# st.markdown(
#     """
#     <style>
#     :root {
#         --theme-font: 'sans serif';
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )


#  # ---- READ EXCEL ----
#     df = pd.read_excel(
#             io="data.xlsx",
#             engine="openpyxl",
#             sheet_name="data",
#             skiprows=0,
#             usecols="A:G",
#             nrows=46,
#         )


client = pymongo.MongoClient("mongodb+srv://2020ashishgupta:diversity@cluster0.f7gobiq.mongodb.net/")
db = client["buildtogether"]

# collection = db["employee data"]
# data = collection.find()
# df = pd.DataFrame(data)

#---Navigation Menu---
selected = option_menu(
    menu_title=None,
    options=["Job", "Dashboard", "Campus & Vendors"],
    icons=[ "people", "pencil-fill", "bar-chart-fill"],
    orientation="horizontal",
)


if selected == "Job":

    # client = pymongo.MongoClient("mongodb+srv://2020ashishgupta:diversity@cluster0.f7gobiq.mongodb.net/")
    # db = client["buildtogether"]
    #create a database for data collection
    job_collection = db["job"]
    applicant_collection = db["applicant"]


    #function post a job
    def post_job():
        st.header("Post a Job")

        department = ["Sales", "Marketing", "Finance", "Technology", "HR"]
        band = ["Entry", "Associate", "Manger"]

        department = st.selectbox("Department", department)
        band = st.selectbox("Band", band)
        title = st.text_input("Job Title")
        description = st.text_area("Job Description")

        if st.button("Post Job", key="post_job_button"):
            job_data = {
                "department": department,
                "band": band,
                "title": title,
                "description": description 
            }

            job_id = job_collection.insert_one(job_data)
            st.success("Job Posted Successfully!")

    

    #function to veiw about current job opening
    def view_job_openings():
        
        st.header("Job Opening")

        department = ["Sales", "Marketing", "Finance", "Technology", "HR"]
        band = ["Entry", "Associate", "Manger"]

        department = st.selectbox("Department", department)
        band = st.selectbox("Band", band)

        jobs = job_collection.find({"department": department, "band": band})

        for job in jobs:
            st.subheader(job["title"])
            st.write("Department:", job["department"])
            st.write("Band:", job["band"])
            st.write("Job Description:", job["description"])

            apply_job(job["_id"])


    #function to apply for a job
    def apply_job(job_id):
        st.header("Apply for Job")

        job = job_collection.find_one({"_id": job_id})

        st.subheader("Applicant Details")

        # Use session_state to retain form data
        if 'applicant_data' not in st.session_state:
                st.session_state.applicant_data = {
                    "name": "",
                    "email": "",
                    "age": 18,
                    "gender": "Male",
                    "referral": False,
                    "referral_name": "",
                    "description": "",
                    "cv": None
                }

        
        name = st.text_input("Name", value=st.session_state.applicant_data["name"])
        email = st.text_input("Email", value=st.session_state.applicant_data["email"])
        age = st.number_input("Age", min_value=18, max_value=65, value=st.session_state.applicant_data["age"])
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if st.session_state.applicant_data["gender"]=="Male" else 1 if st.session_state.applicant_data["gender"]=="Female" else 2)

        referral = st.checkbox("Referral", value=st.session_state.applicant_data["referral"])
        if referral:
            referral_name = st.text_input("Referral Name", value=st.session_state.applicant_data["referral_name"])
        else:
            referral_name = ""
        
        description = st.text_area("Describe yourself in 300 characters", value=st.session_state.applicant_data["description"], max_chars=300)

        cv = st.file_uploader("Upload CV")

        if st.button("Submit", key="applicant_button"):
            if name and email and gender and description and cv:
                cv_content = cv.read()

                applicant_data = {
                    "job_id": str(job_id),
                    "department": job["department"],
                    "band": job["band"],
                    "name": name,
                    "email": email,
                    "age": age,
                    "gender": gender,
                    "referral": referral,
                    "referral_name": referral_name if referral else None,
                    "description": description,
                    "cv": cv_content
                }

                app_id = applicant_collection.insert_one(applicant_data)
                st.success("Aplication Submitted Successfully")

                #Refresh form
                st.session_state.applicant_data = {
                    "name": "",
                    "email": "",
                    "age": 18,
                    "gender": "Male",
                    "referral": False,
                    "referral_name": "",
                    "description": "",
                    "cv": None
                }
            else:
                st.warning("Please fill all details")


    #function to visualize the candidates
    def visualize_candidates():
        st.header("Visualize Candidate")

        department = ["Sales", "Marketing", "Finance", "Technology", "HR"]
        band = ["Entry", "Associate", "Manger"]
        genders = ["Male", "Female", "Others"]

        department = st.selectbox("Department", department)
        band = st.selectbox("Band", band)
        gender_filter = st.selectbox("Filter by Gender", genders)
        referral_filter = st.checkbox("Filter by Referral")

        candidates = applicant_collection.find({"job_id": {"$ne": None}})

        for candidate in candidates:
            applicant = applicant_collection.find_one({"_id": ObjectId(candidate["_id"])})
            if applicant["department"]== department and applicant["band"] ==band:
                if gender_filter !="All" and applicant["gender"] !=gender_filter:
                    continue
                if referral_filter and not applicant["referral"]:
                    continue

                name= candidate["name"]
                gender=candidate["gender"]
                age= candidate["age"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader(name)
                with col2:
                    st.subheader(f"{gender}")
                with col3:
                    st.subheader(f"{age}")
                st.write("Description:", candidate["description"][:300])

                if st.button("Read More",f"{candidate['_id']}"):
                    view_questionaire(candidate["_id"])

                

    # function to read the questionaire
    def view_questionaire(candidate_id):
        candidate = applicant_collection.find_one({"_id": ObjectId(candidate_id)})
        st.write("Name:", candidate["name"])
        st.write("Email:", candidate["email"])
        st.write("Age", candidate["age"])
        st.write("Gender", candidate["gender"])
        st.write("Referral", candidate["referral"])
        if candidate["referral"]:
            st.write("Referral Name", candidate["referral_name"])
        st.write("Description", candidate["description"])


    #main function
    def main():
        st.title("Job Portal")

        st.sidebar.header("Navigation")
        menu = st.sidebar.radio("Go to", ("Post a Job", "View Job Openings", "Applicant"))

        if menu == "Post a Job":
            post_job()
        elif menu == "View Job Openings":
            view_job_openings()
        elif menu == "Applicant":
            visualize_candidates()
    
    if __name__ == "__main__":
        main()




  



if selected == "Dashboard":

    collection = db["employee data"]
    data = collection.find()
    df = pd.DataFrame(data)



    #---slidebar----
    st.sidebar.header("Select the Filter:")
    department = st.sidebar.multiselect(
        "Select the Department:",
        options=df["Department"].unique(),
        default=df["Department"].unique()
    )

    band = st.sidebar.multiselect(
        "Select the Band:",
        options=df["Band"].unique(),
        default=df["Band"].unique()
    )

    df_selection = df.query(
        "Department == @department & Band == @band"
    )


    #st.dataframe(df_selection)

    #---Main Page--
    st.title("Diversity Dashboard")
    st.markdown("##")

    #--Plot Pie Chart
    diversity = df_selection
    pc1 = px.pie(diversity,
                 title='Diversity Overview',
                 values='Count',
                 names='Gender')
    
    pc2 = px.pie(diversity,
                 title='D&I Goals',
                 values=[60, 35, 5],
                 names=['Male', 'Female', 'Others'])
    
    pc3 = px.pie(diversity,
                 title='Attrition',
                 values='Attrition',
                 names='Gender')
    
    col1, col2, col3 = st.columns(3)
    col1.plotly_chart(pc1, use_container_width=True)
    col2.plotly_chart(pc2, use_container_width=True)
    col3.plotly_chart(pc3, use_container_width=True)



    st.markdown("---")

    pc4 = px.pie(diversity,
                 title='Applicant',
                 values='Applicant',
                 names='Gender')
    
    col1, col2, col3 = st.columns(3)
    col2.plotly_chart(pc4, use_container_width=True)

    diversity_goal = {
        'Male': 0.6,
        'Female':0.35,
        'Others':0.05
    }
 
    #Recommendation to optimize the diversity
    def cal_candidate_needed(df):
        df = df.query(
        "Department == @department & Band == @band"
    )
        
        total_need = df['Demand'].sum() - df['Count'].sum()

        candidates_needed = {}
        for gender, percentage in diversity_goal.items():
            candidates_needed[gender]= int(total_need * percentage)

        return candidates_needed
    
    df_recomd = df.query(
        "Department == @department & Band == @band"
    )

    candidates_needed = cal_candidate_needed(df_selection)


    col1, col2, col3 = st.columns(3)
    col2.write("Recommendation:")
    for gender, count in candidates_needed.items():
        col2.write(f"Number of {gender}: {count}")



if selected == "Campus & Vendors":

    collection = db["vendors"]

    data = collection.find()
    df = pd.DataFrame(data)
    df = df.drop("_id", axis=1)


    #-----Sidebar----
    st.sidebar.header("Select the filter:")

    department = st.sidebar.multiselect(
        "Select the Department:",
        options=df["Department"].unique(),
        default=df["Department"].unique()
    )

    band = st.sidebar.multiselect(
        "Select the Band:",
        options=df["Band"].unique(),
        default=df["Band"].unique()
    )

    vendor = st.sidebar.multiselect(
        "Select the Campus & Vendors:",
        options=df["VC"].unique(),
        default=df["VC"].unique()
    )


    df_selection = df.query(
        "Department == @department & Band == @band & VC == @vendor"
    )


    st.title("Campus & Vendor Overview")
    st.markdown("##")


    #---bar Chart
    diversity = df_selection
    bc1 = px.bar(
        diversity,
        x='VC',
        y='Applicant',
        title='Applicant',
        color='VC'
    )

    
    diversity = df_selection
    bc2 = px.bar(diversity,
                 title='Hired',
                 y='hired',
                 x='VC',
                 color='VC')
    
    bc1.update_layout(showlegend=False)
    bc2.update_layout(showlegend=False)
    
    col1, col2 = st.columns(2)
    col1.plotly_chart(bc1, use_container_width=True)
    col2.plotly_chart(bc2, use_container_width=True)


    metrics_df = df_selection.sort_values(by="metric", ascending=True)
    #st.dataframe(metrics_df)


    def display_vc(metrics_df):
        vc_list = metrics_df["VC"].unique()

        for vc in vc_list:
            st.write("Campus/Vendor:", vc)

            #filter dataframe for current vc
            vc_df = metrics_df[metrics_df["VC"] == vc]

            # Compute gender diversity for Applicant and hired columns
            applicant_gender_diversity = vc_df.groupby("Gender")["Applicant"].sum()
            hired_gender_diversity = vc_df.groupby("Gender")["hired"].sum()

            # Create a list of labels and values for the pie chart
            applicant_labels = applicant_gender_diversity.index
            applicant_values = applicant_gender_diversity.values
            hired_labels = hired_gender_diversity.index
            hired_values = hired_gender_diversity.values

            #---pie chart
            fig1 = px.pie(
                 title='Applicant Diversity',
                 values=applicant_values,
                 names=applicant_labels)
            
            fig2 = px.pie(
                 title='Hired Diversity',
                 values=hired_values,
                 names=hired_labels)
            
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig1, use_container_width=True)
            col2.plotly_chart(fig2, use_container_width=True)
            st.write("----")   


    #call function to display vendor diversity
    display_vc(metrics_df)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)



      
            



    











    



    














