# Automated Social Media Frame Poster

A Python automation bot that posts image frames to X (Twitter) at scheduled intervals.

## Features
- Fetches images from Cloudinary storage
- Posts frames automatically to X (Twitter)
- Keeps track of previously posted frames using a state file
- Posts in batches with rate-limit protection
- Runs continuously using a timed loop

## Technologies Used
- Python
- Tweepy (Twitter API)
- Cloudinary API
- Requests
- Railway deployment

## How it Works
1. Fetches frame images from Cloudinary
2. Sorts frames sequentially
3. Posts a batch of frames to X
4. Saves progress using `state.json`
5. Waits 6 hours before posting the next batch

## Purpose
This project was built as an experiment in automation, cloud storage integration, and scheduled content posting.

## Note
API keys and credentials are stored as environment variables for security.
