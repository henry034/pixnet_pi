from gtts import gTTS
lang='zh-tw'
tts = gTTS('歡迎光臨金峰魯肉飯', lang=lang, lang_check=False)
tts.save('./audio/welcome.mp3')
