# Synesthesia
Image creation based on musical data pulled from Spotify!

## Spotify Integration
This program authenticates a user with Spotify's API, then uses Spotify's Audio Analysis information for a track to get loudness of a section (i.e. Chorus, Verse, Bridge), and the loudness of all of its underlying segments.

The program also downloads the album cover of a given song from Spotify and uses that image to create 5 "Spectrum Pillars" which are used in creating the spectrum.


## Usage
As of right now, for the program to work you need the Secret Key for the project. This currently is not included in the project, but will someday work as part of a Web App.

``` python3 main.py [username] ```

On first run, the program will open a browser to authenticate the username given. After authentication, the browser will lead to another website, which then is copied back into the terminal, and the program is now authenticated with that specific username.
