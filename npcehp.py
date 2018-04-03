#!/usr/bin/env python3

import numpy as np
import requests
import json

#Ammo attributes
#arrays in this order: em, th, kin, ex
#all are normalized to total damage = 1

#Projectile
emp = np.array([9, 0, 1, 2])/np.sum([9, 0, 1, 2])
phased = np.array([0, 10, 2, 0])/np.sum([0, 10, 2, 0])
fusion = np.array([0, 0, 2, 10])/np.sum([0, 0, 2, 10])
hail = np.array([0, 0, 3.3, 12.1])/np.sum([0, 0, 3.3, 12.1])

#Hybrid
antimatter = np.array([0, 5, 7, 0])/np.sum([0, 5, 7, 0])
void = np.array([0, 7.7, 7.7, 0])/np.sum([0, 7.7, 7.7, 0])

#Laser
multi = np.array([7, 5, 0, 0])/np.sum([7, 5, 0, 0])
conflag = np.array([7.7, 7.7, 0, 0])/np.sum([7.7, 7.7, 0, 0])

#Single damage
em = np.array([1, 0, 0, 0])
th = np.array([0, 1, 0, 0])
kin = np.array([0, 0, 1, 0])
ex = np.array([0, 0, 0, 1])


while True:
	#Call ESI
	type_id = input("Give type ID: ")

	url = "https://esi.tech.ccp.is/v3/universe/types/"+type_id+"/?datasource=tranquility&language=en-us"

	#Uncomment this to get SISI stats
	#url = "https://esi.tech.ccp.is/v3/universe/types/"+type_id+"/?datasource=singularity&language=en-us"

	esi_response = requests.get(url)
	npc_stats = esi_response.json()

	#Attributes:
	#9, structure HP
	#109, structure kinteic resonance
	#110, structure thermal resonance
	#111, structure explosive resonance
	#113, structure em resonance

	#265 armor HP
	#269, armor kinteic resonance
	#270, armor thermal resonance
	#268, armor explosive resonance
	#267, armor em resonance

	#263 shield HP
	#273, shield kinteic resonance
	#274, shield thermal resonance
	#272, shield explosive resonance
	#271, shield em resonance

	#zero resistance is not included in API
	structure_kin = 1
	structure_th = 1
	structure_ex = 1
	structure_em = 1
	
	shield_kin = 1
	shield_th = 1
	shield_ex = 1
	shield_em = 1
	
	armor_kin = 1
	armor_th = 1
	armor_ex = 1
	armor_em = 1

	length = len(npc_stats['dogma_attributes'])

	for n in range(0, length):
		dogma_id = npc_stats['dogma_attributes'][n]['attribute_id']
		value = npc_stats['dogma_attributes'][n]['value']
		if dogma_id == 9:
			structure = value
		elif dogma_id == 109:
			structure_kin = value
		elif dogma_id == 110:
			structure_th = value
		elif dogma_id == 111:
			structure_ex = value
		elif dogma_id == 113:
			structure_em = value
			
		elif dogma_id == 265:
			armor = value
		elif dogma_id == 269:
			armor_kin = value
		elif dogma_id == 270:
			armor_th = value
		elif dogma_id == 268:
			armor_ex = value
		elif dogma_id == 267:
			armor_em = value
			
		elif dogma_id == 263:
			shield = value
		elif dogma_id == 273:
			shield_kin = value
		elif dogma_id == 274:
			shield_th = value
		elif dogma_id == 272:
			shield_ex = value
		elif dogma_id == 271:
			shield_em = value

	structure_resist = np.array([structure_em, structure_th, structure_kin, structure_ex])
	armor_resist = np.array([armor_em, armor_th, armor_kin, armor_ex])
	shield_resist = np.array([shield_em, shield_th, shield_kin, shield_ex])

	#Calculate the EHP of the rat with all the ammo typses.
	emp_ehp = structure/np.sum(emp*structure_resist) + armor/np.sum(emp*armor_resist) + shield/np.sum(emp*shield_resist)
	phased_ehp = structure/np.sum(phased*structure_resist) + armor/np.sum(phased*armor_resist) + shield/np.sum(phased*shield_resist)
	fusion_ehp = structure/np.sum(fusion*structure_resist) + armor/np.sum(fusion*armor_resist) + shield/np.sum(fusion*shield_resist)
	hail_ehp = structure/np.sum(hail*structure_resist) + armor/np.sum(hail*armor_resist) + shield/np.sum(hail*shield_resist)

	antimatter_ehp = structure/np.sum(antimatter*structure_resist) + armor/np.sum(antimatter*armor_resist) + shield/np.sum(antimatter*shield_resist)
	void_ehp = structure/np.sum(void*structure_resist) + armor/np.sum(void*armor_resist) + shield/np.sum(void*shield_resist)

	multi_ehp = structure/np.sum(multi*structure_resist) + armor/np.sum(multi*armor_resist) + shield/np.sum(multi*shield_resist)
	conflag_ehp = structure/np.sum(conflag*structure_resist) + armor/np.sum(conflag*armor_resist) + shield/np.sum(conflag*shield_resist)

	em_ehp = structure/np.sum(em*structure_resist) + armor/np.sum(em*armor_resist) + shield/np.sum(em*shield_resist)
	th_ehp = structure/np.sum(th*structure_resist) + armor/np.sum(th*armor_resist) + shield/np.sum(th*shield_resist)
	kin_ehp = structure/np.sum(kin*structure_resist) + armor/np.sum(kin*armor_resist) + shield/np.sum(kin*shield_resist)
	ex_ehp = structure/np.sum(ex*structure_resist) + armor/np.sum(ex*armor_resist) + shield/np.sum(ex*shield_resist)
	
	ammo_list = ['emp',
	'phased plasma',
	'fusion',
	'hail',
	'antimatter',
	'void',
	'multispectral',
	'conflag',
	'electromagnetic',
	'thermal',
	'kinetic',
	'explosive']
	
	ehp = np.array(	[emp_ehp,
	phased_ehp,
	fusion_ehp,
	hail_ehp,
	antimatter_ehp,
	void_ehp,
	multi_ehp,
	conflag_ehp,
	em_ehp,
	th_ehp,
	kin_ehp,
	ex_ehp
	])
	
	ehp_normalized = np.amin(ehp) / ehp

	#Sort and round things for displaying
	ehp_normalized, ammo_list, ehp = zip(*sorted(zip(ehp_normalized, ammo_list, ehp)))

	ehp_normalized = np.around(ehp_normalized, decimals=2)
	ehp = np.around(ehp , decimals=1)

	ehp_normalized = list(reversed(ehp_normalized))
	ehp = list(reversed(ehp))
	ammo_list = list(reversed(ammo_list))

	print('')
	print('----')
	print('Type ID:', npc_stats['type_id'])
	print('Name:', npc_stats['name'])
	print('----')
	print( '{:<17s} {:<14} {:<}'.format('Ammo', 'Relative', 'EHP'))
	print( '{:<17s} {:<14} {:<}'.format('', 'effectiveness', ''))

	for n in range(0, len(ammo_list)):
		ammo = ammo_list[n]
		effectiveness = ehp_normalized[n]
		effectivehp = ehp[n]
		print( '{:<17s} {:<14} {:<}'.format(ammo, str(effectiveness), str(effectivehp)))
	
	print('----')
	print('')
