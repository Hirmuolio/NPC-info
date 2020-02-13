#!/usr/bin/env python3

import numpy as np
import json

import esi_calling

datasource = 'tranquility'
#datasource = 'singularity'


def print_general( npc_stats ):
	print('')
	print('----')
	print('Name:', npc_stats['name'])
	print('Type ID:', npc_stats['type_id'])
	print('\n' + npc_stats['description'])
	

def print_tank( npc_stats ):
	#Attributes:
	#9,   structure HP
	#109, structure kinteic resonance
	#110, structure thermal resonance
	#111, structure explosive resonance
	#113, structure em resonance

	#265  armor HP
	#269, armor kinteic resonance
	#270, armor thermal resonance
	#268, armor explosive resonance
	#267, armor em resonance
	#2635 armor rep amount
	#2633 armor rep duration (ms)
	#1009 entityArmorRepairDelayChance

	#263  shield HP
	#273, shield kinteic resonance
	#274, shield thermal resonance
	#272, shield explosive resonance
	#271, shield em resonance
	#479  shield recharge time
	#636  shield rep duration (ms)
	#637  shield rep amount
	#639  entityShieldBoostDelayChance

	#zero resistance and HP are not included in API
	structure_kin = get_attribute( "109", 1, npc_stats )
	structure_th  = get_attribute( "110", 1, npc_stats )
	structure_ex  = get_attribute( "111", 1, npc_stats )
	structure_em  = get_attribute( "113", 1, npc_stats )
	
	shield_kin = get_attribute( "273", 1, npc_stats )
	shield_th  = get_attribute( "274", 1, npc_stats )
	shield_ex  = get_attribute( "272", 1, npc_stats )
	shield_em  = get_attribute( "271", 1, npc_stats )
	
	armor_kin = get_attribute( "269", 1, npc_stats )
	armor_th  = get_attribute( "270", 1, npc_stats )
	armor_ex  = get_attribute( "268", 1, npc_stats )
	armor_em  = get_attribute( "267", 1, npc_stats )
	
	
	shield    = get_attribute( "263", 0, npc_stats )
	armor     = get_attribute( "265", 0, npc_stats )
	structure = get_attribute( "9", 0, npc_stats )
	
	armor_rep = round( get_attribute( "1009", 1, npc_stats ) * get_attribute( "2635", 0, npc_stats ) / get_attribute( "2633", 1, npc_stats ) * 1000, 1 )
	shield_rep = round( get_attribute( "639", 1, npc_stats ) * get_attribute( "637", 0, npc_stats ) / get_attribute( "636", 1, npc_stats ) * 1000, 1 )
	shield_regen = round( 1000 * 2.5 * shield / get_attribute( "479", 1, npc_stats ), 1 )


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
	
	prnt_shield_em = str( round((1-shield_resist[0])*100, 2) )+'%'
	prnt_shield_th = str( round((1-shield_resist[1])*100, 2) )+'%'
	prnt_shield_kin = str( round((1-shield_resist[2])*100, 2) )+'%'
	prnt_shield_ex = str( round((1-shield_resist[3])*100, 2) )+'%'
	
	prnt_armor_em = str( round((1-armor_resist[0])*100, 2) )+'%'
	prnt_armor_th = str( round((1-armor_resist[1])*100, 2) )+'%'
	prnt_armor_kin = str( round((1-armor_resist[2])*100, 2) )+'%'
	prnt_armor_ex = str( round((1-armor_resist[3])*100, 2) )+'%'
	
	prnt_structure_em = str( round((1-structure_resist[0])*100, 2) )+'%'
	prnt_structure_th = str( round((1-structure_resist[1])*100, 2) )+'%'
	prnt_structure_kin = str( round((1-structure_resist[2])*100, 2) )+'%'
	prnt_structure_ex = str( round((1-structure_resist[3])*100, 2) )+'%'
	
	# 30 hp/s + 5 hp/s
	prnt_shield_rep = str( shield_rep ) + ' + ' + str( shield_regen ) + ' HP/s'
	prnt_armor_rep =  str( armor_rep ) + ' HP/s'
	
	print('\n-- TANK --')
	print( '{:<10} {:<10} {:<8} {:<8} {:<8} {:<8} {:<8}'.format(' ', 'HP', 'EM', 'TH', 'KIN', 'EX', 'Repair'))
	print( '{:<10} {:<10} {:<8} {:<8} {:<8} {:<8} {:<8}'.format('shield', int(shield), prnt_shield_em, prnt_shield_th, prnt_shield_kin, prnt_shield_ex, prnt_shield_rep) )
	print( '{:<10} {:<10} {:<8} {:<8} {:<8} {:<8} {:<8}'.format('armor', int(armor), prnt_armor_em, prnt_armor_th, prnt_armor_kin, prnt_armor_ex, prnt_armor_rep ) )
	print( '{:<10} {:<10} {:<8} {:<8} {:<8} {:<8}'.format('structure', int(structure), prnt_structure_em, prnt_structure_th, prnt_structure_kin, prnt_structure_ex) )
	print('')
	print( '{:<17s} {:<14} {:<}'.format('Ammo/damage type', 'Relative', 'EHP'))
	print( '{:<17s} {:<14} {:<}'.format('', 'effectiveness', ''))

	for n in range(0, len(ammo_list)):
		ammo = ammo_list[n]
		effectiveness = ehp_normalized[n]
		effectivehp = ehp[n]
		print( '{:<17s} {:<14} {:<}'.format(ammo, str(effectiveness), str(effectivehp)))
	
	print('')

