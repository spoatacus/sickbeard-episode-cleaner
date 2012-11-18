#!/usr/bin/python
import os
import time
import json
import glob
import logging
import argparse
import urllib
from operator import itemgetter

DEBUG = False
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'episode-trimmer.log')

# configure logging
logger = logging.getLogger()
logger.setLevel( logging.DEBUG )
if DEBUG:
	lh = logging.StreamHandler()
else:
	lh = logging.FileHandler( LOG_FILE )
lh.setFormatter( logging.Formatter('%(asctime)s %(message)s') )
logger.addHandler( lh )

config = json.load(open(CONFIG_FILE, 'r'))

parser = argparse.ArgumentParser()
parser.add_argument("full_path")
parser.add_argument("original_name")
parser.add_argument("tvdbid")
parser.add_argument("season")
parser.add_argument("episode")
parser.add_argument("air_date")


# make a SB api call
def sb_request( params ):
	p = urllib.urlencode(params)
	url = "http://%s:%s%s/api/%s/?%s" % (config['server']['hostname'], config['server']['port'], config['server']['web_root'], config['server']['api_key'], p)
	return json.loads( urllib.urlopen(url).read().decode('utf-8') )


# delete files associated with an episode
def delete_episode( filename ):
	name, ext = os.path.splitext( filename )

	for f in glob.glob(name + "*"):
		logger.info( "delete file: %s" % f )
		if not DEBUG:
			os.remove( f )


def process_episode( tvdbid ):
	# get episodes
	params = {'cmd': 'show.seasons', 'tvdbid': tvdbid}
	episodes_json = sb_request(params)

	# skip 'specials'
	if '0' in episodes_json['data']:
		del episodes_json['data']['0']


	# find episodes that have been downloaded
	downloaded_episodes = []

	for season_key, season in episodes_json['data'].items():
		for episode_key, episode in season.items():
			if episode['status'] == 'Downloaded':
				downloaded_episodes.append( [int(season_key), int(episode_key)] )
	
	# sort episodes by season, episode number
	downloaded_episodes = sorted( downloaded_episodes, key=itemgetter(0,1) )
	logger.info( "%s: %s" % (tvdbid, len(downloaded_episodes)) )

	# delete oldest episodes until we are within the threshold of episodes to keep
	if len(downloaded_episodes) > config['shows'][tvdbid]['keep_episodes']:
		while len(downloaded_episodes) > config['shows'][tvdbid]['keep_episodes']:
			remove_episode = downloaded_episodes.pop(0)

			# get the filename
			params = {'cmd': 'episode', 'tvdbid': tvdbid, 'season': remove_episode[0], 'episode': remove_episode[1], 'full_path': 1}
			episode_json = sb_request(params)
			filename = episode_json['data']['location']

			logger.info( "cleaning: S%sE%s" % (remove_episode[0], remove_episode[1]) )

			# delete the episode from disk
			delete_episode( filename )

			# update episode status in SB
			params = {'cmd': 'episode.setstatus', 'tvdbid': tvdbid, 'season': remove_episode[0], 'episode': remove_episode[1], 'status': 'ignored', 'force': 1}
			status_json = sb_request( params )
			logger.info( "S%sE%s update status: %s" % (remove_episode[0], remove_episode[1], status_json['result']) )

		# tell sickbeard to rescan local files
		params = {'cmd': 'show.refresh', 'tvdbid': tvdbid}
		refresh_json = sb_request( params )

	else:
		logger.info( "%s: %s" % (tvdbid, "No episodes to delete") )


if __name__ == '__main__':
	args = parser.parse_args()

	# see if we are supposed to process this show
	if args.tvdbid in config['shows']:
		process_episode( args.tvdbid )

