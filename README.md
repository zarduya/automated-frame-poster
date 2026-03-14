# Automated Social Media Frame Poster

A Python automation bot that uploads image frames to Cloudinary and posts them automatically to X (Twitter) at scheduled intervals.

## Features
- Fetches images from Cloudinary storage
- Automatically posts frames to X (Twitter)
- Tracks previously posted frames using a state file
- Posts images in controlled batches to avoid API rate limits
- Runs continuously with scheduled delays between batches
- Designed to handle large image collections (10,000+ frames)

## Technologies Used
- Python
- Tweepy (Twitter API)
- Cloudinary API
- Requests
- Railway (cloud deployment)

## How It Works
1. Image frames are uploaded to Cloudinary storage.
2. The bot retrieves frame URLs from the Cloudinary folder.
3. Frames are sorted sequentially to maintain correct order.
4. The bot posts a batch of frames to X (Twitter).
5. Progress is saved in a `state.json` file to avoid duplicate posts.
6. The bot waits for a scheduled interval before posting the next batch.

## System Architecture

The project consists of two main components:

### 1. Frame Upload Pipeline
A Python script uploads image frames from a local directory to Cloudinary.

Process:
- Reads images from the local `frames/` directory
- Uploads them to a Cloudinary folder
- Stores uploaded URLs in a progress file
- Prevents duplicate uploads using a mapping file

### 2. Automated Posting Bot
A Python automation bot retrieves stored frames and posts them to X (Twitter).

Workflow:
1. Fetch frame URLs from Cloudinary
2. Track posting progress using a state file
3. Post frames in batches
4. Wait between batches to avoid API rate limits
5. Continue until all frames are posted

### Data Flow
Local Images → Cloudinary Storage → Python Bot → X (Twitter)

## Purpose
This project was built as an experiment in automation, cloud storage integration, and scheduled content posting using Python.

## Security
API keys and credentials are **not stored in the repository**.  
All sensitive values (Twitter API keys, Cloudinary credentials) are loaded securely using environment variables.

## Deployment
The automation bot was deployed on Railway to run continuously in a cloud environment.