def print_damage( npc_stats ):
	
	print('\n-- DAMAGE --')
	
	miss_total = 0
	turr_total = 0
	# Turret damage
	
	# em, th, kin, ex
	turr_damage = np.array([ 
		get_attribute( "114", 0, npc_stats ),
		get_attribute( "118", 0, npc_stats ),
		get_attribute( "117", 0, npc_stats ),
		get_attribute( "116", 0, npc_stats )
		]) * get_attribute( "64", 1, npc_stats )
	
	
	turr_total = sum( turr_damage )
	turr_dps = round( turr_total / get_attribute( "51", 1, npc_stats ) * 1000 )
	
	if turr_total != 0:
		prnt_distribution = ''
		if turr_damage[0] > 0:
			prnt_distribution += 'EM: ' + str( round( 100 * turr_damage[0] / turr_total ) ) + '% '
		if turr_damage[1] > 0:
			prnt_distribution += 'Th: ' + str( round( 100 * turr_damage[1] / turr_total ) ) + '% '
		if turr_damage[2] > 0:
			prnt_distribution += 'Kin: ' + str( round( 100 * turr_damage[2] / turr_total ) ) + '% '
		if turr_damage[3] > 0:
			prnt_distribution += 'Ex: ' + str( round( 100 * turr_damage[3] / turr_total ) ) + '% '
		
		range =  str( round( get_attribute( "54", 0, npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( "158", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		tracking = str( round( get_attribute( "54", 0, npc_stats ) / get_attribute( "620", 1, npc_stats ) , 3 ) ) + ' rad/s'
		
		print( 'Turrets: ' )
		print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'DPS:', turr_dps, prnt_distribution ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Range:', range ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Tracking:', tracking ))
	
	# Missile damage
	if 569 in npc_stats['dogma_effects']:
		missile_id = round( get_attribute( "507", 0, npc_stats ) )
		
		esi_response = esi_calling.call_esi(scope = '/v3/universe/types/{par}', url_parameters = [missile_id], job = 'get missile attributes')[0][0]
		missile_stats = process_response( esi_response )
		
		miss_damage = np.array([ 
			get_attribute( "114", 0, missile_stats ),
			get_attribute( "118", 0, missile_stats ),
			get_attribute( "117", 0, missile_stats ),
			get_attribute( "116", 0, missile_stats )
			]) * get_attribute( "212", 1, npc_stats )
			
		miss_total = sum( miss_damage )
		miss_dps = round( miss_total / get_attribute( "506", 1, npc_stats ) * 1000 )
		
		range = str( round( get_attribute( "645", 0, npc_stats ) * get_attribute( "37", 0, missile_stats ) * get_attribute( "646", 0, npc_stats ) * get_attribute( "281", 0, missile_stats ) / 1000 /1000, 1 ) ) + ' km'
		expl_radius = str( round( get_attribute( "654", 0, missile_stats ) * get_attribute( "858", 0, npc_stats ) ) ) + ' m'
		expl_velocity = str( round( get_attribute( "653", 0, missile_stats ) * get_attribute( "859", 0, npc_stats ) ) ) + ' m/s'
		
		
		prnt_distribution = ''
		if miss_damage[0] > 0:
			prnt_distribution += 'EM: ' + str( round( 100 * miss_damage[0] / miss_total ) ) + '% '
		if miss_damage[1] > 0:
			prnt_distribution += 'Th: ' + str( round( 100 * miss_damage[1] / miss_total ) ) + '% '
		if miss_damage[2] > 0:
			prnt_distribution += 'Kin: ' + str( round( 100 * miss_damage[2] / miss_total ) ) + '% '
		if miss_damage[3] > 0:
			prnt_distribution += 'Ex: ' + str( round( 100 * miss_damage[3] / miss_total ) ) + '% '
			
		
		print( 'Missiles: ' )
		print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'DPS:', miss_dps, prnt_distribution ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Range:', range ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Expl rad:', expl_radius ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Expl vel:', expl_velocity ))
	
	# Total damage
	if miss_total != 0 and turr_total != 0:
		total_dmg = turr_damage + miss_damage
		total_total = sum( total_dmg )
		
		total_dps = turr_dps + miss_dps
		
		prnt_distribution = ''
		if total_dmg[0] > 0:
			prnt_distribution += 'EM: ' + str( round( 100 * total_dmg[0] / total_total ) ) + '% '
		if total_dmg[1] > 0:
			prnt_distribution += 'Th: ' + str( round( 100 * total_dmg[1] / total_total ) ) + '% '
		if total_dmg[2] > 0:
			prnt_distribution += 'Kin: ' + str( round( 100 * total_dmg[2] / total_total ) ) + '% '
		if total_dmg[3] > 0:
			prnt_distribution += 'Ex: ' + str( round( 100 * total_dmg[3] / total_total ) ) + '% '
		
		print( 'Total: ' )
		print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'DPS:', total_dps, prnt_distribution ))

