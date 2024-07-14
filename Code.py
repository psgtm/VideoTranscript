import streamlit as st
import pandas as pd

# Function to parse uploaded file
def parse_file(file):
    if file is None:
        return None
    elif file.name.endswith('.csv'):
        return pd.read_csv(file), 'csv'
    elif file.name.endswith('.json'):
        return pd.read_json(file), 'json'
    else:
        st.error("Unsupported file format. Please upload a CSV or JSON file.")
        return None, None

# Function to convert time format (HH:MM:SS) to seconds
def convert_to_seconds(time_str):
    try:
        parts = time_str.split(':')
        seconds = float(parts[-1])
        minutes = int(parts[-2]) * 60
        hours = int(parts[-3]) * 3600 if len(parts) == 3 else 0
        return hours + minutes + seconds
    except ValueError:
        st.error(f"Invalid time format: {time_str}")
        return 0

# Function to create the transcript panel
def create_transcript_panel(transcript_df):
    st.write("Transcription Results:")
    st.dataframe(transcript_df)

# Function to create the video panel with timestamp buttons and text display
def create_video_panel(video_path, transcript_df):
    st.write("Trial Video:")
    
    video_start_time = st.session_state.get('video_start_time', 0)
    st.video(video_path, format="video/mp4", start_time=video_start_time)

    st.write("Click timestamps to jump:")
    start_time_col = 'Start Time'
    for i, row in transcript_df.iterrows():
        try:
            start_time = row[start_time_col]
            seconds = convert_to_seconds(start_time)
            button_key = f"button_{i}"  # Generate a unique key for each button
            if st.button(f"{start_time} - {row['Text']}", key=button_key):
                st.session_state.video_start_time = seconds
                st.experimental_rerun()  # Rerun the app to update the video start time
        except KeyError as e:
            st.error(f"KeyError: {e}")
            st.write(row)

# Main function to orchestrate the application flow
def main():
    st.title("Transcription and Video Sync")

    # File upload widgets
    transcription_file = st.file_uploader("Upload Transcription Results (CSV/JSON)", type=['csv', 'json'])
    video_file = st.file_uploader("Upload the Trial Video (MP4)", type=['mp4'])

    if transcription_file and video_file:
        # Parse transcription file
        transcript_df, file_type = parse_file(transcription_file)
        if transcript_df is not None and file_type == 'csv':
            create_transcript_panel(transcript_df)
        elif transcript_df is not None and file_type == 'json':
            st.warning("JSON format not supported for transcript display. Please upload a CSV file.")
        else:
            st.warning("Please upload a valid transcription file (CSV/JSON).")

        # Handle video file upload
        if file_type == 'csv' and video_file is not None:
            # Save the video file temporarily
            video_path = f"./{video_file.name}"
            with open(video_path, "wb") as f:
                f.write(video_file.getbuffer())
            
            create_video_panel(video_path, transcript_df)
        elif file_type is None:
            st.warning("Please upload both transcription and video files to sync.")
        
        # Handle missing video file
        if not video_file:
            st.write("Upload a video file (MP4) to view.")

    elif transcription_file:
        st.write("Upload a video file (MP4) to view.")
    elif video_file:
        st.write("Upload a transcription file (CSV/JSON) to view.")

# Run the main function
if __name__ == "__main__":
    main()