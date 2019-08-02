#******************************************************************************
# Name: Sandbox Settings Class
# Author: Elton "Elxx" Muuga (http://elxx.net)
# Version: 1.0
# Website: http://sandboxmod.com
#******************************************************************************

import host
import ConfigParser

from sbxErrorHandling import ExceptionOutput

class sbxSettingsManager:
	def __init__(self):
		self.mpObjectLimit = 850
		self.mapObjectLimits = {
			"clearing":			920,
			"dalian_plant":		920,
			"daqing_oilfields":	860,
			"dragon_valley":	950,
			"fushe_pass":		860,
			"gulf_of_oman":		910,
			"kubra_dam":		880,
			"mashtuur_city":	880,
			"operation_clean_sweep":	855,
			"road_to_jalalabad":	890,
			"sharqi_peninsula":	870,
			"songhua_stalemate":	870,
			"strike_at_karkand":	860,
			"wake_island_2007":	930,
			"zatar_wetlands":	820
		}
		self.sbxObjects = ['sign1','sign2','sign3','sign4','sign5','teddy','ball','fish','toolshed_door_l','toolshed_door_r','pallet','concrete_pillar_beam','beam_01','xp2_highwaynoisewallpost_01','woodsteel_bridge_segment','wooden_bridge_segment','xp1_submarinepen_walkway','mi_plane_stair','woodencrate_1m','woodencrate_3m','woodencrate_4m','container_cargo_red','container_cl_green','construct_metal_plate','xp1_airtower_elevator_door','glassplane01','ch_stnwalls_10m_up','ch_stnwalls_10m_stairs','wallhigh02','brickwall','brick_pillar','stonefence_5m','barrier_blocks_high_8m','xp2_highwaynoisewall_01','ch_wall_high_6m','ch_wall_high_6m_door','ch_wall_high_6m_win_hole','ch_wall_high_l','ch_wall_low_6m','ch_wall_low_end','wirefence_6m','xp2_overpass_fence_12m','fence_corrugated_3x12m','fence_dest','xp2_farm_fence_01','xp2_farmfence_post','xp2_picketfence_01','steelrailing_4m','pedestrian_railing_12m_ends','trestle01_dest','concretebarrier','xp2_divider_01','mi_sandbags_4m','mi_sandbags_corner_4m','mi_sandbags_circle_half','cablepole','wpipe_10m','wpipe_bend','cabledrum_2m','xp2_pylon_01','cone_dest','xp2_pylon_02','barrel_green','xp2_alaskasign02','xp2_alaskan_sign_04','sign_streetcrossing_dest','trafficlight_dest','billboard_highway_01','billboard_highway_02','billboard_highway_03','billboard_dicecream','xp2_highway_billboard_01','xp2_highway_billboard_02','xp2_highway_exit','xp2_highway_service','sign_electric','sign_noentry','sign_powercompany','nc_birch01','me_olive03','nc_weeping01','me_palmtree01','nc_pinebig02','xp2_sprucetree_01','me_deadtree01','me_shortpalm01','me_flowerpot01','me_wildbush01','me_tropicalplant03','me_vines01','xp2_picnictable_01','chsalestable_02','table01','xp1_desk','cafechair','parkbench2','xp1_bed','tvset','xp1_desk_lamp','xp1_tall_lamp','xp1_devils_lamp','barrel_yellow','fueltankwagon','barrel_blue','fishingbox','trash_dumpster','lrg_trash_dumpster','trashcan_small','basket_hoops','xp2_swingset','xp2_mailbox_01','xp2_icemachine','wheelbarrow','xp1_wheelchair','phonebooth','ch_phone_booth','xp2_haybale_01','chsalestable_box_02','xp2_cowtrough_01','xp1_iv_stand_2','xp1_launchpad_elevator','xp1_ac_bomb_rack','xp1_ac_missile_rack','xp2_windmill_blades_02','xp1_controlbunker_elevatordoor','xp1_terminaldoor','wpipe_support','pipestack_01','fx_fire','fx_smoke','fx_fountain','fx_waterfall','ladder_10m_noholders','ladder_40m','woodencrate_destructible','concreteblock_airstrip_endstr','convbelt','pedestrian_railing_6m_ends','gate_boom','rock2m']
		self.vehicles = ['xpak_ailraider','xpak_apache','xpak_bmp3','xpak_hind','xpak2_tnkl2a6','xpak2_tiger','xpak2_tnkc2','xpak2_eurofighter','xp2_musclecar_01','air_su39','che_wz11','she_ec635','xpak2_fantan','jeep_faav','jep_mec_paratrooper','usjep_hmmwv','jep_vodnik','jep_nanjing','usapc_lav25','apc_btr90','apc_wz551','usaav_m6','aav_tunguska','aav_type95','ustnk_m1a2','rutnk_t90','tnk_type98','she_littlebird','ahe_ah1z','ahe_havoc','ahe_z10','usthe_uh60','the_mi17','chthe_z8','air_f35b','ruair_mig29','air_j10','usair_f15','usair_f18','ruair_su34','air_a10','air_su30mkk','xpak_civ2','xpak_civ1','xpak_atv','xpak_forklift','boat_rib','xpak_jetski','truck1','xpak2_semi','xpak2_fantan','dirtbike','faav_nb','faav_st','ats_tow','usaas_stinger','uav_pred']
		self.dynamic_objects = ['teddy','ball','fish','fx_fire','fx_smoke','fx_fountain','fx_waterfall','fence_dest','barrel_blue','cone_dest','fueltankwagon','fishingbox','barrel_yellow','supply_crate','xpak_ailraider','xpak_apache','xpak_bmp3','xpak_hind','xpak2_tnkl2a6','xpak2_tiger','xpak2_tnkc2','xpak2_eurofighter','xp2_musclecar_01','air_su39','che_wz11','she_ec635','xpak2_fantan','jeep_faav','jep_mec_paratrooper','usjep_hmmwv','jep_vodnik','jep_nanjing','usapc_lav25','apc_btr90','apc_wz551','usaav_m6','aav_tunguska','aav_type95','ustnk_m1a2','rutnk_t90','tnk_type98','she_littlebird','ahe_ah1z','ahe_havoc','ahe_z10','usthe_uh60','the_mi17','chthe_z8','air_f35b','ruair_mig29','xpak2_fantan','air_j10','usair_f15','usair_f18','ruair_su34','air_a10','air_su30mkk','xpak_civ2','xpak_civ1','xpak_atv','xpak_forklift','boat_rib','xpak_jetski','truck1','xpak2_semi','dirtbike','faav_nb','faav_st','ats_tow','usaas_stinger','uav_pred','aircontroltower','usaas_stinger_spw']
		self.pMessages = {
			"GRABMODE_ALL":	     [1031105, 1],
			"GRABMODE_MINE":		[1031105, 2],
			"":	     [1031105, 3],
			"":     [1031113, 1],
			"GROUP_INITIALIZED":    [1031113, 2],
			"GROUP_ALREADY_SELECTED": [1031113, 3],
			"GROUP_DESELECTED":	     [1031121, 1],
			"GROUP_SELECTED":	       [1031121, 2],
			"GROUP_OBJECTADDED":    [1031121, 3],
			"GROUP_OBJECTREMOVED":  [1031115, 1],
			"ROTATION_SAVED":	       [1031115, 2],
			"ROTATION_CLEARED":	     [1031115, 3],
			"AUTOLOCK_ENABLED":	     [1031120, 1],
			"AUTOLOCK_DISABLED":    [1031120, 2],
			"BUSY":						 [1031120, 3],
			"AUTOGRAB_ENABLED":	     [1031109, 1],
			"AUTOGRAB_DISABLED":    [1031109, 2],
			"MERGE_STARTED":			[1031109, 3],
			"MERGE_COMPLETED":	      [1031923, 1],
			"MERGE_CANCELLED":	      [1031923, 2],
			"GROUP_LIMITREACHED":   [1031923, 3],
			"SAVEDELAY":			    [1032415, 1],
			"GROUP_DUPELIMITREACHED": [1032415, 2],
			"DUPEDELAY":			    [1032415, 3],
			"GROUP_UNGROUPED":	      [1031119, 1],
			"OBJLIMITREACHED":	      [1031119, 2],
			"GROUP_OBJLIMITREACHED": [1031119, 3],
			"SELF_BUSY":			    [1031406, 1],
			"GRABMODE_TEMPLATE":	     [1031619, 2],
			"GRABMODE_VEHICLE":	     [1190601, 2],
			"GRABSNAP_RELATIVE":	     [1190507, 2],
			"GRABSNAP_TRACER":	     [1191819, 2],
			"ANIMATION_CREATED":	     [1190304, 2],
			"ANIMATION_SELECTED":	     [1220118, 2],
			"ANIMATION_DESELECTED":	     [1222016, 2],
			"KEYFRAME_ADDED":	     [1220803, 2],
			"KEYFRAME_DELETED":	     [1220122, 2],
			"NO_SELECTED_ANIMATION":	     [1220104, 2],
			"KEYFRAME_UPDATED":	     [1031619, 3],
			"ADDED_TO_ANIMATION":	     [1190601, 3],
			"ANIMATION_DELETED":	     [1190507, 3],
			"REMOVED_FROM_ANIMATION":	     [1191819, 3],
			"THERE_ARE_NO_OBJECTS_TO_ANIMATE":	     [1190304, 3],
			"THERE_ARE_NO_KEYFRAMES_TO_DELETE":	     [1220118, 3],
			"NO_ANIMATION_FRAME_DEFINED":	     [1222016, 3],
			"AUTOHEAL_ON":	     [1220803, 3],
			"AUTOHEAL_OFF":	     [1220122, 3],
			"PRESET_CHOOSE_CLEAR":	     [1190304, 1],
			"TRIGGER_DIFF_ANIMATION":	     [1190601, 1],
			"LOOP_STARTED_CONTINUOUS":	     [1220803, 1],
			"":	     [1191819, 1],
			"LOCATIONSAVEDAS_1":	     [1220104, 1],
			"LOCATIONSAVEDAS_2":	     [1031619, 1],
			"LOCATIONSAVEDAS_3":	     [1220122, 1],
			"LOCATIONSAVEDAS_4":	     [1222016, 1],
			#"NO_ASSIGNED_ANIMATION":	[2051907, 0],
			#"ANIMATION_HAS_NO_KEYFRAMES":	[2051919, 0],
			"LOOP_STARTED_BACKANDFORTH":	[2191608, 0],
			"LOOP_STOPPED":	[2191319, 0],
			"TRIGGER_MODE_2":	[2190303, 0],
			"TRIGGER_MODE_3":	[2190309, 0],
			"TRIGGER_MODE_4":	[2190318, 0],
			"TRIGGER_MODE_5":	[2190308, 0],
			"TRIGGER_MODE_6":	[2190703, 0],
			"TRIGGER_MODE_1":	[2020903, 0],
			"TRIGGER_SET":	[2020913, 0],
			"PRESET_MODE_2":	[2020919, 0],
			"PRESET_MODE_1":	[2021322, 0],
			"PRESET_CHOOSE":	[2020419, 0],
			"PRESET_SET":	[2021403, 0],
			"PRESET_CLEARED":	[2020719, 0],
			"TRIGGER_CLEARED":	[2021613, 0]
			}

		self.kits = {}
		self.kits[4] = ["US_Specops",		"US_Sniper",	"US_Assault",	"US_Support",	"US_Engineer",		"US_Medic",		"US_AT"]
		self.kits[5] = ["MEC_Specops",	"MEC_Sniper",	"MEC_Assault",	"MEC_Support",	"MEC_Engineer",	"MEC_Medic",	"MEC_AT"]
		self.kits[6] = ["CH_Specops",		"CH_Sniper",	"CH_Assault",	"CH_Support",	"CH_Engineer",		"CH_Medic",		"CH_AT"]

	def loadGameSettings(self, file="/settings/sandbox/game.ini"):
		try:
			config = ConfigParser.ConfigParser()
			config.read(host.sgl_getModDirectory() + str(file))
		except: ExceptionOutput()

		# [objectlimit]
		self.disconnectTime = 300
		try: self.spawnDelay = int(config.get("objectlimit","disconnecttime"))
		except: ExceptionOutput()

		# [antispam]
		self.spawnDelay = 20
		try: self.spawnDelay = int(config.get("antispam","spawndelay"))
		except: ExceptionOutput()
		self.vehiclespawnDelay = 120
		try: self.vehiclespawnDelay = int(config.get("antispam","vehiclespawndelay"))
		except: ExceptionOutput()

		# [grouping]
		self.groupDupeDelay = 30
		try: self.groupDupeDelay = int(config.get("groups","dupedelay"))
		except: ExceptionOutput()
		self.groupObjectLimit = 300
		try: self.groupObjectLimit = int(config.get("groups","objectlimit"))
		except: ExceptionOutput()
		self.groupDupeLimit = 100
		try: self.groupDupeLimit = int(config.get("groups","duplicatelimit"))
		except: ExceptionOutput()
		self.groupLoadLimit = 130
		try: self.groupLoadLimit = int(config.get("groups","loadlimit"))
		except: ExceptionOutput()

		# [hitpoints]
		hpZombie = 500000
		hpConstruction = 500000
		hpCombat = 100
		try:
			hpZombie = int(config.get("hitpoints","zombie"))
			hpConstruction = int(config.get("hitpoints","construction"))
			hpCombat = int(config.get("hitpoints","combat"))
			if hpZombie > 999999999: hpZombie = 999999999
			if hpConstruction > 999999999: hpConstruction = 999999999
			if hpCombat > 999999999: hpCombat = 999999999
		except: ExceptionOutput()
		try:
			host.rcon_invoke("objecttemplate.active meinsurgent_heavy_soldier")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpZombie))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpZombie))
			host.rcon_invoke("objecttemplate.active meinsurgent_heavy_soldier_3p")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpZombie))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpZombie))
			host.rcon_invoke("objecttemplate.active meinsurgent_soldier_jet")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpConstruction))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpConstruction))
			host.rcon_invoke("objecttemplate.active meinsurgent_soldier_jet_3p")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpConstruction))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpConstruction))
			host.rcon_invoke("objecttemplate.active us_light_soldier")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpCombat))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpCombat))
			host.rcon_invoke("objecttemplate.active ch_heavy_soldier")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpCombat))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpCombat))
			host.rcon_invoke("objecttemplate.active mec_heavy_soldier")
			host.rcon_invoke("objecttemplate.armor.maxhitpoints " + str(hpCombat))
			host.rcon_invoke("objecttemplate.armor.hitpoints " + str(hpCombat))
		except: ExceptionOutput()

		# [engine]
		self.gravity = -15
		try: self.gravity = int(config.get("engine","gravity"))
		except: ExceptionOutput()
		try: host.rcon_invoke("physics.gravity " + str(self.gravity))
		except: ExceptionOutput()

	def loadAddonSettings(self, file="/settings/sandbox/addons.ini"):
		try:
			config = ConfigParser.ConfigParser()
			config.read(host.sgl_getModDirectory() + str(file))
		except: ExceptionOutput()
		self.addons = []
		try: self.addons = str(config.get("addons","addons")).split(",")
		except: ExceptionOutput()

	def loadUsers(self, file="/settings/sandbox/users.ini"):
		self.users = {}
		f = open(host.sgl_getModDirectory() + str(file),'r')
		for line in f:
			try:
				line = line.replace("\n","")
				line = line.replace("\r","")
				if len(line) == 0: continue
				if line[0] == "#": continue
				u = line.split(";")
				if len(u) != 4: continue
				self.users[u[0]] = {}
				self.users[u[0]]["level"] = int(u[1])
				self.users[u[0]]["password"] = u[2]
				self.users[u[0]]["hash"] = u[3]
			except:
				ExceptionOutput()
		f.close()
		return self.users

	def loadPermissions(self, file="/settings/sandbox/permissions.ini"):
		try:
			config = ConfigParser.ConfigParser()
			config.read(host.sgl_getModDirectory() + str(file))
		except: ExceptionOutput()
		self.permissions = {}
		for cat in ["chat","rcon","objects","misc"]:
			self.permissions[cat] = {}
			if not config.has_section(cat): continue
			for i in config.items(cat):
				try: self.permissions[cat][i[0]] = int(i[1])
				except: ExceptionOutput()
		if not self.permissions["misc"].has_key("grablocked"):
			self.permissions["misc"]["grablocked"] = 21
		return self.permissions

	def checkPermission(self, p, cat, command):
		command = command.lower()
		if self.permissions.has_key(cat):
			if self.permissions[cat].has_key(command):
				if p.level >= self.permissions[cat][command]:
					return True
				else:
					return False
		return True