"""
File:     dutch_speech_rate.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    I wrote down the explanation messages from our video takes and their times
    to calculate the speech rate.
"""

TEXT_1 = "we spelen het spel wow (with other words) waarin een robot een woord bedenkt en jij moet raden wat het is door ja/nee vragen te stellen. de robot geeft korte antwoorden zonder taboewoorden te gebruiken. als je het woord raadt, maakt de robot een vrolijk liedje in het engels. zo niet, mixt het liedje nederlands en engels om te helpen bij het leren. zeg 'doei', 'tot ziens' of 'stop' om te eindigen. veel plezier en vraag om hints wanneer nodig!"
num_words_1 = len(TEXT_1.split())
TIME_1 = 28  # seconds
speech_rate_1 = TIME_1 / num_words_1

TEXT_2 = "speel het leuke spel wow (with other words) waarbij de robot (host) een woord bedenkt en jij vragen stelt om het te raden. de robot zal kort antwoorden geven zonder verboden woorden te gebruiken. als je het woord raadt, maakt de robot een grappig liedje in het engels. als je stopt, zegt 'goodbye'. vraag gerust om hints in het engels of door 'hint' te zeggen. veel plezier met spelen!"
num_words_2 = len(TEXT_2.split())
TIME_2 = 26  # seconds
speech_rate_2 = TIME_2 / num_words_2

TEXT_3 = "bij het wow-spel denkt de robot aan een woord dat de speler moet raden door ja/nee-vragen te stellen. de robot kan alleen kort antwoorden zonder verboden woorden te gebruiken. na elke ronde maakt de robot een vrolijk liedje over het geraden woord. als het woord niet geraden wordt, zal het liedje een mix van nederlands en engels zijn om te helpen leren. de speler kan altijd stoppen door 'doei' of 'stop' te zeggen en wordt aangemoedigd om hints te vragen en plezier te hebben met het spel. veel speelplezier!"
num_words_3 = len(TEXT_3.split())
TIME_3 = 29  # seconds
speech_rate_3 = TIME_3 / num_words_3

average_speech_rate = (speech_rate_1 + speech_rate_2 + speech_rate_3) / 3  # = 0.35088476361070403
print("Average speech rate (seconds per word):", average_speech_rate)
