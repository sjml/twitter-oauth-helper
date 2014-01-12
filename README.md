twitter-oauth-helper
====================

Gets OAuth tokens for a specific Twitter application from the command line. Run the program, then visit `http://localhost:8000` in your web browser and go from there. 

I use it for when I'm doing some automated twitter stuff and want to test it on a non-publicized account before switching over to the main one. Twitter's developer site only easily lets you make login tokens for the owning account, so you have to do full-on OAuth implementation for other accounts. This is a tiny little web server that does nothing except get said tokens. 

If, in fact, there *is* an easier way to get said tokens, please open a pull request. :)