def print_mobility( npc_stats ):
	print('\n-- Mobility --')
	
	max_speed = str( round( get_attribute( "37", 0, npc_stats ) ) ) + ' m/s'
	cruise_speed = str( round( get_attribute( "508", 0, npc_stats ) ) ) + ' m/s'
	
	
	prop_dist = str( round( get_attribute( "665", 0, npc_stats )/1000 ) ) + ' km'
	
	orbit_dist = str( round( get_attribute( "2786", 0, npc_stats )/1000 ) ) + ' km'
	
	print( '{:<15} {:<10} '.format( 'Cruise speed:', cruise_speed ))
	print( '{:<15} {:<10} '.format( 'Max speed:', max_speed ))
	
	if get_attribute( "1133", 0, npc_stats ) != 0:
		prop_bloom = str( round( get_attribute( "1133", 0, npc_stats ) * 100 ) ) + '%'
		print( '{:<15} {:<10} '.format( '  MWD bloom:', prop_bloom ))
	
	print( '{:<15} {:<10} '.format( 'Max speed dist:', prop_dist ))
	print( '{:<15} {:<10} '.format( 'Orbit range:', orbit_dist ))
	

def print_ewar( npc_stats ):
	print('\n-- EWAR --')
	
	# Scram
	if 6745 in npc_stats['dogma_effects']:
		type = 'Scram'
		modifier = str( round( get_attribute( "2509", 0, npc_stats ) ) )
		range = str( round( get_attribute( "2507", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# point
	if 6744 in npc_stats['dogma_effects']:
		type = 'Point'
		modifier = str( round( get_attribute( "2510", 0, npc_stats ) ) )
		range = str( round( get_attribute( "2504", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Web
	if 2509 in npc_stats['dogma_effects']:
		type = 'Web'
		modifier = str( round( get_attribute( "20", 0, npc_stats ) ) ) + '%'
		range = str( round( get_attribute( "2500", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Neut
	if 6756 in npc_stats['dogma_effects']:
		type = 'Neut'
		modifier = str( round( 1000 * get_attribute( "2522", 0, npc_stats ) / get_attribute( "2519", 0, npc_stats ) ) ) + ' GJ/s'
		range = str( round( get_attribute( "2520", 0, npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( "2521", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Paint
	if 6754 in npc_stats['dogma_effects']:
		type = 'TP'
		modifier = str( round( get_attribute( "554", 0, npc_stats ) ) ) + '%'
		range = str( round( get_attribute( "2524", 0, npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( "2525", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Damp
	if 6755 in npc_stats['dogma_effects']:
		type = 'Damp'
		modifier = 'Range: ' + str( round( get_attribute( "309", 0, npc_stats ) ) ) + '%, ' + 'Res:' + str( round( get_attribute( "566", 0, npc_stats ) ) ) + '%'
		range = str( round( get_attribute( "2528", 0, npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( "2529", 0, npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<13} {:<10}'.format(type, modifier, range))
	# Tracking disruptor
	if 6747 in npc_stats['dogma_effects']:
		type = 'TD'
		modifier = 'TODO'
		range = 'TODO'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Guidance disruptor
	if 6746 in npc_stats['dogma_effects']:
		type = 'GD'
		modifier = 'TODO'
		range = 'TODO'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# ECM
	if 6747 in npc_stats['dogma_effects']:
		type = 'GD'
		modifier = 'TODO'
		range = 'TODO'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	print( '' )

def get_attribute( attribute_id, default, npc_stats ):
	if attribute_id in npc_stats['dogma_attributes']:
		return npc_stats['dogma_attributes'][ attribute_id ]
	else:
		return default


def process_response( esi_response ):
	response_dic = esi_response.json()
	
	npc_stats = {}
	npc_stats['name'] = response_dic['name']
	npc_stats['description'] = response_dic['description']
	npc_stats['type_id'] = response_dic['type_id']
	npc_stats['dogma_attributes'] = {}
	npc_stats['dogma_effects'] = []
	
	if not 'dogma_attributes' in response_dic:
		print('Type ID',npc_stats['type_id'],'has no defined attributes')
		return npc_stats
	elif len(response_dic['dogma_attributes']) == 0:
		print('Type ID',npc_stats['type_id'],'has zero attributes')
		return npc_stats
	
	for attribute_dic in response_dic['dogma_attributes']:
		npc_stats['dogma_attributes'][ str( attribute_dic["attribute_id"] ) ] = attribute_dic["value"]
	for effect_dic in response_dic['dogma_effects']:
		npc_stats['dogma_effects'].append( effect_dic["effect_id"] )
	
	return npc_stats

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
	
	esi_response = esi_calling.call_esi(scope = '/v3/universe/types/{par}', url_parameters = [type_id], job = 'get type ID attributes')[0][0]

	
	if not esi_response.status_code in [400, 404]:
		npc_stats = process_response( esi_response )
		print_general( npc_stats )
		print_tank( npc_stats )
		print_damage( npc_stats )
		print_ewar( npc_stats )
		print_mobility( npc_stats )
	else:
		print(esi_response.status_code, '- invalid ID')
	
