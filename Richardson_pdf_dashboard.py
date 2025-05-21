import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import base64


# --- S3 Config ---
BUCKET_NAME = "sitelevel-reports"
S3_KEY = "scoreboard/richardson/latest.pdf"

# --- Use AWS credentials from local config (~/.aws/credentials) ---
s3 = boto3.client("s3", region_name="us-east-1")

# --- Hide all Streamlit UI + force fullscreen layout ---
st.set_page_config(page_title="", layout="wide")

st.markdown(
    """
    <style>
        html, body, .block-container {
            padding: 0;
            margin: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }

        #MainMenu, header, footer {
            display: none;
        }

        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Fetch PDF from S3 ---
try:
    response = s3.get_object(Bucket=BUCKET_NAME, Key=S3_KEY)
    pdf_data = response["Body"].read()
    base64_pdf = base64.b64encode(pdf_data).decode("utf-8")

    # --- Render fullscreen PDF ---
    pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}"></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

except s3.exceptions.NoSuchKey:
    st.error("❌ No PDF report found.")
except NoCredentialsError:
    st.error("❌ AWS credentials not found.")
except ClientError as e:
    st.error(f"❌ AWS error: {e.response['Error']['Message']}")
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")

