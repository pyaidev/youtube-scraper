import os
import json
import googleapiclient.discovery
import re
from pprint import pprint

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "Devoloper_key"


MAX_COMMENT_RESULTS = 5000
COMMENT_CACHE = {}  # Кэш результатов запросов к YouTube API


YOUTUBE = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)


def req_comment_threads(video_id, page_token=None):
    if video_id in COMMENT_CACHE:
        response = COMMENT_CACHE[video_id]
    else:
        request = YOUTUBE.commentThreads().list(
            part="snippet,replies",
            maxResults=MAX_COMMENT_RESULTS,
            textFormat="plainText",
            videoId=video_id,
            pageToken=page_token,
        )
        try:
            response = request.execute()
            COMMENT_CACHE[video_id] = response
        except Exception as e:
            print(f"An error occurred while fetching comments for video {video_id}: {str(e)}")
            response = {}
    pprint(response)
    return response

def find_comments_in_file(video_link, comments_to_find):
    found_comment_links = []
    video_id = re.search(r'v=([A-Za-z0-9_-]+)', video_link).group(1)
    response = req_comment_threads(video_id)

    for item in response.get("items", []):
        comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comment_text = comment_text.replace('\n', ' ')
        for comment_to_find in comments_to_find:
            if re.search(comment_to_find, comment_text, re.IGNORECASE | re.UNICODE):  # Use re.UNICODE for Unicode support
                comment_link = f"https://www.youtube.com/watch?v={item['snippet']['videoId']}&lc={item['snippet']['topLevelComment']['id']}"
                found_comment_links.append(comment_link)

        if 'replies' in item:
            comment_replies = item['replies']['comments']
            for reply in comment_replies:
                reply_text = reply['snippet']['textDisplay']
                reply_text = reply_text.replace('\n', ' ')
                for comment_to_find in comments_to_find:
                    if re.search(comment_to_find, reply_text, re.IGNORECASE | re.UNICODE):  # Use re.UNICODE for Unicode support
                        reply_link = f"https://www.youtube.com/watch?v={item['snippet']['videoId']}&lc={reply['id']}"
                        found_comment_links.append(reply_link)

    return found_comment_links

def main():
    comments_to_find = []
    with open('comments_to_find.txt', 'r') as comments_file:
        comments_to_find = [line.strip() for line in comments_file]

    with open('video_links.txt', 'r') as links_file:
        video_links = [line.strip() for line in links_file]

    YOUTUBE = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    for video_link in video_links:
        found_comment_links = find_comments_in_file(video_link, comments_to_find)
        if found_comment_links:
            with open('found_comment_links.txt', 'a') as found_file:
                for link in found_comment_links:
                    found_file.write(link + '\n')
            print(f'Найдены комментарии для видео {video_link}. Ссылки на комментарии сохранены в файле found_comment_links.txt')
        else:
            print(f'Комментарии для видео {video_link} не найдены')

if __name__ == "__main__":
    main()
