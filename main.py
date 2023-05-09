import googleapiclient.discovery
import datetime


def scrapping():
    API_KEY = "your-api-key"
    SEARCH_TERM = input("Введите поисковый запрос: ")
    VIEW_COUNT_MIN = 1  # Введите минимальное количество просмотров
    VIEW_COUNT_MAX = 10000000000  # Введите максимальное количество просмотров
    COMMENT_COUNT_MIN = 1  # Введите минимальное количество комментариев
    COMMENT_COUNT_MAX = 10000000000  # Введите максимальное количество комментариев

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

    saved_videos_file = "videos.txt"

    saved_videos = set()
    try:
        with open(saved_videos_file, "r", encoding="utf-8") as f:
            saved_videos = set(f.read().splitlines())
    except FileNotFoundError:
        pass

    search_params = {
        "q": SEARCH_TERM,
        "type": "video",
        "part": "id,snippet",
        "maxResults": 500000000,
        "order": "viewCount",
    }

    from_date = "2020-11-11" # Введите дату загрузки с (гггг-мм-дд)
    to_date = "2023-01-01" # Введите дату загрузки до (гггг-мм-дд)

    if from_date and to_date:
        search_params["publishedAfter"] = from_date + "T00:00:00Z"
        search_params["publishedBefore"] = to_date + "T23:59:59Z"

    search_response = youtube.search().list(**search_params).execute()

    videos = []
    for search_result in search_response.get("items", []):
        video_id = search_result["id"]["videoId"]
        video_response = youtube.videos().list(id=video_id, part="id,snippet,statistics").execute()
        video_data = video_response["items"][0]
        view_count = int(video_data["statistics"]["viewCount"])
        comment_count = int(video_data["statistics"].get("commentCount", "0"))
        if view_count >= VIEW_COUNT_MIN and view_count <= VIEW_COUNT_MAX and \
                comment_count >= COMMENT_COUNT_MIN and comment_count <= COMMENT_COUNT_MAX:
            videos.append({
                "title": video_data["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "view_count": view_count,
                "comment_count": comment_count,
            })
            saved_videos.add(f"Ссылка: https://www.youtube.com/watch?v={video_id}")

    with open(saved_videos_file, "w", encoding="utf-8") as f:
        f.write("\n".join(saved_videos))


if __name__ == "__main__":
    scrapping()
