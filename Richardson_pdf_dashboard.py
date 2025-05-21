import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import pytz # For timezone handling
import streamlit.components.v1 as components
import datetime # For refreshing at a specific time

# --- S3 Config ---
BUCKET_NAME = "sitelevel-reports"
S3_KEY = "scoreboard/richardson/latest.pdf"

# Set the expiration for the presigned URL.
# Ensure this is less than or equal to your IAM role's session duration.
# For 12 hours of operation, aim for 12-13 hours.
PRESIGNED_URL_EXPIRATION = 12 * 3600 # 12 hours in seconds

# --- AWS S3 Client ---
# Use st.secrets for credentials
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_DEFAULT_REGION"]
)

# --- Streamlit Page Config ---
st.set_page_config(page_title="Site Scoreboard", layout="wide")

# --- Custom CSS for Fullscreen Display & Hiding UI ---
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

# --- Cached function to get PDF presigned URL ---
@st.cache_data(ttl=PRESIGNED_URL_EXPIRATION - 600) # Regenerate 10 minutes before the URL expires
def get_pdf_presigned_url(bucket_name, s3_key, expiration_seconds):
    """Generates a presigned URL for an S3 object."""
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key, 'ResponseContentType': 'application/pdf'},
            ExpiresIn=expiration_seconds
        )
        return url
    except s3.exceptions.NoSuchKey:
        st.error(f"❌ PDF not found in S3: s3://{bucket_name}/{s3_key}")
        return None
    except NoCredentialsError:
        st.error("❌ AWS credentials not found or configured incorrectly.")
        return None
    except ClientError as e:
        st.error(f"❌ AWS S3 client error: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        return None

# --- Main app logic ---
pdf_url = get_pdf_presigned_url(BUCKET_NAME, S3_KEY, PRESIGNED_URL_EXPIRATION)

if pdf_url:
    # Render fullscreen PDF using the presigned URL
    pdf_display = f"""
        <iframe
            src="{pdf_url}"
            width="100%"
            height="100%"
            style="position: fixed; top: 0; left: 0; bottom: 0; right: 0; border: none;"
            title="Embedded PDF"
        ></iframe>
    """
    components.html(pdf_display, height=1080, width=1920) # Use actual screen dimensions if known
else:
    # Error message will be displayed by the cached function
    st.write("Please check the error messages above.")


# --- Client-side JavaScript for daily refresh at 12:30 PM Chicago Time ---
# Calculate time until next 12:30 PM CT
chicago_tz = pytz.timezone('America/Chicago')
now = datetime.datetime.now(chicago_tz)

target_hour = 12
target_minute = 30

next_refresh_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

# If current time is past 12:30 PM, schedule for tomorrow
if now >= next_refresh_time:
    next_refresh_time += datetime.timedelta(days=1)

time_until_refresh_ms = int((next_refresh_time - now).total_seconds() * 1000)

st.markdown(
    f"""
    <script>
        const timeUntilRefresh = {time_until_refresh_ms};
        console.log("Next refresh in (ms):", timeUntilRefresh);
        setTimeout(function() {{
            location.reload();
        }}, timeUntilRefresh);
    </script>
    """,
    unsafe_allow_html=True
)

# --- Display Last Modified Date ---
try:
    meta = s3.head_object(Bucket=BUCKET_NAME, Key=S3_KEY)
    last_modified = meta['LastModified'].astimezone(chicago_tz)
    st.caption(f"Last updated: {last_modified.strftime('%Y-%m-%d %I:%M %p CT')}")
except Exception as e:
    st.caption(f"Could not retrieve last modified date: {e}")