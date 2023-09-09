import googleapiclient.discovery
import datetime
import isodate


def load_keywords(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        keywords = f.read().splitlines()
    return keywords


def save_videos_by_keyword(saved_videos_file, keyword, videos):
    with open(saved_videos_file, "a", encoding="utf-8") as f:
        f.write(f"название-{keyword}\n")
        for video in videos:
            f.write(f"{video['url']}\n")

def scrapping():
    start_time = datetime.datetime.now()
    print("Парсер начал работу")
    API_KEY = "your_api_key"
    keywords_file = "keywords.txt"  # Путь к блокноту с ключевыми словами
    VIEW_COUNT_MIN = 10   # Минимальное количество просмотров
    VIEW_COUNT_MAX = 10000000000    # Максимальное количество просмотров
    COMMENT_COUNT_MIN = 25    # Минимальное количество комментариев
    COMMENT_COUNT_MAX = 5000  # Максимальное количество комментариев

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

    saved_videos_file = "videos.txt"  # Путь к файлу, в котором будут сохраняться в результатах парсинга

    saved_videos = set()
    try:
        with open(saved_videos_file, "r", encoding="utf-8") as f:
            saved_videos = set(f.read().splitlines())
    except FileNotFoundError:
        pass

    keywords = load_keywords(keywords_file)  # Загрузить ключевые слова из блокнота

    for keyword in keywords:
        print(f"Парсим ключевое слово: {keyword}")
        search_params = {
            "q": keyword,
            "type": "video",
            "part": "id,snippet",
            "maxResults": 500000000,
            "order": "viewCount",
        }

        from_date = "2023-08-08"  # начальная дата публикации видео
        to_date = "2023-09-09"   # конечная дата публикации видео

        if from_date and to_date:
            search_params["publishedAfter"] = from_date + "T00:00:00Z"
            search_params["publishedBefore"] = to_date + "T23:59:59Z"

        search_response = youtube.search().list(**search_params).execute()

        videos = []
        for search_result in search_response.get("items", []):
            video_id = search_result["id"]["videoId"]
            video_response = youtube.videos().list(id=video_id, part="id,snippet,statistics,contentDetails").execute()
            video_data = video_response["items"][0]
            if "statistics" in video_data:
                view_count = int(video_data["statistics"].get("viewCount", "0"))
                comment_count = int(video_data["statistics"].get("commentCount", "0"))
            else:
                # Пропускаем видео, для которых отсутствует информация о статистике
                continue
            comment_count = int(video_data["statistics"].get("commentCount", "0"))

            duration = isodate.parse_duration(video_data["contentDetails"]["duration"])

            if view_count >= VIEW_COUNT_MIN and view_count <= VIEW_COUNT_MAX and \
                    comment_count >= COMMENT_COUNT_MIN and comment_count <= COMMENT_COUNT_MAX and \
                    duration.total_seconds() >= 300:  # длительность видео не менее 5 минут
                videos.append({
                    "title": video_data["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "view_count": view_count,
                    "comment_count": comment_count,
                    "duration": str(duration),
                })
                saved_videos.add(f"https://www.youtube.com/watch?v={video_id}")

        print(f"Найдено {len(videos)} видео по ключевому слову {keyword}")
        save_videos_by_keyword(saved_videos_file, keyword, videos)
    print("Парсер закончил работу")



if __name__ == "__main__":
    scrapping()

