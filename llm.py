import openai


class YouTubeAssistant:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_title(self):
        response = self._query_openai(
            user_message=f"Generate a short cats/pets youtube video title with just 2 words. dont use these words: hilarious, entertain, funny, play words. always include some tags after the title. #shorts #catlovers #funnycats",
            max_tokens=25,
        )
        return response["choices"][0]["message"]["content"]

    def generate_description(self, desc_param):
        response = self._query_openai(
            user_message=f"Generate a meaningful, attractive youtube video description, include many tags below the description, here is the short video description: {desc_param}",
            max_tokens=250,
        )
        return response["choices"][0]["message"]["content"]

    def generate_tags(self, video_param, niche):
        response = self._query_openai(
            user_message=f"Generate 15 popular cool tags for my video {niche}, divide by comma, example: #football, #sport, here is short description: {video_param}",
            max_tokens=250,
        )
        return response["choices"][0]["message"]["content"]

    def _query_openai(self, user_message, max_tokens):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced Youtuber assistant.",
                },
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
        )
