<?php
$url = isset($_GET['url']) ? htmlspecialchars($_GET['url']) : null;
?>
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>MediaFire</title>
</head>
<body>
<div id="player"></div>
<script src="https://content.jwplatform.com/libraries/wr6i4gal.js"></script>
<script>
jwplayer("player").setup({
/**** ADVERTISING SECTION STARTS HERE ****/
        advertising: {
            client: "vast",
            schedule: {
                "myAds": {
                    "offset": "pre",
                    "tag": "https://syndication.exosrv.com/splash.php?idzone=2930468"
                }
            }
        },
        /**** ADVERTISING SECTION ENDS HERE ****/
  playlist: [{
    "sources": <?php require 'mediafire.php';?>
  }],
  allowfullscreen: true,
  width: '100%',
  aspectratio: '16:9',
});
</script>
</body>
</html>
