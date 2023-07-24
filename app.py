# using schedule to send posts with fast api

# from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
# import os
# import requests
# import time
# import json
# import uvicorn
# from dotenv import load_dotenv
# import schedule
# import sys

# load_dotenv()  # Load environment variables from .env file

# app = FastAPI()

# # Variable to track if all posts are published
# all_posts_published = False

# @app.get("/post_photos")
# async def post_photos(background_tasks: BackgroundTasks,n: int = Query(4, gt=0)):
#     if all_posts_published:
#         raise HTTPException(status_code=400, detail="posts are being published")
#     background_tasks.add_task(schedule_photo_posts,n)
#     return {"message": "Photos will be posted to Facebook with descriptions."}

# def schedule_photo_posts(n: int ):
#     # Schedule the posting of photos every two hours
#     schedule.every(n).hours.do(post_next_photo)

#     # Run the scheduled tasks continuously
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# def post_next_photo():
#     # Path to the folder containing the photos
#     photos_folder = os.getenv("PHOTOS_FOLDER")

#     # Path to the file containing descriptions
#     descriptions_file = os.getenv("JSON_FILE")

#     # Facebook access token
#     access_token = os.getenv("ACCESS_TOKEN")

#     # Facebook page ID
#     page_id = os.getenv("PAGE_ID")

#     # Read the descriptions from the file
#     with open(descriptions_file, "r") as f:
#         descriptions = json.load(f)

#     # Make sure there are descriptions available
#     if not descriptions:
#         print("Error: No descriptions available.")
#         return

#     # Get the index of the last posted photo
#     last_posted_index = get_last_posted_index()
    
#     next_index = last_posted_index + 1
#     # Check if all descriptions have been posted
#     if last_posted_index == len(descriptions) - 1:
#         print("All Posts have been posted.")
#         # Set the flag to indicate that all posts are published
#         # Reset the index file to 0
        
#         update_last_posted_index(-1)
#         sys.exit()
#         return

#     # Determine the next description to post
#     description = descriptions[next_index]

#     # Check if the photo path exists
#     photo_path = os.path.join(photos_folder, description["path"])
#     if not os.path.exists(photo_path):
#         print(f"Error: Photo '{description['path']}' does not exist.")
#         return
    
#     global all_posts_published
#     all_posts_published = True
    
#     # Post the photo to Facebook using the access token and the description
#     with open(photo_path, "rb") as photo:
#         response = requests.post(
#             f"https://graph.facebook.com/{page_id}/photos",
#             params={"access_token": access_token, "caption": description["description"]},
#             files={"source": photo}
#         )

#     # Optional: Print the response from the Facebook API
#     print(response.json())

#     # Update the last posted index
#     update_last_posted_index(next_index)

# def get_last_posted_index():
#     index_file = "last_posted_index.txt"

#     if not os.path.exists(index_file):
#         # If the index file doesn't exist, initialize it with 0
#         update_last_posted_index(-1)
#         return -1

#     with open(index_file, "r") as f:
#         try:
#             index = int(f.read())
#             return index
#         except ValueError:
#             # If the index file contains invalid data, reset it to 0
#             update_last_posted_index(-1)
#             return -1

# def update_last_posted_index(index):
#     index_file = "last_posted_index.txt"

#     with open(index_file, "w") as f:
#         f.write(str(index))

# if __name__ == "__main__":
#     uvicorn.run(app, port=8000)


# with flask

from flask import Flask, request, jsonify, abort
from flask_background import BackgroundScheduler
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Variable to track if all posts are published
all_posts_published = False

@app.route("/post_photos", methods=["GET"])
def post_photos():
    if all_posts_published:
        abort(400, "Posts are being published")
    
    n = int(request.args.get("n", default=1))
    scheduler.add_job(schedule_photo_posts, 'interval', minutes=n, args=(n,))
    scheduler.start()
    
    return jsonify({"message": "Photos will be posted to Facebook with descriptions."})

def schedule_photo_posts(n):
    # Schedule the posting of photos every two hours
    post_job = scheduler.add_job(post_next_photo, 'interval', minutes=1, args=(n,))

def post_next_photo(n):
    # Path to the folder containing the photos
    photos_folder = os.getenv("PHOTOS_FOLDER")

    # Path to the file containing descriptions
    descriptions_file = os.getenv("JSON_FILE")

    # Facebook access token
    access_token = os.getenv("ACCESS_TOKEN")

    # Facebook page ID
    page_id = os.getenv("PAGE_ID")

    # Read the descriptions from the file
    with open(descriptions_file, "r") as f:
        descriptions = json.load(f)

    # Make sure there are descriptions available
    if not descriptions:
        print("Error: No descriptions available.")
        return

    # Get the index of the last posted photo
    last_posted_index = get_last_posted_index()
    
    next_index = last_posted_index + 1
    # Check if all descriptions have been posted
    if last_posted_index == len(descriptions) - 1:
        print("All Posts have been posted.")
        # Set the flag to indicate that all posts are published
        # Reset the index file to 0
        
        update_last_posted_index(-1)
        scheduler.remove_all_jobs()
        return

    # Determine the next description to post
    description = descriptions[next_index]

    # Check if the photo path exists
    photo_path = os.path.join(photos_folder, description["path"])
    if not os.path.exists(photo_path):
        print(f"Error: Photo '{description['path']}' does not exist.")
        return
    
    global all_posts_published
    all_posts_published = True
    
    # Post the photo to Facebook using the access token and the description
    with open(photo_path, "rb") as photo:
        response = requests.post(
            f"https://graph.facebook.com/{page_id}/photos",
            params={"access_token": access_token, "caption": description["description"]},
            files={"source": photo}
        )

    # Optional: Print the response from the Facebook API
    print(response.json())

    # Update the last posted index
    update_last_posted_index(next_index)

def get_last_posted_index():
    index_file = "last_posted_index.txt"

    if not os.path.exists(index_file):
        # If the index file doesn't exist, initialize it with 0
        update_last_posted_index(-1)
        return -1

    with open(index_file, "r") as f:
        try:
            index = int(f.read())
            return index
        except ValueError:
            # If the index file contains invalid data, reset it to 0
            update_last_posted_index(-1)
            return -1

def update_last_posted_index(index):
    index_file = "last_posted_index.txt"

    with open(index_file, "w") as f:
        f.write(str(index))

if __name__ == "__main__":
    app.run()

