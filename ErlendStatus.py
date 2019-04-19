# -*- coding: utf-8 -*-

import atexit
import certifi

from time                       import sleep
from bs4                        import BeautifulSoup
from urllib3                    import PoolManager
from datetime                   import date
from googleapiclient.discovery  import build
from google_auth_oauthlib.flow  import InstalledAppFlow

url = "https://www.youtube.com/results?search_query=meme&sp=EgIIAQ%253D%253D"
r = PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

api_service_name = "youtube"                                                # ←
api_version = "v3"                                                          #  |
DEVELOPER_KEY = "AIzaSyBn1PaUP_iz8z9Ku3nw3jRTqTOy_Lj1V9w"                   #  |
CLIENT_SECRET = "client_secret.json"                                        #  |
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']              #  |→   YOUTUBE API SHIT
                                                                            #  |
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)     #  |
credentials = flow.run_console()                                                  #  |
youtube = build(api_service_name, api_version, credentials=credentials)         # ←

knownVideos = []
begin = date(2011, 10, 7)


def exit_handler():                                                 # ←
    print("[!]EXIT\n Commented videos:", knownVideos)               #  |→   ON EXIT
atexit.register(exit_handler)                                       # ←


# GETS NEW VIDEO BY PARSING HTML... This was a pain to make
def getNewVideo():
    html = r.request('GET', url)
    soup = BeautifulSoup(html.data.decode('utf-8'), 'html.parser')
    for a in soup.find_all('a'):
        if a.get('href').split('=')[0] == '/watch?v':
            return a.get('href').split('=')[1]


# CREATES A NEW COMMENT WITH YOUTUBE API
def insertComment(videoId, text):
    result = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": videoId,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": text
                    }
                }
            }
        }
    ).execute()

# QUERIES YOUTUBE API TO GET SUBSCRIBER COUNT
def getSubs(channelId):
    result = youtube.channels().list(
        part="statistics",
        id=channelId
    ).execute()
    return result['items'][0]['statistics']['subscriberCount']

# CREATES THE STATUS COMMENT
def getComment():
    erlendSubs = int(getSubs("UCkDCaahQdyHaSHUk2RM6ifQ"))
    pewDiePieSubs = int(getSubs("UC-lHJZR3Gqxm24_Vd_AJ5Yw"))
    tSeriesSubs = int(getSubs("UCq-Fj5jknLsUf-MWSy4_brA"))


    daysActive = int(str(date.today() - begin).split(' ')[0])
    deltaPewds = daysActive*(pewDiePieSubs/erlendSubs)
    deltaTSeries = daysActive*(tSeriesSubs/erlendSubs)

    comment = (
            "----------------STATUS----------------\n"
            f"Du er bare {pewDiePieSubs-erlendSubs} subs unna PewDiePie\n"
            f"Du er bare {tSeriesSubs - erlendSubs} subs unna T-Series\n"
            f"Bare {deltaPewds} dager til du tar igjen PewDiePie\n"
            f"Bare {deltaTSeries} dager til du tar igjen T-Series\n"
    )

    return comment


# MAIN FUNCTION
def main():
    # PewDiePie channel ID:  UC-lHJZR3Gqxm24_Vd_AJ5Yw               ←
    # T-Series channel ID:  UCq-Fj5jknLsUf-MWSy4_brA                 |→ CHANNEL IDs
    # Erlend Gurvin channel ID:  UCkDCaahQdyHaSHUk2RM6ifQ           ←

    cycle = 0
    video = getNewVideo()                                                           # GETS NEWEST VIDEO
    knownVideos.append(video)                                                       # ADDS IT TO LIST OF KNOWN VIDEOS
    youtube.videos().rate(rating='like', id=video).execute()                        # LIKES VIDEO
    print(getComment())                                                             # PRINTS STATUS COMMENT
    insertComment(video, getComment())                                              # POSTS COMMENT ON NEWEST VIDEO

    # MAIN LOOP
    while True:
        cycle += 1                                                                  # JUST A COUNTER FOR CONVINIENCE
        print("Cycle:", cycle)                                                      # ↑

        # newVideoID = getNewVideo()                                                     #  ←
        # print(newVideoID)                                                              #   |
        # if newVideoID != video:                                                        #   |
        #     if newVideoID not in knownVideos:                                          #   |
        #         # WHEN NEW VIDEO FOUND:                                                #    →  LIKES AND COMMENTS ON NEW VIDEO BY CHECKING IF IT IS IN KNOWN VIDEOS LIST
        #         knownVideos.append(newVideoID)                                         #   |
        #         youtube.videos().rate(rating='like', id=newVideoID).execute()          #   |
        #         print(doneVideos)                                                      #   |
        #         print("New Video:", newVideoID, "\n\n")                                #  ←

        sleep(10)                                                                       # PAUSES TO NOT OVERWHELM YOUTUBE'S API


# RUNS CODE IF THIS FILE IS THE SOURCE FILE
# WILL NOT RUN CODE IF IT'S IMPORTED BY ANOTHER PYTHON FILE
if __name__ == "__main__":
    main()