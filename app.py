import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

# Load the environment variables from .env file
load_dotenv()

# Configure Google API Key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Summarizer prompt for the Gemini model
prompt = """You are a YouTube Video Summarizer. You will take the transcript text and
            summarize the entire video, providing the clear summary  in a important points ."""

# Function to extract transcript from YouTube video
def extract_transcript(youtube_video_url):
    try:
        # Check if URL is in 'youtu.be' format and extract video ID
        if "youtu.be" in youtube_video_url:
            video_id = youtube_video_url.split("/")[-1]
        # Check if URL is in 'youtube.com' format and extract video ID
        elif "youtube.com" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]  # Ensure video ID is properly split
        else:
            raise ValueError("Invalid YouTube URL format.")
        
        # Fetch the transcript of the video
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id=video_id)
        
        # Combine all the transcript texts into a single string
        transcript = " ".join([item["text"] for item in transcript_data])
        
        return transcript
    
    except TranscriptsDisabled:
        # Handle case when transcripts are disabled for the video
        st.error("Subtitles are disabled for this video. Unable to fetch the transcript.")
        return None
    except ValueError as ve:
        # Handle invalid URL format
        st.error(str(ve))
        return None
    except Exception as e:
        # Handle other unexpected errors
        st.error(f"Error fetching transcript: {e}")
        return None

# Function to generate summary using Google's Gemini model
def generate_summary(transcript_text, prompt):
    try:
        # Initialize the generative model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-002")
        
        # Generate content by combining the prompt and the transcript
        response = model.generate_content(prompt + transcript_text)
        
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit UI
st.title("YouTube Video Transcript Summarizer")

# Text input box to get YouTube video URL
youtube_link = st.text_input("Enter the YouTube Video Link:")

# Check if the URL is valid and display the thumbnail
if youtube_link:
    try:
        # Extract the video ID correctly from both youtube.com and youtu.be URLs
        if "youtube.com" in youtube_link:
            video_id = youtube_link.split("v=")[1].split("&")[0]  # Extract video ID after 'v='
        elif "youtu.be" in youtube_link:
            video_id = youtube_link.split("/")[-1]  # Extract video ID after the last '/'
        else:
            raise ValueError("Invalid YouTube URL format.")
        
        # Display the video thumbnail
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        st.success(f"Video ID: {video_id}")  # For debugging purposes (you can remove this later)
        
    except IndexError:
        st.error("Invalid YouTube URL format. Please provide a valid link.")
    except ValueError as e:
        st.error(str(e))

# Button to trigger transcript extraction and summary generation
if st.button("Get the Summary"):
    if youtube_link:
        # Extract transcript from the provided YouTube link
        transcript = extract_transcript(youtube_link)

        if transcript:
            # Generate summary based on the transcript
            summary = generate_summary(transcript, prompt)
            
            if summary:
                st.markdown("### Video Summary:")
                st.write(summary)
            else:
                st.warning("Failed to generate summary.")
        else:
            st.warning("Failed to extract transcript.")
