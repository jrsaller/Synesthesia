import sys
import spotipy
import spotipy.util as util
import urllib.request
import tempfile

def askForToken(username):
    #authenticates the user via browser
    return util.prompt_for_user_token(username,'user-library-read',client_id='84c964082d8b47679258cc9f935b26c3',client_secret='93d1847f263f4b4880b27c15129e713c',redirect_uri='http://localhost:8888/callback')

def searchForTrackAndAlbumURI(sp,query):
    selection = -1
    i=0
    while ( selection == -1 ):
        results = sp.search(q=query,type='track',offset=i)
        #print(results['tracks']['items'])
        for track in results['tracks']['items']:
            print(i,track['name']," --- ",track['artists'][0]['name'])
            i+=1
        selection = int(input("What song would you like to select? [0-9,-1 to keep looking]").strip())
    return results['tracks']['items'][selection%10]['uri'],results['tracks']['items'][selection%10]['album']['images'][0]['url']
    
def main():
    if len(sys.argv) > 1:
        #get username from command line argument
        username = sys.argv[1]
    else:
        print("Usage %s username" % (sys.argv[0]))
        sys.exit()

    token = askForToken(username)

    if token:
        #create the spotify wrapper object
        sp = spotipy.Spotify(auth=token)
        search = input("Enter the song you would like to search for: ").strip()
        track_uri,album_url = searchForTrackAndAlbumURI(sp,search)
        #print(album_url)
        urllib.request.urlretrieve(album_url,"./OneDrive/Documents/Dixie State Spring 2020/SeniorProject/albumcover.jpeg")
        analysis =sp.audio_analysis(track_uri) 
        #print(analysis.keys())
        for key in analysis:
            print(key,len(analysis[key]))
        
    
    
    
    
    
    
    
    
    
    else:
        print("Can't get token for",username)

if __name__ == "__main__":
    main()