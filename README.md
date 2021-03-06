# Sickbeard Episode Cleaner

A post processing script for Sickbeard that allows you to set the number of episodes of a show that you would like to keep. Useful for shows that air daily.

The script sorts the episodes you have for a show by the season and episode number, and then deletes the oldest episodes past the threshold you set.

## How to use

1. Clone the repository
``` git clone https://github.com/spoatacus/sickbeard-episode-cleaner.git ```
2. Change owner to your Sickbeard user
``` chown -R sickbeard.sickbeard sickbeard-episode-cleaner ```
3. Make main.py executable by your Sickbeard user
``` chmod ug+x sickbeard-episode-cleaner/main.py ```
4. Configure the script. See section below for details.
5. Configure Sickbeard to use the script
    - Stop Sickbeard
    - Edit Sickbeard's config.ini
    - Add the full path of sickbeard-episode-cleaner/main.py to the extra_scripts setting (under [General])
    - Start Sickbeard

## Configuration

Configuration is pretty straight forward as this sample config file shows. The keys under shows are the tvdb id's for the shows you want to clean.

There is a sample config included. Just move it to config.json.
``` mv sickbeard-episode-cleaner/config.json.sample sickbeard-episode-cleaner/config.json ```

```json
{
    "server": {
    	"hostname": "",
		"port": 8081,
		"web_root": "",
		"api_key": ""
	},
	"shows": {
        // The Colbert Report
		"79274": {					// tvdb id
			"keep_episodes": 10		// number of episodes to keep
		},
        // The Daily Show
		"71256": {					// tvdb id
			"keep_episodes": 10		// number of episodes to keep
		},
        // Conan
		"194751": {					// tvdb id
			"keep_episodes": 10		// number of episodes to keep
		}
	}
}
```
