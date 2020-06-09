#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import math
import json
import gettext
import sys
from ikabot.helpers.pedirInfo import read
from decimal import *
from ikabot.config import *
from ikabot.helpers.gui import *
from ikabot.helpers.naval import *
from ikabot.helpers.varios import *

t = gettext.translation('shipMovements',
                        localedir,
                        languages=idiomas,
                        fallback=True)
_ = t.gettext

def isHostile(movement):
	if movement['army']['amount']:
		return True
	for mov in movement['fleet']['ships']:
		if mov['cssClass'] != 'ship_transport':
			return True
	return False

def shipMovements(s,e,fd):
	sys.stdin = os.fdopen(fd)
	try:
		banner()

		print(_('Ships {:d}/{:d}\n').format(getAvailableShips(s), getTotalShips(s)))

		cityId = getCurrentCityId(s)
		url = 'view=militaryAdvisor&oldView=city&oldBackgroundView=city&backgroundView=city&currentCityId={}&actionRequest=REQUESTID&ajax=1'.format(cityId)
		resp = s.post(url)
		resp = json.loads(resp, strict=False)
		movements = resp[1][1][2]['viewScriptParams']['militaryAndFleetMovements']
		time_now = int(resp[0][1]['time'])

		if len(movements) == 0:
			print(_('There are no movements'))
			enter()
			e.set()
			return

		for movement in movements:

			color = ''
			if movement['isHostile']:
				color = bcolors.RED + bcolors.BOLD
			elif movement['isOwnArmyOrFleet']:
				color = bcolors.BLUE + bcolors.BOLD
			elif movement['isSameAlliance']:
				color = bcolors.GREEN + bcolors.BOLD

			origin      = '{} ({})'.format(movement['origin']['name'], movement['origin']['avatarName'])
			destination = '{} ({})'.format(movement['target']['name'], movement['target']['avatarName'])
			arrow       = '<-' if movement['event']['isFleetReturning'] else '->'
			time_left = int(movement['eventTime']) - time_now
			print('{}{} {} {}: {} ({}) {}'.format(color, origin, arrow, destination, movement['event']['missionText'], daysHoursMinutes(time_left), bcolors.ENDC))

			if movement['isHostile']:
				troops = movement['army']['amount']
				fleets = movement['fleet']['amount']
				print(_('Troops:{}\nFleets:{}').format(addDot(troops), addDot(fleets)))
			elif isHostile(movement):
				troops = movement['army']['amount']
				ships = 0
				fleets = 0
				for mov in movement['fleet']['ships']:
					if mov['cssClass'] == 'ship_transport':
						ships += int(mov['amount'])
					else:
						fleets += int(mov['amount'])
				print(_('Troops:{}\nFleets:{}\n Ships:{}').format(addDot(troops), addDot(fleets), addDot(ships)))
			else:
				assert len(materials_names) == 5
				names_index = {'wood': 1, 'wine': 2, 'marble': 3, 'glass': 4, 'sulfur': 5}
				total_load = 0
				for resource in movement['resources']:
					amount = resource['amount']
					tradegood = resource['cssClass'].split()[1]
					index = names_index[tradegood]
					tradegood = materials_names[index]
					total_load += int( amount.replace(',', '') )
					print(_('{} of {}').format(amount, tradegood))
				ships = int(math.ceil((Decimal(total_load) / Decimal(500))))
				print(_('{:d} Ships').format(ships))
		enter()
		e.set()
	except KeyboardInterrupt:
		e.set()
		return
