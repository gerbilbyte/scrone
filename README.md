# Scrone

Author: gerbil.
Version: 0.1 
Date: 15/05/2024

Twenty plus years after initial discussion, Scrone has been made!
This is a simple python3 script created to crawl and evaluate websites.

This is a tool used to aid myself and fellow security folk.
DO NOT USE THIS TOOL ON WEBSITE YOU DON'T OWN OR DON'T HAVE PERMISSION 
TO SCAN/PENTEST. DOING SO CAN BE ILLEGAL, CAN GET YOU IN SERIOUS TROUBLE
AND SENT TO BED WITHOUT ANY SUPPER.
Also, as I'm in capital writing mood: USE THIS PROGRAM AT YOUR OWN RISK! 
I WILL NOT BE ACCOUNTABLE FOR ANY DAMAGE OR LOSS OF DATA CAUSED MY USING
THIS TOOL!

Features included are:

* Deep crawl: As well as crawling href tags this will also crawl other
  tags found on the website, such as js scripts and their sub folders.
  All found and ignored (out of domain) locations are stored in respective
  files.
  NOTE: This is a bit buggy, but not dangerous, and is being worked on.

* "Index of" search: Pages with directory listing enabled will be found
  and location recorded.
 
* WordPress User Enumeration: An attempt will be used to enumerate WordPress
  users of the site.
 
* WordPress Password bruteforcer: Attempts to crack passwords using a given 
  wordfile.
  NOTE: This is currently slow, and will only attempt one retry when the
  'rate limit' has been hit. Also, xmlrpc needs to be enabled for attack to work. 
 
This is completely PoC stuff, so use at your own risk.
Also, the features in this program are all basic where the script assumes
certain features (such as xml.rpc.php) are in certain places etc. These 
will eventually be automated.

TODO/Future features will include:

* Silent/verbose options.
* Multithreading to speed up crawling.
* Timestamped output files with URL included.
* Include an "ignore" so that certian files will be ignored. Currently, 
  "image files" (.jpg, .jpeg, .png, .gif, .bmp) are ignored but hardcoded - 
  this will soon be an optional feature.
* Alternative password cracking method - currently I have only implemented
  the 'xmlrpc' method. It would be good to include another routine such as 
  using the actuall login page. but that would be well slower.
* Check if xmlrpc is enabled.
* Audit xmlrpc allowed methods.
* WordPress Plugin and Themes enumeration
* ...and WordPress version number checks
* And other things not associated with WordPress! Other CMSs  
* ...and other stuff that I can't think of right now!

Also a better help page will be included, but the tool is more or less self descriptive with its help screen.

Have fun and enjoy yourselves. :O)

# -gerbil 
