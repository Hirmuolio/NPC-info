#!/usr/bin/env python3

import numpy as np
import json
import gzip

import esi_calling

esi_calling.set_user_agent('Hirmuolio/NPC-info')


def print_general( npc_stats ):
	print('Name:', npc_stats['name'])
	print('Type ID:', npc_stats['type_id'])
	print('\n' + npc_stats['description'])
	

def print_tank( npc_stats ):

	# Note: zero resistance and HP are not included in API
	structure_kin = get_attribute( 'kineticDamageResonance', npc_stats )
	structure_th  = get_attribute( 'thermalDamageResonance', npc_stats )
	structure_ex  = get_attribute( 'explosiveDamageResonance', npc_stats )
	structure_em  = get_attribute( 'emDamageResonance', npc_stats )
	
	shield_kin = get_attribute( 'shieldKineticDamageResonance', npc_stats )
	shield_th  = get_attribute( 'shieldThermalDamageResonance', npc_stats )
	shield_ex  = get_attribute( 'shieldExplosiveDamageResonance', npc_stats )
	shield_em  = get_attribute( 'shieldEmDamageResonance', npc_stats )
	
	armor_kin = get_attribute( 'armorKineticDamageResonance', npc_stats )
	armor_th  = get_attribute( 'armorThermalDamageResonance', npc_stats )
	armor_ex  = get_attribute( 'armorExplosiveDamageResonance', npc_stats )
	armor_em  = get_attribute( 'armorEmDamageResonance', npc_stats )
	
	
	shield	= get_attribute( 'shieldCapacity', npc_stats )
	armor	 = get_attribute( 'armorHP', npc_stats )
	structure = get_attribute( 'hp', npc_stats )
	
	armor_rep = 0
	shield_rep= 0
	
	if has_effect( 'npcBehaviorArmorRepairer', npc_stats ):
		# New armor rep
		armor_rep = round( get_attribute( 'entityArmorRepairDelayChanceSmall', npc_stats ) * get_attribute( 'behaviorArmorRepairerAmount', npc_stats ) / get_attribute( 'behaviorArmorRepairerDuration', npc_stats ) * 1000, 1 )
	elif has_effect( 'armorRepairForEntities', npc_stats ) or has_effect( 'entityArmorRepairingLarge', npc_stats ) or has_effect( 'entityArmorRepairingSmall', npc_stats ) or has_effect( 'entityArmorRepairingMedium', npc_stats ):
		# old armor rep
		if has_attribute( 'entityArmorRepairDelayChanceLarge', npc_stats ):
			chance = 1 - get_attribute( 'entityArmorRepairDelayChanceLarge', npc_stats )
		elif has_attribute( 'entityArmorRepairDelayChanceSmall', npc_stats ):
			chance = 1 - get_attribute( 'entityArmorRepairDelayChanceSmall', npc_stats )
		elif has_attribute( 'entityArmorRepairDelayChanceMedium', npc_stats ):
			chance = 1 - get_attribute( 'entityArmorRepairDelayChanceMedium', npc_stats )
		else:
			chance = 1 - get_attribute( 'entityArmorRepairDelayChance', npc_stats )
		if get_attribute( 'entityArmorRepairDuration', npc_stats ) != 0:	#Some sleepers do not have this
			armor_rep = round( chance * get_attribute( 'entityArmorRepairAmount', npc_stats ) / get_attribute( 'entityArmorRepairDuration', npc_stats ) * 1000, 1 )
		else:
			armor_rep = 0
	
	if has_effect( 'npcBehaviorShieldBooster', npc_stats):
		# New shield booster
		shield_rep = round( get_attribute( 'BehaviorShieldBoosterAmount', npc_stats ) / get_attribute( 'BehaviorShieldBoosterDuration', npc_stats ) * 1000, 1 )
	elif has_effect( 'entityShieldBoostingSmall', npc_stats ) or has_effect( 'entityShieldBoostingMedium', npc_stats ) or has_effect( 'entityShieldBoostingLarge', npc_stats ):
		# old shield rep	
		if has_attribute( 'entityShieldBoostDelayChanceSmall', npc_stats ):
			chance = 1 - get_attribute( 'entityShieldBoostDelayChanceSmall', npc_stats )
		elif has_attribute( 'entityShieldBoostDelayChanceMedium', npc_stats ):
			chance = 1 - get_attribute( 'entityShieldBoostDelayChanceMedium', npc_stats )
		elif has_attribute( 'entityShieldBoostDelayChanceLarge', npc_stats ):
			chance = 1 - get_attribute( 'entityShieldBoostDelayChanceLarge', npc_stats )
		else:
			chance = 1 - get_attribute( 'entityShieldBoostDelayChance', npc_stats )
				
		shield_rep = round( chance * get_attribute( 'entityShieldBoostAmount', npc_stats ) / get_attribute( 'entityShieldBoostDuration', npc_stats ) * 1000, 1 )
	
	shield_regen = 0
	if shield > 0 and get_attribute( 'shieldRechargeRate', npc_stats ) != 0:
		shield_regen = round( 1000 * 2.5 * shield / get_attribute( 'shieldRechargeRate', npc_stats ), 1 )


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
	if has_effect( 'targetAttack', npc_stats ) or has_effect( 'targetDisintegratorAttack', npc_stats ):
		# em, th, kin, ex
		turr_damage = np.array([ 
			get_attribute( 'emDamage', npc_stats ),
			get_attribute( 'thermalDamage', npc_stats ),
			get_attribute( 'kineticDamage', npc_stats ),
			get_attribute( 'explosiveDamage', npc_stats )
			]) * get_attribute( 'damageMultiplier', npc_stats )
	
	
		turr_total = sum( turr_damage )
		
		if turr_total != 0:
			turr_dps = turr_damage * ( 1000 / get_attribute( 'speed', npc_stats ) )
		
			prnt_distribution = ''
			if turr_damage[0] > 0:
				prnt_distribution += 'EM: ' + str( round( 100 * turr_damage[0] / turr_total ) ) + '% '
			if turr_damage[1] > 0:
				prnt_distribution += 'Th: ' + str( round( 100 * turr_damage[1] / turr_total ) ) + '% '
			if turr_damage[2] > 0:
				prnt_distribution += 'Kin: ' + str( round( 100 * turr_damage[2] / turr_total ) ) + '% '
			if turr_damage[3] > 0:
				prnt_distribution += 'Ex: ' + str( round( 100 * turr_damage[3] / turr_total ) ) + '% '
			
			range =  str( round( get_attribute( 'maxRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'falloff', npc_stats ) / 1000, 1 ) ) + ' km'
			tracking = str( round( 40000 * get_attribute( 'trackingSpeed', npc_stats )  / get_attribute( 'optimalSigRadius', npc_stats )  , 3 ) ) + ' rad/s'
			
			if has_effect( 'targetDisintegratorAttack', npc_stats ):
				print( 'Disintegrator: ' )
				bonus = str( 100 * get_attribute( 'damageMultiplierBonusPerCycle', npc_stats ) )
				max_bonus = str( 100 * get_attribute( 'damageMultiplierBonusMax', npc_stats ) )
				
				print( '{:<2} {:<9} {:<10}'.format(' ', 'Ramps up:', bonus + '% per cycle. Max: ' + max_bonus + '%'))
			else:
				print( 'Turrets: ' )
			print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'DPS:', sum( turr_dps ), prnt_distribution ))
			print( '{:<2} {:<9} {:<10}'.format(' ', 'Range:', range ))
			print( '{:<2} {:<9} {:<10}'.format(' ', 'Tracking:', tracking ))

			
	# Missile damage
	if has_effect( 'missileLaunchingForEntity', npc_stats ):
		
		missile_id = round( get_attribute( 'entityMissileTypeID', npc_stats ) )
		
		esi_response = esi_calling.call_esi(scope = '/v3/universe/types/{par}', url_parameters = [missile_id], job = 'get missile attributes')[0][0]
		missile_stats = process_response( esi_response )
		
		miss_damage = np.array([
			get_attribute( 'emDamage', missile_stats ),
			get_attribute( 'thermalDamage', missile_stats ),
			get_attribute( 'kineticDamage', missile_stats ),
			get_attribute( 'explosiveDamage', missile_stats )
			]) * get_attribute( 'missileDamageMultiplier', npc_stats )
			
		miss_total = sum( miss_damage )
		miss_dps = miss_damage * ( 1000 / get_attribute( 'missileLaunchDuration', npc_stats ) )
		
		range = str( round( get_attribute( 'missileEntityVelocityMultiplier', npc_stats ) * get_attribute( 'maxVelocity', missile_stats ) * get_attribute( 'missileEntityFlightTimeMultiplier', npc_stats ) * get_attribute( 'explosionDelay', missile_stats ) / 1000 /1000, 1 ) ) + ' km'
		expl_radius = str( round( get_attribute( 'aoeCloudSize', missile_stats ) * get_attribute( 'missileEntityAoeCloudSizeMultiplier', npc_stats  ) ) ) + ' m'
		expl_velocity = str( round( get_attribute( 'aoeVelocity', missile_stats ) * get_attribute( 'missileEntityAoeVelocityMultiplier', npc_stats ) ) ) + ' m/s'
		
		
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
		print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'DPS:', sum(miss_dps), prnt_distribution ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Range:', range ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Expl rad:', expl_radius ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Expl vel:', expl_velocity ))
	
	# Total damage
	if miss_total != 0 and turr_total != 0:
		total_dps = turr_dps + miss_dps
		total_total = sum( total_dps )
		
		
		
		prnt_distribution = ''
		if total_dps[0] > 0:
			prnt_distribution += 'EM: ' + str( round( 100 * total_dps[0] / total_total ) ) + '% '
		if total_dps[1] > 0:
			prnt_distribution += 'Th: ' + str( round( 100 * total_dps[1] / total_total ) ) + '% '
		if total_dps[2] > 0:
			prnt_distribution += 'Kin: ' + str( round( 100 * total_dps[2] / total_total ) ) + '% '
		if total_dps[3] > 0:
			prnt_distribution += 'Ex: ' + str( round( 100 * total_dps[3] / total_total ) ) + '% '
		
		print( 'Total: ' )
		print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'DPS:', round(total_total), prnt_distribution ))
	if has_effect( 'entitySuperWeapon', npc_stats ):
		
		super_damage = np.array([ 
			get_attribute( 'entitySuperWeaponEmDamage', npc_stats ),
			get_attribute( 'entitySuperWeaponThermalDamage', npc_stats ),
			get_attribute( 'entitySuperWeaponKineticDamage', npc_stats ),
			get_attribute( 'entitySuperWeaponExplosiveDamage', npc_stats )
			])
		super_total = sum(super_damage)
		
		prnt_distribution = ''
		if super_damage[0] > 0:
			prnt_distribution += 'EM: ' + str( round( 100 * super_damage[0] / super_total ) ) + '% '
		if super_damage[1] > 0:
			prnt_distribution += 'Th: ' + str( round( 100 * super_damage[1] / super_total ) ) + '% '
		if super_damage[2] > 0:
			prnt_distribution += 'Kin: ' + str( round( 100 * super_damage[2] / super_total ) ) + '% '
		if super_damage[3] > 0:
			prnt_distribution += 'Ex: ' + str( round( 100 * super_damage[3] / super_total ) ) + '% '
			
		super_duration = str( round( get_attribute( 'entitySuperWeaponDuration', npc_stats ) / 1000, 1 ) ) + ' s'
		
		range =  str( round( get_attribute( 'entitySuperWeaponMaxRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'entitySuperWeaponFallOff', npc_stats ) / 1000, 1 ) ) + ' km'
		tracking = str( round( 40000 * get_attribute( 'entitySuperWeaponTrackingSpeed', npc_stats )  / get_attribute( 'entitySuperWeaponOptimalSignatureRadius', npc_stats )  , 3 ) ) + ' rad/s'
		
		print( 'Superweapon: ' )
		print( '{:<2} {:<9} {:<10} {:<8}'.format(' ', 'Damage:', super_total, prnt_distribution ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Range:', range ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Tracking:', tracking ))
		print( '{:<2} {:<9} {:<10}'.format(' ', 'Duration:', super_duration ))
	print('')

def print_mobility( npc_stats ):
	print('\n-- Mobility --')
	
	max_speed = str( round( get_attribute( 'maxVelocity', npc_stats ) ) ) + ' m/s'
	cruise_speed = str( round( get_attribute( 'entityCruiseSpeed', npc_stats ) ) ) + ' m/s'
	
	
	prop_dist = str( round( get_attribute( 'entityChaseMaxDistance', npc_stats )/1000 ) ) + ' km'
	
	orbit_dist = str( round( get_attribute( 'npcBehaviorMaximumCombatOrbitRange', npc_stats )/1000 ) ) + ' km'
	sig_rad = str( round( get_attribute( 'signatureRadius', npc_stats ) ) ) + ' m'
	
	print( '{:<15} {:<10} '.format( 'Cruise speed:', cruise_speed ))
	print( '{:<15} {:<10} '.format( 'Max speed:', max_speed ))
	
	if get_attribute( 'entityMaxVelocitySignatureRadiusMultiplier', npc_stats ) != 0:
		prop_bloom = str( get_attribute( 'entityMaxVelocitySignatureRadiusMultiplier', npc_stats ) )
		print( '{:<15} {:<10} '.format( '  MWD bloom:', prop_bloom ))
	
	print( '{:<15} {:<10} '.format( 'Max speed dist:', prop_dist ))
	print( '{:<15} {:<10} '.format( 'Orbit range:', orbit_dist ))
	print( '{:<15} {:<10} '.format( 'Sig radius:', sig_rad ))
	print('')

def print_sensor( npc_stats ):
	print('\n-- Sensors --')
	
	get_attribute( 'scanRadarStrength', npc_stats )
	
	targ_range = str( round( get_attribute( 'maxTargetRange', npc_stats )/1000 ) ) + ' km'
	print( '{:<15} {:<10} '.format( 'Range:', targ_range ))
	
	max_range = str( round( get_attribute( 'maximumRangeCap', npc_stats )/1000 ) ) + ' km'
	print( '{:<15} {:<10} '.format( 'Max range:', max_range ))
	
	scan_res = str( round( get_attribute( 'scanResolution', npc_stats ) ) )
	print( '{:<15} {:<10} '.format( 'Scan res:', scan_res ))
	
	# Radar, ladar, magnetometric, gravimetric
	Sensors = [
		get_attribute( 'scanRadarStrength', npc_stats ),
		get_attribute( 'scanLadarStrength', npc_stats ),
		get_attribute( 'scanMagnetometricStrength', npc_stats ),
		get_attribute( 'scanGravimetricStrength', npc_stats )
		]
	if Sensors[0] != 0:
		print( '{:<15} {:<10} '.format( 'Radar:', Sensors[0] ))
	if Sensors[1] != 0:
		print( '{:<15} {:<10} '.format( 'Ladar:', Sensors[1] ))
	if Sensors[2] != 0:
		print( '{:<15} {:<10} '.format( 'Magnetometric:', Sensors[2] ))
	if Sensors[3] != 0:
		print( '{:<15} {:<10} '.format( 'Gravimetric:', Sensors[3] ))
		

def print_support( npc_stats ):
	print( '\n-- SUPPORT --')

	if has_effect( 'npcBehaviorRemoteArmorRepairer', npc_stats ):
		
		duration = get_attribute( 'behaviorRemoteArmorRepairDuration', npc_stats )
		repair = get_attribute( 'behaviorArmorRepairerAmount', npc_stats )
		
		if has_attribute( 'armorDamageAmount', npc_stats ):
			# Some hacky way CCP first implemented repairing NPCs
			repair = get_attribute( 'armorDamageAmount', npc_stats )
		
		rp_str = str( round( repair / duration * 1000 ) ) + ' HP/s'
		
		range = str( round( get_attribute( 'behaviorRemoteArmorRepairRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'behaviorRemoteArmorRepairFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		
		print( 'Remote armor repair')
		print( '{:<2} {:<9} {:<10}'.format('', 'Repair', rp_str ))
		print( '{:<2} {:<9} {:<10}'.format('', 'Range: ', range ))
	
	if has_effect( 'NPCRemoteArmorRepair', npc_stats ):
		# Old sleeper armor rep
		
		duration = get_attribute( 'npcRemoteArmorRepairDuration', npc_stats )
		repair = get_attribute( 'npcRemoteArmorRepairAmount', npc_stats )
		
		rp_str = str( round( repair / duration * 1000 ) ) + ' HP/s'
		
		range = '?'
		
		print( 'Remote armor repair')
		print( '{:<2} {:<9} {:<10}'.format('', 'Repair', rp_str ))
		print( '{:<2} {:<9} {:<10}'.format('', 'Range: ', range ))
		
	if has_effect( 'npcBehaviorRemoteShieldBooster',npc_stats ):
		duration = get_attribute( 'behaviorRemoteShieldBoostDuration', npc_stats )
		repair = get_attribute( 'shieldBonus', npc_stats )
		
		rp_str = str( round( repair / duration * 1000 ) ) + ' HP/s'
		
		range = str( round( get_attribute( 'behaviorRemoteShieldBoostRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'behaviorRemoteShieldBoostFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		
		print( 'Remote shield repair')
		print( '{:<2} {:<9} {:<10}'.format('', 'Repair', rp_str ))
		print( '{:<2} {:<9} {:<10}'.format('', 'Range: ', range ))
		
	
	print('')
	
def print_other( npc_stats ):
	print('\n-- Other --')
	
	if get_attribute( 'disallowAssistance', npc_stats ) == 1:
		print( 'Disallow assistance' )
	if get_attribute( 'disallowOffensiveModifiers', npc_stats ) == 1:
		print( 'EWAR immune' )
	if get_attribute( 'energyWarfareResistance', npc_stats ) != 1:
		neut_res = 1 - get_attribute( 'energyWarfareResistance', npc_stats )
		print( 'Neut resist:', str(neut_res ) )
	
	if has_effect( 'npcBehaviorSiege', npc_stats ):
		print( 'Siege' )
		
		print( '  Turret damage modifier:', get_attribute( 'BehaviorSiegeTurretDamageModifier', npc_stats )  )
		print( '  Missile damage modifier:', get_attribute( 'BehaviorSiegeMissileDamageModifier', npc_stats )  )
		print( '  Remote repair impedance:', get_attribute( 'BehaviorSiegeRemoteRepairImpedanceModifier', npc_stats )  )
		print( '  Remote assistance impedance:', get_attribute( 'BehaviorSiegeRemoteAssistanceImpedanceModifier', npc_stats )  )
		print( '  Remote dampener resistance:', get_attribute( 'BehaviorSiegeSensorDampenerResistanceModifier', npc_stats )  )
		print( '  Remote weapon disruptor resistance:', get_attribute( 'BehaviorSiegeWeaponDisruptionResistanceModifier', npc_stats )  )
		print( '  ECM resistance:', get_attribute( 'BehaviorSiegeECMResistanceModifier', npc_stats )  )
		print( '  Velocity modifier:', get_attribute( 'BehaviorSiegeMaxVelocityModifier', npc_stats )  )
		print( '  Self warp disrupt:', get_attribute( 'BehaviorSiegeWarpScrambleStatusModifier', npc_stats )  )
		print( '  Disallow tethering:', get_attribute( 'BehaviorSiegeDisallowTetheringModifier', npc_stats )  )
		print( '  Mass modifier:', get_attribute( 'BehaviorSiegeMassModifier', npc_stats )  )
		print( '  Local rep modifier:', get_attribute( 'BehaviorSiegeLocalLogisticsAmountModifier', npc_stats )  )
		print( '  Local rep duration modifier:', get_attribute( 'BehaviorSiegeLocalLogisticsDurationModifier', npc_stats )  )
	
	if get_attribute( 'AI_IgnoreDronesBelowSignatureRadius', npc_stats) > 0:
		print( 'Ignore drones below', get_attribute( 'AI_IgnoreDronesBelowSignatureRadius', npc_stats), 'm' )
	
	if get_attribute( 'entityFactionLoss', npc_stats) > 0:
		print( 'Standing loss', round( get_attribute( 'entityFactionLoss', npc_stats) * 2, 3), '%' )
		

def print_ewar( npc_stats ):
	print('\n-- EWAR --')
	
	# Scram
	if has_effect( 'behaviorWarpScramble', npc_stats ):
		type = 'Scram'
		modifier = str( round( get_attribute( 'behaviorWarpScrambleStrength', npc_stats ) ) )
		range = str( round( get_attribute( 'behaviorWarpScrambleRange', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# point
	if has_effect( 'behaviorWarpDisrupt', npc_stats ):
		type = 'Point'
		modifier = str( round( get_attribute( 'behaviorWarpDisruptStrength', npc_stats ) ) )
		range = str( round( get_attribute( 'behaviorWarpDisruptRange', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Old point entityWarpScrambleChance
	if has_effect( 'warpScrambleForEntity', npc_stats ) and get_attribute( 'entityWarpScrambleChance', npc_stats ) != 0:
		type = 'Point (o)'
		modifier = str( round( get_attribute( 'warpScrambleStrength', npc_stats ) ) )
		range = str( round( get_attribute( 'warpScrambleRange', npc_stats ) / 1000, 1 ) ) + ' km'
		chance = 'chance: ' + str( round( get_attribute( 'entityWarpScrambleChance', npc_stats ), 1 ) )
		print( '{:<8} {:<8} {:<10} {:<8}'.format(type, modifier, range, chance))
	# Web
	if has_effect( 'npcBehaviorWebifier', npc_stats ):
		type = 'Web'
		modifier = str( round( get_attribute( 'speedFactor', npc_stats ) ) ) + '%'
		range = str( round( get_attribute( 'behaviorWebifierRange', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Old web
	if has_effect( 'modifyTargetSpeed2', npc_stats ) and get_attribute( 'modifyTargetSpeedChance', npc_stats ) != 0:
		type = 'Web (o)'
		modifier = str( round( get_attribute( 'speedFactor', npc_stats ) ) ) + '%'
		range = str( round( get_attribute( 'modifyTargetSpeedRange', npc_stats ) / 1000, 1 ) ) + ' km'
		chance = 'chance: ' + str( round( get_attribute( 'modifyTargetSpeedChance', npc_stats ), 1 ) )
		print( '{:<8} {:<8} {:<10} {:<8}'.format(type, modifier, range, chance))
	# Neut
	if has_effect( 'npcBehaviorEnergyNeutralizer', npc_stats ):
		type = 'Neut'
		modifier = str( round( 1000 * get_attribute( 'energyNeutralizerAmount', npc_stats ) / get_attribute( 'behaviorEnergyNeutralizerDuration', npc_stats ) ) ) + ' GJ/s'
		range = str( round( get_attribute( 'behaviorEnergyNeutralizerRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'behaviorEnergyNeutralizerFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		if get_attribute( 'nosOverride', npc_stats ) == 1:
			type = 'NOS'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Old Neut
	if has_effect( 'entityEnergyNeutralizerFalloff', npc_stats ) and get_attribute( 'energyNeutralizerEntityChance', npc_stats ) != 0:
		chance = 'chance: ' + str( round( get_attribute( 'energyNeutralizerEntityChance', npc_stats ), 1 ) )
		type = 'Neut (o)'
		modifier = str( round( 1000 * get_attribute( 'energyNeutralizerAmount', npc_stats ) / get_attribute( 'energyNeutralizerDuration', npc_stats ) ) ) + ' GJ/s'
		range = str( round( get_attribute( 'energyNeutralizerRangeOptimal', npc_stats ) / 1000, 1 ) ) + ' km'
		if get_attribute( 'nosOverride', npc_stats ) == 1:
			type = 'NOS'
		print( '{:<8} {:<8} {:<10} {:<8}'.format(type, modifier, range, chance))
	# Paint
	if has_effect( 'behaviorTargetPainter', npc_stats ):
		type = 'TP'
		modifier = str( round( get_attribute( 'signatureRadiusBonus', npc_stats ) ) ) + '%'
		range = str( round( get_attribute( 'behaviorTargetPainterRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'behaviorTargetPainterFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Damp
	if has_effect( 'behaviorSensorDampener', npc_stats ):
		type = 'Damp'
		modifier = 'Range: ' + str( round( get_attribute( 'maxTargetRangeBonus', npc_stats ) ) ) + '%, ' + 'Res:' + str( round( get_attribute( 'scanResolutionBonus', npc_stats ) ) ) + '%'
		range = str( round( get_attribute( 'behaviorSensorDampenerRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'behaviorSensorDampenerFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<13} {:<10}'.format(type, modifier, range))
	# Tracking disruptor
	if has_effect( 'npcBehaviorTrackingDisruptor', npc_stats ):
		type = 'Tracking disruptor'
		falloff_loss = round( get_attribute( 'falloffBonus', npc_stats ) )
		optimal_loss = round( get_attribute( 'maxRangeBonus', npc_stats ) )
		tracking_loss = round( get_attribute( 'trackingSpeedBonus', npc_stats ) ) # This may be wrong

		modifier = 'Optimal:' + str(optimal_loss) + '%' +' falloff:' + str(falloff_loss) + '%' + ' tracking:' + str(tracking_loss) + '%'
		range = str( round( get_attribute( 'npcTrackingDisruptorRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'npcTrackingDisruptorFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Old tracking disruptor
	if has_effect( 'npcEntityTrackingDisruptor', npc_stats ):
		type = 'Tracking disruptor (o)'
		falloff_loss = round( get_attribute( 'falloffBonus', npc_stats ) )
		optimal_loss = round( get_attribute( 'maxRangeBonus', npc_stats ) )
		tracking_loss = round( get_attribute( 'trackingSpeedBonus', npc_stats ) )

		modifier = 'Optimal:' + str(optimal_loss) + '%' +' falloff:' + str(falloff_loss) + '%' + ' tracking:' + str(tracking_loss) + '%'
		range = str( round( get_attribute( 'npcTrackingDisruptorRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'npcTrackingDisruptorFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Guidance disruptor
	if has_effect( 'npcBehaviorGuidanceDisruptor', npc_stats ):
		type = 'Guidance disruptor'
		
		velocity_bonus = round( get_attribute( 'missileVelocityBonus', npc_stats ) )
		expl_velocity_bonus = round( get_attribute( 'aoeVelocityBonus', npc_stats ) )
		flytime_bonus = round( get_attribute( 'explosionDelayBonus', npc_stats ) )
		
		modifier = 'velocity:' + str( velocity_bonus ) + '% expl velocity:' + str( expl_velocity_bonus ) + '% flight time:' + str( flytime_bonus ) + '%'
		range = str( round( get_attribute( 'npcGuidanceDisruptorRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'npcGuidanceDisruptorFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# ECM
	if has_effect( 'behaviorECM', npc_stats ):
		type = 'ECM'
		
		ladar = get_attribute( 'scanLadarStrengthBonus', npc_stats )
		gravimetric = get_attribute( 'scanGravimetricStrengthBonus', npc_stats )
		magnetometric = get_attribute( 'scanMagnetometricStrengthBonus', npc_stats )
		radar = get_attribute( 'scanRadarStrengthBonus', npc_stats )
		
		if ladar == gravimetric == magnetometric == radar:
			modifier = radar
		else:
			modifier = 'Ladar:', ladar, ' gravimetric:', gravimetric, ' magnetometric:', magnetometric, ' radar:', radar
		range = str( round( get_attribute( 'behaviorECMRange', npc_stats ) / 1000, 1 ) ) + ' + ' + str( round( get_attribute( 'behaviorECMFalloff', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	# Old ECM
	if has_effect( 'entityECMFalloff', npc_stats ):
		type = 'ECM (o)'
		
		ladar = get_attribute( 'scanLadarStrengthBonus', npc_stats )
		gravimetric = get_attribute( 'scanGravimetricStrengthBonus', npc_stats )
		magnetometric = get_attribute( 'scanMagnetometricStrengthBonus', npc_stats )
		radar = get_attribute( 'scanRadarStrengthBonus', npc_stats )
		
		if ladar == gravimetric == magnetometric == radar:
			modifier = radar
		else:
			modifier = 'Ladar:', ladar, ' gravimetric:', gravimetric, ' magnetometric:', magnetometric, ' radar:', radar
		range = str( round( get_attribute( 'ECMRangeOptimal', npc_stats ) / 1000, 1 ) ) + ' km'
		print( '{:<8} {:<8} {:<10}'.format(type, modifier, range))
	
	print( '' )


def get_attribute( attrobute_name, npc_stats ):
	if not attrobute_name in dogma_attribute_names:
		print( 'Unknown attribute', attrobute_name )
		return 0
	attribute_id = str( dogma_attribute_names[ attrobute_name ] )
	
	if attribute_id in npc_stats['dogma_attributes']:
		return npc_stats['dogma_attributes'][ attribute_id ]
	else:
		return dogma_attributes[ attribute_id ][ "default_value" ]

def has_attribute( attrobute_name, npc_stats ):
	if not attrobute_name in dogma_attribute_names:
		print( 'Unknown attribute', attrobute_name )
		return False
	attribute_id = str( dogma_attribute_names[ attrobute_name ] )
	
	if attribute_id in npc_stats['dogma_attributes']:
		return True
	else:
		return False

def has_effect( effect_name, npc_stats ):
	if not effect_name in dogma_effect_names:
		print( 'Unknown effect', effect_name )
		# If it is not cached it is not here
		return False
	effect_id = dogma_effect_names[ effect_name ]
	
	
	if effect_id in npc_stats[ "dogma_effects" ]:
		return True
	else:
		return False

def process_response( esi_response ):
	global dogma_attributes
	global dogma_attribute_names
	global dogma_effects
	global dogma_effect_names
	
	
	response_dic = esi_response.json()
	
	npc_stats = {}
	npc_stats['name'] = response_dic['name']
	npc_stats['description'] = response_dic['description']
	npc_stats['type_id'] = response_dic['type_id']
	npc_stats['dogma_attributes'] = {}
	npc_stats['dogma_effects'] = []
	
	
	# Dogma attributes
	if not 'dogma_attributes' in response_dic:
		print('Type ID',npc_stats['type_id'],'has no defined attributes')
	elif len(response_dic['dogma_attributes']) == 0:
		print('Type ID',npc_stats['type_id'],'has zero attributes')
	else:		
		new_attributes = []
		
		for attribute_dic in response_dic['dogma_attributes']:
			dogma_id = attribute_dic["attribute_id"]
			if not str(dogma_id) in dogma_attributes:
				#Find what this ID is for
				new_attributes.append(dogma_id)
		
		if len(new_attributes) != 0:
			esi_response_arrays = esi_calling.call_esi(scope = '/v1/dogma/attributes/{par}', url_parameters = new_attributes, job = 'get info on dogma attribute')
				
			for array in esi_response_arrays:
				response_json = array[0].json()
				if 'attribute_id' in response_json:
					dogma_attributes[str(response_json['attribute_id'])] = response_json
					dogma_attribute_names[ response_json['name'] ] = response_json['attribute_id']
			#Save the ID list
			with gzip.GzipFile('dogma_attributes.gz', 'w') as outfile:
				outfile.write(json.dumps(dogma_attributes, indent=2).encode('utf-8'))
			with gzip.GzipFile('dogma_attribute_names.gz', 'w') as outfile:
				outfile.write(json.dumps(dogma_attribute_names, indent=2).encode('utf-8'))
		
		for attribute_dic in response_dic['dogma_attributes']:
			npc_stats['dogma_attributes'][ str( attribute_dic["attribute_id"] ) ] = attribute_dic["value"]
	
	
	# Dogma effects
	if not 'dogma_effects' in response_dic:
		print('Type ID',npc_stats['type_id'],'has no defined effects')
	elif len(response_dic['dogma_effects']) == 0:
		print('Type ID',npc_stats['type_id'],'has zero effects')
	else:
		
		new_effects = []
		
		for effect_dic in response_dic['dogma_effects']:
			dogma_id = effect_dic['effect_id']
			if not str(dogma_id) in dogma_effects:
				#Find what this ID is for
				new_effects.append(dogma_id)
		
		if len(new_effects) != 0:
			esi_response_arrays = esi_calling.call_esi(scope = '/v2/dogma/effects/{par}', url_parameters = new_effects, job = 'get info on dogma attribute')
				
			for array in esi_response_arrays:
				response_json = array[0].json()
				if 'effect_id' in response_json:
					dogma_effects[str(response_json['effect_id'])] = response_json
					dogma_effect_names[ response_json['name'] ] = response_json['effect_id']
				else:
					print( "Something wrong: ", response_json )
			#Save the ID list
			with gzip.GzipFile('dogma_effects.gz', 'w') as outfile:
				outfile.write(json.dumps(dogma_effects, indent=2).encode('utf-8'))
			with gzip.GzipFile('dogma_effect_names.gz', 'w') as outfile:
				outfile.write(json.dumps(dogma_effect_names, indent=2).encode('utf-8'))

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


try:
	#Load cached dogma attribute ID info
	with gzip.GzipFile('dogma_attributes.gz', 'r') as fin:
		dogma_attributes = json.loads(fin.read().decode('utf-8'))
except FileNotFoundError:
	#No file found. Start from scratch
	dogma_attributes = {}

try:
	#Load cached dogma attribute ID-name info
	with gzip.GzipFile('dogma_attribute_names.gz', 'r') as fin:
		dogma_attribute_names = json.loads(fin.read().decode('utf-8'))
except FileNotFoundError:
	#No file found. Start from scratch
	dogma_attribute_names = {}

try:
	#Load cached dogma effect ID info
	with gzip.GzipFile('dogma_effects.gz', 'r') as fin:
		dogma_effects = json.loads(fin.read().decode('utf-8'))
except FileNotFoundError:
	#No file found. Start from scratch
	dogma_effects = {}

try:
	#Load cached dogma effect ID-name info
	with gzip.GzipFile('dogma_effect_names.gz', 'r') as fin:
		dogma_effect_names = json.loads(fin.read().decode('utf-8'))
except FileNotFoundError:
	#No file found. Start from scratch
	dogma_effect_names = {}


while True:
	#Call ESI
	type_id = input("\n\nGive type ID: ")
	
	esi_response = esi_calling.call_esi(scope = '/v3/universe/types/{par}', url_parameters = [type_id], job = 'get type ID attributes')[0][0]

	
	if not esi_response.status_code in [400, 404]:
		print('')
		print('*************************************')
		npc_stats = process_response( esi_response )
		print_general( npc_stats )
		print_tank( npc_stats )
		print_damage( npc_stats )
		print_support( npc_stats )
		print_ewar( npc_stats )
		print_mobility( npc_stats )
		print_sensor( npc_stats )
		print_other( npc_stats )
	else:
		print(esi_response.status_code, '- invalid ID')
	
