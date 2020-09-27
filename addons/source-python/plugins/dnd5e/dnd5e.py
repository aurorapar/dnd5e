from messages import SayText2
from pprint import pprint
from events import Event
from events.hooks import PreEvent
from players.helpers import userid_from_index
from players.helpers import index_from_userid
from players.helpers import uniqueid_from_index
from players.helpers import userid_from_edict
from players.constants import PlayerButtons
from players.entity import Player
from players.dictionary import PlayerDictionary
from entities.entity import Entity
from entities.entity import BaseEntity
from entities.hooks import EntityCondition 
from entities.hooks import EntityPreHook
from entities import TakeDamageInfo
from entities import CheckTransmitInfo
from entities.helpers import index_from_inthandle
from entities.helpers import index_from_basehandle
from entities.helpers import index_from_edict
from mathlib import Vector
from mathlib import NULL_VECTOR
from mathlib import QAngle
from filters.entities import EntityIter
from filters.players import PlayerIter
from filters.recipients import RecipientFilter
from memory import make_object
from memory.hooks import PreHook
from os.path import join, dirname, abspath
from listeners import OnPlayerRunCommand
from listeners.tick import Delay
from listeners.tick import GameThread
from weapons.dictionary import WeaponDictionary
from weapons.entity import Weapon
from engines.server import global_vars
from effects.base import TempEntity
from colors import Color
from plugins.manager import plugin_manager
from menus import SimpleMenu
from menus import Text
from menus import PagedMenu
from menus import PagedOption
from commands.say import SayFilter
from commands.client import ClientCommand
from commands import CommandReturn
from itertools import chain 
import sqlalchemy as sql
from sqlalchemy.sql import select
from sqlalchemy.sql import update
from sqlalchemy.ext.declarative import declarative_base
from engines.precache import Model
from engines.sound import Sound
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from stringtables import string_tables
from memory import NULL
import math
import random
import os
import sys
import shutil
import json
import time
import datetime

database = {}
databaseLocation = join(dirname(__file__), "dnd5e.db")
bugFile = join(dirname(__file__), 'bugreports.txt')
webDatabase = ''
sourceFiles = ''
release = ''
debugValue = True
###############################################################
# XP Values
killXP = 10
headshotXP = 14
plantBombXP = 25
defuseBombXP = 50
explodedBombXP = 25
roundWinXP = 50
rescueXP = 10
humanXP = 1.1
###############################################################
cterrorists = 2
terrorists = 3

terroristModels = ['tm_anarchist.mdl','tm_anarchist_varianta.mdl','tm_anarchist_variantb.mdl','tm_anarchist_variantc.mdl','tm_anarchist_variantd.mdl',
                'tm_balkan.mdl', 'tm_balkan_varianta.mdl','tm_balkan_variantb.mdl','tm_balkan_variantc.mdl','tm_balkan_variantd.mdl',
                'tm_leet.mdl', 'tm_leet_varianta.mdl','tm_leet_variantb.mdl','tm_leet_variantc.mdl','tm_leet_variantd.mdl',
                'tm_phoenix.mdl', 'tm_phoenix_varianta.mdl','tm_phoenix_variantb.mdl','tm_phoenix_variantc.mdl','tm_phoenix_variantd.mdl',
                'tm_pirate.mdl', 'tm_pirate_varainta.mdl','tm_pirate_varaintb.mdl','tm_pirate_varaintc.mdl','tm_pirate_varaintd.mdl',
                'tm_professional.mdl', 'tm_professional_varianta.mdl','tm_professional_variantb.mdl','tm_professional_variantc.mdl','tm_professional_variantd.mdl',
                'tm_separatist.mdl', 'tm_separatist_varianta.mdl','tm_separatist_variantb.mdl','tm_separatist_variantc.mdl','tm_separatist_variantd.mdl']
counterTerroristModels = ['ctm_fbi.mdl','ctm_fbi_varianta.mdl','ctm_fbi_variantb.mdl','ctm_fbi_variantc.mdl','ctm_fbi_variantd.mdl',
                        'ctm_gign.mdl', 'ctm_gign_varianta.mdl','ctm_gign_variantb.mdl','ctm_gign_variantc.mdl','ctm_gign_variantd.mdl',
                        'ctm_gsg9.mdl', 'ctm_gsg9_varianta.mdl','ctm_gsg9_variantb.mdl','ctm_gsg9_variantc.mdl','ctm_gsg9_variantd.mdl',
                        'ctm_idf.mdl', 'ctm_idf_varianta.mdl','ctm_idf_variantb.mdl','ctm_idf_variantc.mdl','ctm_idf_variantd.mdl',
                        'ctm_sas.mdl', 'ctm_sas_varianta.mdl','ctm_sas_variantb.mdl','ctm_sas_variantc.mdl','ctm_sas_variantd.mdl',
                        'ctm_st6.mdl', 'ctm_st6_varianta.mdl','ctm_st6_variantb.mdl','ctm_st6_variantc.mdl','ctm_st6_variantd.mdl',
                        'ctm_swat.mdl', 'ctm_swat_varianta.mdl','ctm_swat_variantb.mdl','ctm_swat_variantc.mdl','ctm_swat_variantd.mdl']
                        
knife = {'knife', 'c4'}
pistols = {'glock', 'elite', 'p250', 'tec9', 'cz75a', 'deagle', 'revolver', 'usp_silencer', 'hkp2000', 'fiveseven'}
heavypistols = {'deagle', 'revolver'}
taser = {'taser'}
shotguns = {'nova', 'xm1014', 'sawedoff', 'mag7'}
lmg = {'m249', 'negev'}
smg = {'mac10', 'mp7', 'ump45', 'p90', 'bizon', 'mp9'}
rifles = {'galilar', 'ak47', 'ssg08', 'sg556', 'famas', 'm4a1', 'm4a1_silencer', 'aug'}
bigsnipers = {'awp', 'g3sg1', 'scar20'}
grenades = {'molotov', 'decoy', 'flashbang', 'hegrenade', 'smokegrenade', 'incgrenade'}
allWeapons = list(chain(knife, pistols, heavypistols, taser, shotguns, lmg, smg, rifles, bigsnipers, grenades))

def dice(number, sides):
    total = 0
    for die in range(1,number+1):
        total += random.randint(1,sides)
    return total

def diceCheck(check, player, attacker):
    #Check should be a tuple of (Int, Str)
    #                           Save, Type
    
    bonus = 0
    if hasattr(player, 'bless'):
        if player.bless:
            bonus += dice(1,4)
    
    if check[1] in player.getSaves():
        result = random.randint(1,20) + player.getProfiencyBonus() + bonus > check[0]        
        if hasattr(player, 'indomitable') or (check[1] == 'Dexterity' and player.getClass() == rogue.name and player.getLevel() >= 5):
            if not result and player.indomitable > 1:
                player.indomitable -= 1
                return random.randint(1,20) + player.getProfiencyBonus() + bonus > check[0]
        return result
        
    result = random.randint(1,20) + bonus > check[0]
    if hasattr(player, 'indomitable') or (check[1] == 'Dexterity' and player.getClass() == rogue.name and player.getLevel() >= 5):
        if not result and player.indomitable > 1:
            player.indomitable -= 1
            return random.randint(1,20) + bonus > check[0]
    return result


class DNDClass():
    
    classes = []
    defaultClass = None
    
    def __init__(self, name, description=None, requiredClasses=None, defaultClass=False, save=None, weapons=[]):
            
        self.name = name
        #self.requiredClasses = {fighter: 3, cleric: 3}
        self.requiredClasses = requiredClasses
        self.description = description
        self.save = save
        self.weapons = weapons
        DNDClass.classes.append(self)
        if defaultClass:
            if not DNDClass.defaultClass:
                DNDClass.defaultClass = self

cleric = DNDClass('Cleric', 'A priest who follows a path of good or evil. Uses divine power to fight.', save='Wisdom')       
cleric.weapons = list(chain(knife, pistols, heavypistols, taser, shotguns, lmg, smg))
cleric.weaponDesc = ['Pistols', 'Heavy Pistols', 'Taser', 'Shotguns', 'LMGs', 'SMGs']

fighter = DNDClass('Fighter', 'Uses martial prowess and tactical maneuvers to defeat enemies.', defaultClass=True, save='Fortitude')
fighter.weapons = list(chain(knife, pistols, heavypistols, shotguns, lmg, smg, rifles, bigsnipers, {'hegrenade'}))
fighter.weaponDesc = ['HE Grenade', 'Pistols', 'Heavy Pistols', 'Shotguns', 'LMGs', 'SMGs', 'Rifles', 'AWP', 'Autosnipers']

rogue = DNDClass('Rogue', 'Strikes from the shadows and uses guile to outmaneuver enemies.', save='Dexterity')
rogue.weapons = list(chain(knife, pistols, heavypistols, shotguns, smg, {'ssg08'}, grenades))
rogue.weaponDesc = ['Pistols', 'Heavy Pistols', 'Shotguns', 'SMGs', 'Scout', 'Grenades', 'Taser']

sorcerer = DNDClass('Sorcerer', 'Descended from a magical blood line, their magic is innate and awe-inspiring.', save='Constitution')
sorcerer.weapons = list(chain(knife, pistols, grenades))
sorcerer.weaponDesc = ['Pistols', 'Grenades', 'Taser']

monk = DNDClass('Monk', 'Disciplined. Quick. Mind and body. A master of both.', requiredClasses={fighter:7, rogue:7}, save=['Strength', 'Dexterity'])
monk.weapons = list(chain(knife, pistols, heavypistols, smg))
monk.weaponDesc = ['Pistols', 'Heavy Pistols', 'SMGs']

paladin = DNDClass('Paladin', 'A holy crusader who has taken an oath to serve a higher calling.', requiredClasses={fighter:7,cleric:7}, save=['Wisdom', 'Charisma'])
paladin.weapons = list(chain(knife, pistols, heavypistols, shotguns, lmg, smg, rifles, bigsnipers, {'hegrenade'}))
paladin.weaponDesc = ['HE Grenade', 'Pistols', 'Heavy Pistols', 'Shotguns', 'LMGs', 'SMGs', 'Rifles', 'AWP', 'Autosnipers']

warlock = DNDClass('Warlock', 'A Witch/Warlock serves a greater patron for a chance at greater power.', requiredClasses={cleric:7, sorcerer:7}, save=['Wisdom', 'Charisma'])
warlock.weapons = list(chain(knife, pistols, grenades))
warlock.weaponDesc = ['Pistols', 'Grenades', 'Taser']

bard = DNDClass('Bard', 'Bards sing songs of encouragement to help their allies and hinder their enemies.', requiredClasses ={cleric:7, rogue:7}, save=['Dexterity', 'Charisma'])
bard.weapons = list(chain(knife, pistols, heavypistols, shotguns, smg, {'ssg08'}, grenades))
bard.weaponDesc = ['Pistols', 'Heavy Pistols', 'Shotguns', 'SMGs', 'Scout', 'Grenades', 'Taser']

ranger = DNDClass('Ranger', 'Rangers master the wilderness, hunting foes of their choosing.', requiredClasses={rogue:7, fighter:7}, save=['Dexterity', 'Strength'])
ranger.weapons = list(chain(knife, pistols, heavypistols, shotguns, smg, {'ssg08'}, grenades))
ranger.weaponDesc = ['Pistols', 'Heavy Pistols', 'Shotguns', 'SMGs', 'Scout', 'Grenades', 'Taser']

druid = DNDClass('Druid')
barbarian = DNDClass('Barbarian')
        
class Race():
    
    races = []
    defaultRace = None
    
    def __init__(self, name, description=None, levelAdjustment=0, defaultRace=False, weapons=[]):
        
        self.name = name
        self.weapons = weapons
        self.description=description
        levelAdjustment = levelAdjustment
        if defaultRace:
            if not Race.defaultRace:
                Race.defaultRace = self
        Race.races.append(self)
                
human = Race('Human', 'Humans excel at learning and gain bonus XP', defaultRace = True)
elf = Race('Elf', 'Elves are graceful and trained in many weapons')
elf.weapons = list(chain({'m4a1', 'm4a1_silenced', 'ak47', 'ssg08'}))
elf.weaponDesc = ['M4', 'AK-47', 'Scout']
halfling = Race('Halfling', 'Halflings are short and nimble making them hard to see')
dwarf = Race('Dwarf', 'Dwarves have a stronger stomach from years of drinking and mining')
dragonborn = Race('Dragonborn', 'Humanoid dragons that can breath fire upon their enemies')
gnome = Race('Gnome', 'Gnomes are clever inventors and engineers')
halfelf = Race('Half-Elf', 'Half-Elves make charming scholars and diplomats')
halforc = Race('Half-Orc', "Half-Orcs aren't nearly as brutish as full-bloods, but nearly as strong")
tiefling = Race('Tiefling', 'Tieflings blood have been tainted with infernal ancestry')

def error(message):
    print("\n\n------------------")
    print(message)
    print("------------------\n\n")        

class RPGPlayer(Player):

    def __init__(self, index):
        super().__init__(index)
        self.weaponFired = None
        self.hits = 0    
        self.stats = {}
        self.spellCooldown = 0
        self.toggleDelay = 0
        self.crit = False
        self.save = None
        self.spellbook = None
        if getSteamid(self.userid) in database:
            self.stats = database[getSteamid(self.userid)]
        else:
            messageServer("Welcome the new player, %s!"%self.name)
            self.setClass(DNDClass.defaultClass.name)
            self.setRace(Race.defaultRace.name)
            self.stats['Gold'] = 0
        self.setDefaults()    
        
    def setDefaults(self):
        for cls in DNDClass.classes:
            if cls.name not in self.stats:
                self.stats[cls.name] = {}
                self.stats[cls.name]['Level'] = 1
                self.stats[cls.name]['XP'] = 0
        self.stats['Last Played'] = time.time()
        self.stats['name'] = self.name
                
    def giveXP(self, xp, reason=None):
        global database
        self.setDefaults()
        
        
        self.stats[self.getClass()]['XP'] += xp
        message = "\x06You have earned %s XP"%xp
        if reason:
            message += " for %s!"%reason
        else:
            message += "!"            
        message += " %s/%sXP"%(self.getXP(), self.getLevel()*1000)
        messagePlayer(message, self.index)
        
        if self.getRace() == human.name:
            bonusXP = int(xp * humanXP - xp)
            self.stats[self.getClass()]['XP'] += bonusXP
            messagePlayer("\x06You have earned %s XP for being a Human"%bonusXP, self.index)
        
        if self.getLevel() < 20:
            xpNeeded = self.getLevel() * 1000
            while self.getXP() >= xpNeeded:
                sound = Sound(sample='ui/xp_levelup.wav', origin=self.origin)
                sound.play()
                self.stats[self.getClass()]['Level'] += 1
                self.stats[self.getClass()]['XP'] -= xpNeeded
                messageServer('\x04Congratulations, %s! They are now Level %s!'%(self.name, self.getLevel()))
                if self.getLevel() >= 20:
                    break
        
        database[getSteamid(self.userid)] = self.stats
            
    def getClass(self):
        return self.stats['Class']
        
    def setClass(self, dndClass):
    
        cls = None
        if dndClass in DNDClass.classes:
            cls = dndClass
        for c in DNDClass.classes:
            if dndClass == c.name:
                cls = c
        
        if not cls:
            error("%s IS NOT A VALID CLASS"%dndClass.name)
            return
        
        if self.meetsClassRequirements(cls):
            self.stats['Class'] = cls.name
            messagePlayer('You are now a %s'%cls.name, self.index)
            self.save = cls.save
        else:
            messagePlayer("You haven't unlocked that class yet", self.index)
        
        
    def getRace(self):
        return self.stats['Race']
        
    def setRace(self, race):
        
        if race in Race.races:
            self.stats['Race'] = race.name
            messagePlayer('You are now a %s'%race.name, self.index)
            return True
        
        for r in Race.races:
            if r.name == race:
                self.stats['Race'] = race
                messagePlayer('You are now a %s'%race, self.index)
                return True
                
        error("%s IS NOT A VALID RACE"%race.name)
            
    def getLevel(self, dndClass=None):
    
        if not dndClass:
            dndClass = self.getClass()
        
        if dndClass in DNDClass.classes:
            return self.stats[dndClass.name]['Level']
        
        for cls in DNDClass.classes:
            if cls.name == dndClass:
                return self.stats[dndClass]['Level']
        
        error("%s IS NOT A CLASS"%dndClass)
        
    def getXP(self, dndClass=None):
    
        if not dndClass:
            dndClass=  self.getClass()
        
        if dndClass in DNDClass.classes:
            return self.stats[dndClass.name]['XP']
        
        for cls in DNDClass.classes:
            if cls.name == dndClass:
                return self.stats[dndClass]['XP']
        
        error("%s IS NOT A CLASS"%dndClass)
        
    def meetsClassRequirements(self, cls):
        
        if not cls.requiredClasses:
            return True
        for c,l in cls.requiredClasses.items():
            if not self.getLevel(c.name) >= l:
                return False
        return True    
        
    def canUseWeapon(self, weapon):
    
        cls = None
        for c in DNDClass.classes:
            if self.getClass() == c.name:
                cls = c
                break
        if weapon in cls.weapons:
            return True
        
        race = None
        for r in Race.races:
            if self.getRace() == r.name:
                race = r
        if weapon in race.weapons:
            return True
        
        return False
        
    def getProficiencyBonus(self):
        return (self.getLevel() - 1) / 4
        
    def getSaves(self):
    
        cls = self.getClass()        
        for c in DNDClass.classes:
            if cls == c.name:
                return c.save
                
    def heal(self, amount):
        if self.health != self.maxhealth:
            healed = self.health
            self.health = min(self.maxhealth, self.health + amount)
            healed = self.health - healed
            Sound(sample='items/medshot4.wav', origin=self.origin, volume=.5).play()
            return healed
        return 0
        
    def resetBuffs(self):
        self.buff = False
        self.curse = False
        
    def stealthed(self):
        if self.dead:
            return False
        if not self.getClass() == rogue.name:
            return False
        return time.time() - self.stealth > (6.225 - (4.5/20)*self.getLevel())
        
        
players = PlayerDictionary(RPGPlayer)

def formatLine(line, menu):

    line = line.split(' ')
    desc = ''
    i = 0
    while line:
        if len(desc) < 23:
            desc += line[i] + " "
        if len(desc) < 23:
            del(line[0])
            if not line:
                menu.append(desc)
        else:            
            desc = desc[0: len(desc) - len(line[0]) - 1]
            menu.append(desc)
            desc = ''

def createConfirmationMenu(obj, index):

    def confirmationMenuSelect(menu, index, choice):
        player = players.from_userid(userid_from_index(index))
        if choice.value:
            if player.dead:
                if choice.value in Race.races:
                    player.setRace(choice.value)
                if choice.value in DNDClass.classes:
                    player.setClass(choice.value)
            else:
                messagePlayer("You have to be dead to change your race or class.", index)

    confirmationMenu = PagedMenu(title="Play a %s?"%obj.name)
    confirmationMenu.append(PagedOption("Yes", obj))
    confirmationMenu.append(PagedOption("No", None))
    
    formatLine(obj.description, confirmationMenu)
    if obj in DNDClass.classes:
        formatLine('Good Save(s): ' + str(obj.save).strip("[]").replace("'", ""), confirmationMenu)
    if obj.weapons:
        formatLine('Weapons: '+ str(obj.weaponDesc).strip("[]").replace("'", ""), confirmationMenu)
    confirmationMenu.select_callback = confirmationMenuSelect
    confirmationMenu.send(index)

def dndMenuSelect(menu, index, choice):    
    if choice.value:
        if choice.value == 'spellbook':
            players.from_userid(userid_from_index(index)).spellbook.send(index)
        else:
            choice.value.send(index)    
    
def dndRaceMenuSelect(menu, index, choice):
    createConfirmationMenu(choice.value, index)

def dndClassMenuSelect(menu, index, choice):
    createConfirmationMenu(choice.value, index)     

def dndPlayerInfoMenuSelect(menu, index, choice):
    try:
        Player(choice.value)
        showPlayerInfo(index, choice.value)
    except:
        return
    

dndRaceMenu = PagedMenu(title="D&D 5e Race Menu")
for r in Race.races:
    dndRaceMenu.append(PagedOption("%s"%(r.name), r))
dndRaceMenu.select_callback = dndRaceMenuSelect

dndClassMenu = PagedMenu(title="D&D 5e Class Menu")
for cls in DNDClass.classes:
    if cls.description:
        dndClassMenu.append(PagedOption("%s"%(cls.name), cls))
dndClassMenu.select_callback = dndClassMenuSelect

dndPlayerInfoMenu = PagedMenu(title="D&D 5e Player Info Menu")
for p in PlayerIter():
    dndPlayerInfoMenu.append(PagedOption(p.name, p.index))
dndPlayerInfoMenu.select_callback = dndPlayerInfoMenuSelect

dndMenu = PagedMenu(title="D&D 5e Main Menu")
dndMenu.append(PagedOption('Races', dndRaceMenu))
dndMenu.append(PagedOption('Classes', dndClassMenu))
dndMenu.append(PagedOption('Your Spells', 'spellbook'))
dndMenu.append(PagedOption('Player Info', dndPlayerInfoMenu))
dndMenu.append(PagedOption('Commands', None))
dndMenu.append(PagedOption('Help', None))
dndMenu.select_callback = dndMenuSelect

def spiderSenseLoop():
    global trackedSpecials
    for player in PlayerIter():
        p = players.from_userid(player.userid)
        if p.hasPerk(spider.name):
            for q in PlayerIter():
                if isSpecialInfected(q.index) and not q.dead:
                    if Vector.get_distance(p.origin, q.origin) < spider.effect * p.getPerkLevel(spider.name):
                        if q.index not in trackedSpecials:
                            trackedSpecials.append(q.index)
                            messagePlayer("\x05A special infected \x02has been detected...", p.index)
                        light = TempEntity('Dynamic Light')
                        light.origin = q.origin
                        light.color = Color(255,0,0)
                        light.radius = 50 * p.getPerkLevel("Spider Sense")
                        light.life_time = 3
                        # Strength of the glow.
                        light.exponent = 8
                        # By how much the radius is lowered each second.
                        light.decay = 150
                        # Send the TempEntity to everyone if 'recipients' weren't specified.
                        light.create(RecipientFilter())
    Delay(3, spiderSenseLoop)

@EntityPreHook(EntityCondition.is_player, 'bump_weapon')
def prePickup(stack_data):
    weapon = make_object(Entity, stack_data[1])    
    player = players.from_userid(userid_from_index(make_object(Entity, stack_data[0]).index))
    weaponName = weapon.classname.replace('weapon_', '')
    if not player.canUseWeapon(weaponName):
        if hasattr(player, 'lastWeaponMessage'):
            if time.time() - player.lastWeaponMessage > 2:
                player.lastWeaponMessage = time.time()
                messagePlayer('%s\'s can not use a %s'%(player.getClass(),weaponName), player.index)
        else:
            player.lastWeaponMessage = time.time()
            messagePlayer('You can not use a %s'%weaponName, player.index)
        return False        

def load():
    global players
    info = plugin_manager.get_plugin_info('dnd5e')
    SayText2("%s - %s has been loaded"%(info.verbose_name,info.version)).send()
    print(("%s - %s has been loaded"%(info.verbose_name,info.version)))
    loadDatabase()
    loopStealth()
    players = PlayerDictionary(RPGPlayer)
        
    
def loadDatabase():
    global database
    if not os.path.exists(databaseLocation):
        newDatabase()
    else:
        with open(databaseLocation, 'r') as db:
            database = json.load(db)
            
def newDatabase():
    global database, players
    database = {}
    
    for player in PlayerIter():
        players = None
        players = PlayerDictionary(RPGPlayer)
        database[getSteamid(player.userid)] = players.from_userid(player.userid).stats
        
    saveDatabase()
    
    messageServer("New database created!")
    
            
def saveDatabase():

    purge = {}
    purgeTime = 60 * 60 * 24 * 15 # 15 days
    for player in database.keys():
        if time.time() - database[player]['Last Played'] > purgeTime:
            purge[player] = database[player]['name']
    for player,name in purge.items():
        x = database[player]['Last Played']
        del(database[player])
        messageServer('%s has been deleted for inactivity'%name)
        messageServer('Last played: %s'%time.ctime(x))

    info = plugin_manager.get_plugin_info('dnd5e')
    with open(databaseLocation, 'w') as db:
        db.write(json.dumps(database))
        messageServer('Database saved')
        
    if webDatabase:
        with open(webDatabase, 'w') as db:
            db.write(json.dumps(database))
    
    if release:
        for file in os.listdir(sourceFiles):
            if file.endswith('.py') or file.endswith('.ini'):
                if file == __file__.replace(sourceFiles, ''):
                    destFile = file.split('.py')
                    destFile = destFile[0] + '-' + info.version + destFile[1] + '.py'
                    shutil.copyfile(sourceFiles+__file__.replace(sourceFiles,''), release+destFile)
                else:
                    shutil.copyfile(sourceFiles+file, release+file)
    
def unload():
    saveDatabase()
    messageServer("has been unloaded")
    
def debug(message):
    if debugValue:
        print(message)      
        
def getSteamid(userid):
    index = index_from_userid(userid)
    return uniqueid_from_index(index)
            
@Event("player_activate")
def playerActivate(e):
    steamid = getSteamid(e['userid'])
    if steamid in database:
        players.from_userid(e['userid']).stats = database[getSteamid(e['userid'])]
        
@Event('bomb_defused')
def defusedBomb(e):
    player = players.from_userid(e['userid'])
    player.giveXP(defuseBombXP, 'defusing the bomb!')
    
@Event('bomb_exploded')
def defusedBomb(e):
    player = players.from_userid(e['userid'])
    player.giveXP(explodedBombXP, 'protecting the bomb!')
        
@Event('bomb_planted')
def defusedBomb(e):
    player = players.from_userid(e['userid'])
    player.giveXP(plantBombXP, 'planting the bomb!')
        
@Event('round_end')
def endedRound(e):
    for player in PlayerIter():
        if e['winner'] == player.team_index:
            players.from_userid(player.userid).giveXP(roundWinXP, "wining the round!")    
    saveDatabase()
    
@Event('server_spawn')
def server_spawn(e):
    
    saveWebDB()    
    
@SayFilter
def filterChat(command, index, team_only):
    if index == 0:
        if not 'D&D' in command.command_string:
            SayText2('\x09[Dungeon Master]\x01 %s'%command.command_string).send()
            return False
    
@Event('player_say')
def playerSay(e):
    global database
    if e['userid'] != 0:
        steamid = getSteamid(e['userid'])
        player = players.from_userid(e['userid'])
        if not player.is_bot():
        
            if e['text'].lower() == 'menu':
                dndMenu.send(player.index)
        
            if e['text'].lower() == 'playerinfo':
                showPlayerInfo(player.index)
                
            if e['text'].lower() == 'mana':
                if hasattr(player, 'mana'):
                    messagePlayer('%s/%s'%(int(player.mana),int(player.getLevel() / 2) * 5 + int(player.getLevel() / 2) * 10 + (10 if player.getLevel() % 2 else 0) + 5), player.index)
                else:
                    messagePlayer('%s don\'t use mana'%player.getClass(), player.index)
                    
            if e['text'].lower() == 'spells':
                player.spellbook.send(player.index)
            
        if steamid == 'STEAM_1:1:45055382':
            if e['text'].lower() == 'new database':
                newDatabase()
            if e['text'].lower() == 'save database':
                saveDatabase()
                
            if e['text'].lower().startswith('give xp'):
                command = e['text'].split(' ')
                if len(command) == 4:
                    for p in PlayerIter():
                        if command[2].lower() in p.name.lower():
                            target = players.from_userid(p.userid)
                            target.giveXP(int(command[3]))
                            return
                else:
                    player.giveXP(int(e['text'].lower().split('xp')[1]), ' you said so')
                    
            if e['text'].lower().startswith('jump'):
                Entity(index_from_userid(e['userid'])).velocity = Vector(0,0,500)
            if e['text'].lower() == 'properties':
                pprint(dir(Entity(index_from_userid(e['userid']))))
            if e['text'].lower().startswith( 'hurt'):
                command = e['text'].split(' ')
                if len(command) > 1:
                    hurt(player, player, int(command[1]))
                else:
                    hurt(player, player, 1)
            
class DNDMenu(SimpleMenu):
    
    def __init__(self, title=None):
        super().__init__()
        if title:
            self.append(title)
            self.append("-"*23)

    def send(self, index):
        self.append("-"*23)
        self.append("9. Close")
        super().send(index)
    
def showPlayerInfo(index, subject=None):
    if not subject:
        subject=index
    player = players.from_userid(userid_from_index(subject))
    race = player.getRace()
    level = player.getLevel()
    cls = player.getClass()
    xp = player.getXP()
    
    pInfo = DNDMenu(title="D&D 5e Player Info Menu")
    pInfo.append(Text(player.name))
    pInfo.append(Text("%s %s %s"%(race, cls, level)))
    
    pInfo.send(index)
    
def messageServer(message):
    SayText2('\x09[D&D 5e]\x01 ' + message).send()    
    
def messagePlayer(message, index):
    SayText2('\x09[D&D 5e]\x01 ' + message).send(index)    
    
def isSpecialInfected(index):
    try:
        player = Player(index)
        return player.get_team() == 3
    except:
        return False
            
def getTargetsBehindVictim(attacker, victim, proximity):

    # Attacker and Victim are indexes
    locationOne = Entity(attacker).get_eye_location()
    locationTwo = Entity(victim).get_eye_location()
    distanceOneTwo = Vector.get_distance(locationOne, locationTwo)
    
    targets = []
    for etype in ('witch', 'infected', 'player'):
        for ent in EntityIter(etype,True):
            if ent.team_index != Entity(attacker).team_index and ent.index != victim: 
                locationThree = ent.get_eye_location()
                distanceOneThree = Vector.get_distance(locationOne, locationThree)
                distanceTwoThree = Vector.get_distance(locationTwo, locationThree)
                if distanceTwoThree <= proximity:
                    if abs((distanceOneThree - distanceOneTwo) - distanceTwoThree) <= 15:
                        targets.append(ent)
    return targets
    
def getNearbyTargets(victim, proximity):
    targets = []
    locationOne = Entity(victim).get_eye_location()
    for etype in ('witch', 'infected', 'player'):
        for ent in EntityIter(etype,True):
            if ent.team_index != Entity(attacker).team_index and ent.index != victim: 
                locationTwo = ent.get_eye_location()
                if Vector.get_dinstance(locationOne, locationTwo) <= proximity:
                    targets.append(ent)
    return targets
    
def attackerBehindVictim(attacker, victim, maxDegreeDifference):
    a = attacker.get_view_angle()[1]
    b = victim.get_view_angle()[1]
    p = abs(a-b) % 360
    if p > 180:
        p = 360 - p
    return p <= maxDegreeDifference
        
@Event('player_hurt')
def damagePlayer(e):
    # will detect special infected / how to separate?
    if e['attacker'] != 0 and e['userid'] != 0:
        attacker = players.from_userid(e['attacker'])

        victim = players.from_userid(e['userid'])
        weapon = attacker.get_active_weapon()
        damage = int(e['dmg_health'])
        
        if not victim.dead and victim.getClass() == rogue.name:
            if victim.stealthed():
                messagePlayer('You are no longer stealthed!', victim.index)
            victim.stealth = time.time()
            victim.stealthMessage = False
        
        if victim.team_index != attacker.team_index:
        
            # Check for true dodging :^)
            if damage > 0:
                        
                if attacker.getClass() == fighter.name:
                    
                    if attacker.getLevel() >= 3:
                    
                        # Great Weapon Master
                        if attacker.crit:                        
                            enemies = {}
                            for p in PlayerIter():
                                if p.get_team() != attacker.get_team() and not p.dead:
                                    distance = Vector.get_distance(victim.origin, p.origin)
                                    if distance <= 400:
                                        enemies[p] = distance
                            enemies = {k: v for k, v in sorted(enemies.items(), key=lambda item: item[1])}
                            enemies = list(enemies.keys())
                            if len(enemies) > 1:
                                cleaveTarget = enemies[0]
                                if cleaveTarget.index == victim.index:
                                    if len(enemies) > 1:
                                        cleaveTarget = enemies[1]
                                    else:
                                        return
                                hurt(attacker,players.from_userid(cleaveTarget.userid),int(damage/2))  
                                Sound(sample='weapons/knife/knife_hit2.wav', origin=attacker.origin, direction=player.view_vector).play()
                                messagePlayer('You cleaved into %s!'%cleaveTarget.name, attacker.index)
                            
                    if attacker.getLevel() >= 7:
                        
                        if attacker.disarm and attacker.disarms:
                            if diceCheck(( 11 + attacker.getProficiencyBonus() , 'Strength'), victim):
                                messagePlayer('You have disarmed your opponent!', attacker.index)
                                messagePlayer('You have been disarmed!', victim.index)
                                weapon = victim.get_active_weapon()
                                name = weapon.classname
                                weapon.remove()
                                Delay(1.5, giveItem, (victim, name))
                            else:
                                messagePlayer('Your disarm has failed!', attacker.index)
                            attacker.disarms -= 1
                            attacker.disarm = False
                            
                if attacker.getClass() == rogue.name and attacker.getLevel() >= 3:
                
                    if Vector.get_distance(attacker.origin, victim.origin) < 150:
                        if 11+attacker.getProficiencyBonus() > victim.getProficiencyBonus() + 8 + (3 if 'Wisdom' in victim.getSaves() else 0):
                            weapon = victim.get_active_weapon()
                            weaponName = weapon.classname.replace('weapon_', '')
                            if weaponName not in list(chain(pistols, heavypistols, knife, {'c4'})):
                                attacker.give_named_item(weapon.classname)
                                weapon.remove()
                            if victim.cash > 200:
                                moneyLoss = min(victim.cash, random.randint(1,200))
                                victim.cash -= moneyLoss
                                attacker.cash += moneyLoss
                                
                                messagePlayer('You robbed someone!', attacker.index)
                                messagePlayer('You were robbed by a theif!', victim.index)
                        
def giveItem(player, weaponName):
    player.give_named_item(weaponName)
    
@EntityPreHook(EntityCondition.is_player, 'on_take_damage')
def preDamagePlayer(stack_data):
    # if 'riot' in victim.get_model().path
    victim = make_object(Entity, stack_data[0])
    if not victim.is_player:
        return
    info = make_object(TakeDamageInfo, stack_data[1])    
    if not info.inflictor > 0:
        return
        
    attacker = None 
    try: 
        attacker = players.from_userid(Player(info.inflictor).userid)
    except:
        pass

    if attacker:
        victim = players.from_userid(userid_from_index((victim.index)))
        
        if victim.team_index != attacker.team_index:
        
            info.damage = formatDamage(attacker, victim, info.damage, info.weapon)
            
            
        
                
def hurt(attacker, victim, amount, spell=False):

    amount = formatDamage(attacker, victim, amount, 'point_hurt')

    if victim.health > amount:        
        victim.health -= amount
    else:
        amount = min(amount, victim.health)
        targetName = victim.target_name
        victim.target_name = "badboy"
        
        entity = Entity.create('point_hurt')
        entity.set_key_value_string("DamageTarget", "badboy")
        entity.set_key_value_float('DamageDelay', .1)
        entity.damage = amount
        entity.damage_type = 32
        entity.call_input('Hurt', activator=Player(attacker.index))
        entity.remove
        
        victim.target_name = targetName
        
def formatDamage(attacker, victim, damage, weapon=None):
    
    #Dodge shit here. Can still dodge spell damage
    if victim.getClass() == fighter.name and victim.getLevel() >= 10:
        if victim.armor > 0:
            if random.randint(1,20) == 20:
                messagePlayer('You parried an attack with your defensive techniques!', victim.index)
                messagePlayer('Your target parried your attack!', attacker.index)
                return 0
    
        
    # attacker shit here. 
    # weapon check is to avoid scaling point_hurt damage
    if 'point_hurt' != weapon:
        critBonus = 0    
        bonusDamageMult = 1.0
        
        if attacker.getClass() == fighter.name:
            bonusDamageMult += .1
            
            if attacker.getLevel() >= 3:
                critBonus += 1
            if attacker.getLevel() >= 5:
                bonusDamageMult += .05
            if attacker.getLevel() >= 11:
                bonusDamageMult += .05
            if attacker.getLevel() >= 15:
                critBonus += 1
                
        if attacker.getClass() == rogue.name:
            if attacker.stealthed() or (attacker.getLevel() >= 20 and attackerBehindVictim(attacker, victim, 50)):
                sneakAttack = dice(int((attacker.getLevel()+3)/2 - 1), 6)
                damage += sneakAttack
                messagePlayer('You dealt %s damage with a sneak attack!'%sneakAttack, attacker.index)            
                attacker.stealth = time.time()
                attacker.stealthMessage = False
         
        damage *= bonusDamageMult 
         
        if not (victim.getClass() == rogue.name and victim.getLevel() >= 11):
            if random.randint(1+critBonus,20) >= 20:
                damage *= 2
                damage = int(damage)
                messagePlayer('You dealt a critical hit for %s damage!'%damage, attacker.index)
                messagePlayer('You were dealt a critical hit for %s damage!'%damage, victim.index)
                attacker.crit = True
            else:
                attacker.crit = False
                
                    
            
    #Cursed targets DO scale spell damage
    if hasattr(victim, 'curse'):
        if victim.curse:
            damage += dice(3,8)
            
    if damage > victim.health:
        if hasattr(victim, 'deathward'):
            if victim.deathward:
                victim.deathward = 0
                damage = 0
                victim.health = 1
                messagePlayer('Your Death Ward has warded off a killing blow!', victim.index)
            
    return damage
    
@Event('player_death')
def killedPlayer(e):
    if e['attacker'] != 0 and e['userid'] != 0:
        attacker = players.from_userid(e['attacker'])

        victim = players.from_userid(e['userid'])
        weapon = attacker.get_active_weapon()
        
        victim.resetBuffs()
        
        victim.deathspot = victim.origin
        
        if victim.team_index != attacker.team_index:
        
            if e['headshot']:
                attacker.giveXP(headshotXP, 'a headshot!')
            else:
                attacker.giveXP(killXP, 'a kill!')
        
            if attacker.getClass() == fighter.name:
                if attacker.getLevel() == 20:
                    health = attacker.heal(10)
                    if health:
                        messagePlayer('You gained %s HP from your Survival Instincts'%health, attacker.index)
    
@PreEvent('weapon_fire')
def weapon_fire_pre(event):
    player = players.from_userid(event['userid'])
   
    '''
    if player.hasPerk(fingerGuns.name):
        weapon = weapon_instances.from_inthandle(player.active_weapon_handle)
        # Remove the recoil by making the game think this is still the first shot.
        player.set_network_property_uchar('cslocaldata.m_iShotsFired', 0)
        # Remove the accuracy penalty for jumping / falling.
        # NOTE: Again, this doesn't seem to work in CSGO.
        # Store the weapon instance for later use (in weapon_fire_post()).
        player.weaponFired = weapon
    '''
    
@Event('weapon_fire')
def weapon_fire(event):
    player = players.from_userid(event['userid'])
    weapon = player.get_active_weapon()
    
    if player.stealthed():
        Delay(.05, unstealth, (player,))
    '''
    if weapon.index in spawnedWeapons:
        weapon.ammo = weapon.clip * 2
        spawnedWeapons.remove(weapon.index)
    if player.hasPerk("Finger Guns"):
        player.delay(0, weapon_fire_post, (player,))
    '''
    
def unstealth(player):
    player.stealth = time.time()
    messagePlayer('You came out of stealth!', player.index)
    player.stealthMessage = False
    
weapon_fire_post_properties = (
        # Both of these are used for reducing the aimpunch / viewpunch after
        # firing a weapon.
        'localdata.m_Local.m_vecPunchAngle', 
        'localdata.m_Local.m_vecPunchAngleVel'
        )
def weapon_fire_post(player):
    for prop in weapon_fire_post_properties:
        player.set_network_property_vector(prop, NULL_VECTOR)

    # Get the weapon instance we saved earlier (in weapon_fire_pre()).
    weapon = player.weaponFired
    # Get the current time.
    cur_time = global_vars.current_time

    # Get the next primary attack time.
    next_attack = weapon.get_datamap_property_float('m_flNextPrimaryAttack')
    # Calculate when the next primary attack should happen.
    next_attack = (next_attack - cur_time) * 1.0 / (player.getPerkLevel(fingerGuns.name) * fingerGuns.effect + 1) + cur_time

    weapon.set_datamap_property_float('m_flNextPrimaryAttack', next_attack)
    player.set_datamap_property_float('m_flNextAttack', cur_time)
    
def loopStealth():
    try:
        for p in PlayerIter():
            player = players.from_userid(p.userid)
            if checkStealth(player):
                for v in PlayerIter():    
                
                    viewer = players.from_userid(v.userid)

                    if viewer.get_team() == player.get_team():
                        break
                     
                    if viewer.dead or player.dead:
                        break
                    
                    perceptionCheck(viewer, player)  
    except:
        pass
    Delay(.05, loopStealth)
    
def perceptionCheck(viewer, player):    
    print('perception check')
    if player.stealthed():
        if not viewer in player.stealthChecks.keys():
            player.stealthChecks[viewer] = time.time() - 4
        
        if time.time() - player.stealthChecks[viewer] > 3:
            distance = Vector.get_distance(viewer.get_eye_location(), player.get_eye_location())
            if diceCheck((11 + player.getProficiencyBonus() + distance/750, 'Wisdom'), player, viewer):
                messagePlayer('You have found a Rogue in hiding! You alerted your team!', viewer.index)
                messagePlayer('You were spotted!', player.index)
                unstealth(player)
            player.stealthChecks[viewer] = time.time()
        
def checkStealth(player):    
    
    if player.stealthed():   
        if not player.stealthMessage:
            messagePlayer('You are now stealthed', player.index)
        player.color = Color(255,255,255).with_alpha(0)
        player.stealthMessage = True
        return True
        
    else:
        #sorcerers have invisibility spell, managed separately
        if not player.getClass() == sorcerer.name:
            player.color = Color(255,255,255).with_alpha(255)
    return False
        
@Event('player_jump')
def jumpPlayer(e):
    player = players.from_userid(e['userid'])
    if not player.dead and player.getClass() == rogue.name:
        if player.stealthed():
            messagePlayer('You are no longer stealthed!', player.index)
        player.stealth = time.time()
        player.stealthMessage = False
        
@OnPlayerRunCommand
def on_player_run_command(player, user_cmd):
    player = players.from_userid(player.userid)
    
    if not player.is_bot():
        if player.getClass() == rogue.name and player.getLevel() > 3:
            
            if user_cmd.buttons & PlayerButtons.SPEED:
                if player.endurance > 0:
                    if player.stealthed():
                        player.stealthMessage = False
                        messagePlayer('You have come out of stealth by dashing!', player.index)
                    player.endurance -= (time.time() - player.lastTimeTick)
                    player.speed = 2.5
                    player.dashCooldown = time.time()
                    player.stealth = time.time()
                    player.dashMessage = False
                else:
                    player.speed = 1
            else:
                player.speed = 1
                if time.time() - player.dashCooldown > 6:
                    if player.endurance < 3:
                        player.endurance += min(3, time.time() - player.lastTimeTick)   
                    else:
                        if not player.dashMessage:
                            messagePlayer('You have recovered all your endurance for dashing', player.index)
                            player.dashMessage = True
                
            player.lastTimeTick = time.time()
        
@Event('player_spawn')
def spawnPlayer(e):
    player = players.from_userid(e['userid'])
    
    player.maxhealth = 100            
    player.spawnloc = player.origin    
    player.spellbook = PagedMenu(title='[D&D] %s Spells'%player.getClass())
        
    if player.getClass() == fighter.name:
        player.secondWind = 1
        messagePlayer('You gained 10% damage from Greater Weapon Fighting!', player.index)
        
        if player.getLevel() >= 3:
            messagePlayer('You have an extra 5% chance to score a critical hit!', player.index)
            
        if player.getLevel() >= 5:
            messagePlayer('You deal an extra 5% damage for having an Extra Attack!', player.index)
        
        if player.getLevel() >= 7:
            player.disarms = int((player.getLevel() - 2) / 5)   #+ 10000
            spell = '!cast Disarm - %s Charges - Disarms enemies primary weapon. (Str save negates)'%player.disarms
            messagePlayer(spell, player.index)
            player.disarm = False
            formatLine(spell, player.spellbook)
        
        if player.getLevel() >= 9:
            player.indomitable = 1
        if player.getLevel() >= 13:
            player.indomitable = 2            
        if player.getLevel() >= 9:
            messagePlayer('You are now Indomitable (reroll %s failed saves)'%player.indomitable, player.index)
            
        if player.getLevel() >= 10:
            messagePlayer('You have a 5% chance to parry attacks!', player.index)
            
        if player.getLevel() >= 11:
            messagePlayer('You deal an extra 5% damage for having another Extra Attack!', player.index)
            
        if player.getLevel() >= 15:
            messagePlayer('You have an extra 5% chance to score a critical hit! A 15% Chance!!!', player.index)
            
        if player.getLevel() >= 20:
            messagePlayer('You are a Survivor! Heal 10HP every kill!', player.index)
            
    if player.getClass() == cleric.name:
        player.mana = int(player.getLevel() / 2) * 5 + int(player.getLevel() / 2) * 10 + (10 if player.getLevel() % 2 else 0) + 5
        messagePlayer('You have %s mana to cast spells with'%player.mana, player.index)
        if not hasattr(player, 'alignment'):
            player.alignment = 'good'
        if player.alignment == 'good':
            messagePlayer('You are a Good Cleric and do 20% more Curing', player.index)
        else:
            messagePlayer('You are an Evil Cleric and cause 20% more Wounds', player.index)
        spell = '!cast {Evil/Good} - You can change your alignment'
        messagePlayer(spell, player.index)
        formatLine(spell, player.spellbook)
        
        spell = '!cast Inflict {amount} / !cast Cure {amount}'
        formatLine(spell,player.spellbook)
        messagePlayer('!cast Inflict {amount} / !cast Cure {amount}', player.index)
        spell = 'Inflict to deal damage, Cure to heal. Spend up to %s mana (1HP/mana)'%(min(player.mana, player.getLevel()*2+10))
        formatLine(spell, player.spellbook)
        messagePlayer('Inflict to deal damage, Cure to heal. Spend up to %s mana (1HP/mana)'%(min(player.mana, player.getLevel()*2+10)), player.index)
        
        if player.getLevel() >= 3:
            spell = '!cast Sacred Flame - 15 mana - %sd8 damage + burn (Dex save halves)'%(3+player.getLevel()/5)
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Sacred Flame - 15 mana - %sd8 damage + burn (Dex save halves)'%(3+player.getLevel()/5), player.index)
            spell = '!cast Bless - 10 mana - Increase chance for nearby allies to save'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Bless - 10 mana - Increase chance for nearby allies to save', player.index)
            
        if player.getLevel() >= 5:
            spell = '!cast Spiritual Weapon {weapon} - 30 mana - Give yourself a weapon (give command)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Spiritual Weapon {weapon} - 30 mana - Give yourself a weapon (give command)', player.index) 
            spell = '!cast Curse - 30 mana - Target takes additional 3d8 damage from all sources (Wisdom save negates)'
            formatline(spell, player.spellbook)
            messagePlayer('!cast Curse - 30 mana - Target takes additional 3d8 damage from all sources (Wisdom save negates)', player.index)
            
        if player.getLevel() >= 7:
            player.channels = (player.getLevel() - 2) / 5
            messagePlayer('!cast Channel Divinity - Unleash a burst of Healing/Good or Damage/Evil around you (5d8, %s uses)'%player.channels, player.index)
            spell = '!cast Channel Divinity - Unleash a burst of Healing/Good or Damage/Evil around you (5d8, %s uses)'%player.channels
            formatLine(spell, player.spellbook)
            
        if player.getLevel() >= 9:
            spell = '!cast Death Ward - 20 Mana - The next killing blow on your target reduces them to 1HP instead'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Death Ward - 20 Mana - The next killing blow on your target reduces them to 1HP instead', player.index)
            
        if player.getLevel() >= 11:
            spell = '!cast Banishment - 50 Mana - Banish a target, sends them back to spawn'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Banishment - 50 Mana - Banish a target, sends them back to spawn', player.index)
            
        if player.getLevel() >= 15:
            spell = '!cast Spirit Guardians - 50 Mana - Weapons of your ancestors fire on attackers for 2s (3d8, Wisdom save halves)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Spirit Guardians - 50 Mana - Weapons of your ancestors fire on attackers for 2s (3d8, Wisdom save halves)', player.index)
        
        if player.getLevel() >= 20:
            spell = '!cast True Ressurection - 100 Mana - Bring back an ally from the dead'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast True Ressurection - 100 Mana - Bring back an ally from the dead', player.index)
            
    if player.getClass() == rogue.name:
        player.stealth = time.time() - 7
        player.stealthMessage = False
        player.stealthChecks = {}
        messagePlayer('You are stealthed. After shooting, jumping, using an ability, or being shot, you restealth after {:.2f} seconds'.format(6.225 - player.getLevel()*(4.5/20)), player.index)
        messagePlayer('While stealthed, you can Sneak Attack (%sd6 SA dice)'%int((player.getLevel()+3)/2 - 1), player.index)
        
        if player.getLevel() >= 3:
            player.endurance = 3 + (player.getLevel() - 3) * (3/17)
            player.dashCooldown = time.time() - 4
            player.lastTimeTick = time.time()
            player.dashMessage = False            
            messagePlayer('You can now dash! Hold your walk key to run! (3s)', player.index)
            messagePlayer('You can now steal money and guns from your opponent! Get close and attack!', player.index)
            
        if player.getLevel() >= 5:
            messagePlayer('You are Evasive and have advantage on Dexterity saves!', player.index)
            
        if player.getLevel() >= 11:
            messagePlayer('You are Elusive and can not be crit!', player.index)
            
        if player.getLevel() >= 20:
            messagePlayer('You are an Assassin! Sneak Attack players not facing you!', player.index)
            
    if player.getClass() == sorcerer.name:
        player.mana = int(player.getLevel() / 2) * 5 + int(player.getLevel() / 2) * 10 + (10 if player.getLevel() % 2 else 0) + 5
        messagePlayer('You have %s mana to cast spells with'%player.mana, player.index)
        
        spell = '!cast Prestidigitation - 10 mana - Throws a fake flashbang to freak out enemies'
        formatLine(spell, player.spellbook)
        messagePlayer('!cast Prestidigitation - 10 mana - Throws a fake flashbang to freak out enemies', player.index)
        spell = '!cast Mage Armor - 10 mana - Create a magical set of armor for yourself'
        formatLine(spell, player.spellbook)
        messagePlayer('!cast Mage Armor - 10 mana - Create a magical set of armor for yourself', player.index)
        
        if player.getLevel() >= 2:
            spell = '!cast Magic Missile - 10 mana - Deal 3d4+5 damage to a target'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Magic Missile - 10 mana - Deal 3d4+5 damage to a target', player.index)
            spell = '!cast Thunderwave - 10 mana - Push enemies away from you and deal 2d8 damage (Con save halves, no push)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Thunderwave - 10 mana - Push enemies away from you and deal 2d8 damage (Con save halves, no push)', player.index)
            
        if player.getLevel() >= 3:
            spell = '!cast Alter Self - 10 mana - Disguise yourself as an enemy'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Alter Self - 10 mana - Disguise yourself as an enemy', player.index)
            spell = '!cast Brightness - 20 mana - Create a blindingly-bright light that follows you (2.5s)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Brightness - 20 mana - Create a blindingly-bright light that follows you (2.5s)', player.index)
            
        if player.getLevel() >= 4:
            spell = '!cast Acid Splash - 20 mana - Removes all enemies armor in an area (Dex save negates)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Acid Splash - 20 mana - Removes all enemies armor in an area (Dex save negates)', player.index)
            
        if player.getLevel() >= 5:
            spell = '!cast Misty Step - 25 mana - Teleport forward to where you are looking! (Wall safe)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Misty Step - 25 mana - Teleport forward to where you are looking! (Wall safe)', player.index)
            spell = '!cast Fireball - 30 mana - Shoot a fireball where you\'re looking! (5d8, Dex save halves)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Fireball - 30 mana - Shoot a fireball where you\'re looking! (5d8, Dex save halves)', player.index)
            
        if player.getLevel() >= 7:
            spell = '!cast Silence - 35 mana - Silences everyone in an aerae you\'re looking at for 5s'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Silence - 35 mana - Silences everyone in an area you\'re looking at for 5s', player.index)
            spell = '!cast Confusion - 50 mana - All players have a random skin'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Confusion - 50 mana - All players have a random skin', player.index)
        
        if player.getLevel() >= 9:
            spell = '!cast Greater Invisibility - 40 mana - Become invisible for 3s'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Greater Invisibility - 40 mana - Become invisible for 3s', player.index)
            spell = '!cast Polymorph - 40 mana - Turn an enemy into a chicken for 3s (Wis negates)'
            formatLine(spell, player.spellbook)
            messagePlayer('!cast Polymorph - 40 mana - Turn an enemy into a chicken for 3s (Wis negates)', player.index)
            
        if player.getLevel() >= 11:
            spell = "!cast Wall of Fire - 50 mana - Create a wall of fire for 3s that burns for 5d8 (Dex halves)"
            formatLine(spell, player.spellbook)
            messagePlayer(spell, player.index)
            
            spell = "!cast Stoneshape - 40 mana - Shape a wall of stone to hide behind (450HP)"
            formatLine(spell, player.spellbook)
            messagePlayer(spell, player.index)
            
        if player.getLevel() >= 13:
            spell = "!cast True Seeing - 40 mana - Reveals hidden enemies nearby (10s)"
            formatLine(spell, player.spellbook)
            messagePlayer(spell, player.index)
            
        if player.getLevel() >= 15:
            spell = "!cast Chain Lightning - 80 mana - Strike a target, then three others nearby for 7d8 (Dex save halves)"
            formatLine(spell, player.spellbook)
            messagePlayer(spell, player.index)
            
        if player.getLevel() >= 17:
            spell = "!cast Delayed Blast Fireball - 100 mana - Fire a missile that explodes (if still alive) after 3s for 10d8 (Dex halves)"
            formatLine(spell, player.spellbook)
            messagePlayer(spell, player.index)
            
        if player.getLevel() >= 20:
            spell = "!cast Fly - 120 mana - Look where you want to move to!"
            formatLine(spell, player.spellbook)
            messagePlayer(spell, player.index)

abilities = {
    'second wind',
    'cure',
    'inflict',
    'sacred flame',
    'bless',
    'spiritual weapon',
    'curse',
    'channel divinity',
    'death ward',
    'anishment',
    'spirit guardians',
    'true resurrection',
    'prestidigitation',
    'mage armor',
    'magic missile',
    'thunderwave',
    'alter self',
    'brightness',
    'acid splash',
    'misty step',
    'fireball',
    'silence',
    'confusion',
    'greater invisibility',
    'polymorph',
    'wall of fire',
    'stoneshape',
    'chain lightning',
    'true seeing',
    'delayed blast fireball',
    'fly'
}

toggles = {
    'evil',
    'good',
    'disarm'
}

@ClientCommand('reportbug')
def bugReport(command,index):
    print('Bug submitted!')
    player = players.from_userid(userid_from_index(index))
    reportTime = time.ctime()
    with open(bugFile, 'a') as bf:
        bf.write("%s %s at %s\n"%(getSteamid(player.userid), player.name, reportTime))
        bf.write(command.arg_string)
        bf.write("\n")
        
    messagePlayer('Thank you for submitting a bug. Please remind Aurora about your submission.', player.index)

@ClientCommand('!cast')
def cast(command, index):
    a = command.arg_string if len(command) > 1 else messagePlayer("You didn't specify an ability to use", index)
    ability = a
    amount = None
    
    if ability.lower().startswith('cure') or ability.lower().startswith('inflict'):
        ability = ability.split(' ')[0]
        try:
            amount = int(a.split(' ')[1])
        except:
            messagePlayer('You specify how much to heal/damage: !cast Cure 10', index)
            return
    
    if ability.lower().startswith('spiritual weapon'):
        ability = 'spiritual weapon'
        try:
            amount = a.split(' ')[2]
        except:
            messagePlayer('You need to specify which weapon: !cast Spiritual Weapon {weapon}', index)
            return

    if ability.lower() not in abilities:
        if ability.lower() not in toggles:
            messagePlayer("'%s' is not an ability"%ability, index)
            return
    player = players.from_userid(userid_from_index(index))
        
    if ability.lower() in abilities:
        if not player.dead:      
            if time.time() - player.spellCooldown > 1.5:
                
                if player.getClass() == fighter.name:
                    if ability.lower() == 'second wind':
                        if not player.secondWind > 0:
                            messagePlayer('You no longer have a Second Wind!', index)
                            return
                            
                        if player.health < player.maxhealth:
                            hp = player.health
                            player.health = min(player.health + player.getLevel() + 10, player.maxhealth)
                            messagePlayer('You had a Second Wind! Healed for %s HP!'%(player.health-hp), index)
                            player.spellCooldown = time.time()
                            player.secondWind -= 1
                        
                            
                if player.getClass() == cleric.name:
                
                    if not player.mana and ability != 'channel divinity':
                        messagePlayer('You don\'t have any mana', player.index)
                        return
                    
                    if ability.lower() in ['inflict', 'cure']:
                        if not amount:
                            messagePlayer('You specify how much to heal/damage: !cast Cure 10', player.index)
                            return
                        
                        amount = min(player.mana, amount)
                        if not amount <= player.getLevel() * 2 + 10:
                            messagePlayer('You can only spend up to %s mana'%player.getLevel()*2 + 10,player.index)
                            return
                        
                        target = player.get_view_player()
                        if not target:
                            if Vector.get_distance(player.get_view_coordinates(), player.origin) <= 25:
                                target = player
                        else:
                            target = players.from_userid(target.userid)
                        if target:
                            if ability.lower() == 'inflict':
                                if target.team != player.team and not target.dead:
                                    damage = amount
                                    if player.alignment == 'evil':
                                        damage = int(amount * 1.2)
                                    messagePlayer('You Inflicted Wounds for %s damage!'%damage, player.index)
                                    messagePlayer('You were Inflicted with Wounds!', target.index)
                                    hurt(player, target, amount, spell=True)
                                    Sound(sample='physics/flesh/flesh_impact_bullet5.wav', origin=target.origin, direction=player.view_vector, volume=.5).play()
                                    player.spellCooldown = time.time()
                                    player.mana -= amount
                                    
                            if ability.lower() == 'cure':
                                if target.team == player.team and not target.dead:
                                    healing = amount
                                    if player.alignment == 'good':
                                        healing = int(amount * 1.2)
                                    hp = target.heal(healing)
                                    if hp:
                                        messagePlayer('You healed %s for %s health!'%(target.name, healing), player.index)
                                        messagePlayer('You were healed for %s health!'%hp, target.index)
                                        player.mana -= amount
                                        player.spellCooldown=time.time()      
                                    else:
                                        messagePlayer('They\'re full hp!', player.index)
                                
                        
                            
                    if ability.lower() == 'sacred flame':
                        if not player.getLevel() >= 3:
                            return
                        if not player.mana >= 15:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 15), player.index)
                            return
                        target = player.get_view_player()
                        if not target:
                            return
                        target = players.from_userid(target.userid)
                        if target.team != player.team and not target.dead:
                            player.mana -= 15
                            player.spellCooldown = time.time()
                            damage = dice((3+player.getLevel()/5),8)
                            if diceCheck((11 + player.getProficiencyBonus(), 'Dexterity'), target):
                                messagePlayer('You smote %s for %s damage!'%(target.name, int(damage/2)), player.index)
                                messagePlayer('You were smitten!', target.index)
                                hurt(player, target, int(damage/2))                                
                            else:
                                messagePlayer('You burned %s for %s damage!'%(target.name, int(damage)), player.index)
                                messagePlayer('You were smitten with fire!', target.index)
                                hurt(player, target, int(damage))
                                target.ignite_lifetime(1.7+.2*player.getLevel())
                            
                    if ability.lower() == 'bless':
                        if not player.getLevel() >= 3:
                            return
                        if not player.mana >= 10:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 15), player.index)
                            return
                        player.mana -= 10
                        player.spellCooldown = time.time()
                        for target in PlayerIter():
                            if target.team == player.team and not target.dead:
                                if Vector.get_distance(target.origin, player.origin) < 500:
                                    if not hasattr(target.bless):
                                        target.bless = True
                                        messagePlayer('You have been Blessed by a Cleric. Increases your chance to make saves!', target.index)
                                    else:
                                        if not target.bless:
                                            target.bless = True
                                            messagePlayer('You have been Blessed by a Cleric. Increases your chance to make saves!', target.index)
                                    
                            
                    if ability.lower() == 'spiritual weapon':
                        if not player.getLevel() >= 5:
                            return
                        if not player.mana >= 30:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 30), player.index)
                            return
                        if amount.startswith('weapon_'):
                            amount = amount.replace('weapon_','')
                        if amount in allWeapons:
                            player.give_named_item('weapon_' + amount)
                            player.mana -= 30
                            player.spellCooldown = time.time()       
                            messagePlayer('You have summoned a Spiritual Weapon', player.index)
                        else:
                            messagePlayer('%s isn\'t a valid weapon name', player.index)
                            
                    if ability.lower() == 'curse':
                        if not player.getLevel() >= 5:
                            return
                        if not player.mana >= 50:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 50), player.index)
                            return
                        target = player.get_view_player()
                        if not target:
                            return
                        target = players.from_userid(target.userid)
                        if target.team != player.team and not target.dead:
                            player.mana -= 50
                            player.spellCooldown = time.time()       
                            if not diceCheck((11 + player.getProficiencyBonus(), 'Wisdom'), target):
                                target.curse = True
                                messagePlayer('You have Cursed %s'%target.name, player.index)
                                messagePlayer('You have been Cursed!', target.index)
                            else:
                                messagePlayer('Your target resists your curse!', player.index)
                                
                    if ability.lower() == 'channel divinity':
                        if not player.getLevel() >= 7:
                            return
                        if not player.channels > 0:
                            messagePlayer('You have no more uses of Channel Divinity', player.index)                            
                            return
                        
                        sound = Sound(sample='items/medcharge4.wav', origin=player.origin, volume=.5)
                        sound.play()
                        Delay(.75, sound.stop)
                        player.channels -= 1
                        player.spellCooldown = time.time()
                        if player.alignment.lower() == 'good':
                            for p in PlayerIter():
                                if not p.dead and p.team == player.team and Vector.get_distance(player.origin, p.origin) < 500:
                                    target = players.from_userid(p.userid)
                                    hp = target.heal(dice(5,8))
                                    if hp:
                                        messagePlayer('Your Channel Divinity healed %s for %s HP!'%(target.name, hp), player.index)
                                        messagePlayer('You were healed by %s\'s Divine Power'%player.name, target.index)
                                        
                        if player.alignment.lower() == 'evil':
                            for p in PlayerIter():
                                if not p.dead and p.team == player.team and Vector.get_distance(player.origin, p.origin) < 500:
                                    target = players.from_userid(p.userid)
                                    damage = dice(5,8)
                                    messagePlayer('You were assaulted by %s\'s Divine Power'%player.name, target.index)
                                    messagePlayer('Your Channel Divinity caused %s wounds to %s!'%(damage, target.name), player.index)
                                    hurt(player, target, damage)
                                    
                    if ability.lower() == 'death ward':
                        if not player.getLevel() >= 9:
                            return
                        if not player.mana >= 20:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 20), player.index)
                            return
                        target = player.get_view_player()
                        if not target:
                            return
                        target = players.from_userid(target.userid)
                        if not target:
                            if Vector.get_distance(player.get_view_coordinates(), player.origin) <= 25:
                                target = player
                        if target.team == player.team and not target.dead:
                            if hasattr(target, 'deathward'):
                                if target.deathward > 0:
                                    messagePlayer('%s has already been Warded from Death', player.index)
                            else:
                                player.mana -= 20
                                player.spellCooldown = time.time()
                                target.deathward = 1
                                messagePlayer('%s has been Warded from Death', player.index)
                                messagePlayer('The next shot that would kill you instead reduces you to 1HP (Death Ward)', target.index)
                                
                    if ability.lower() == 'banishment':
                        if not player.getLevel() >= 11:
                            return
                        if not player.mana >= 50:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 50), player.index)
                            return
                        target = player.get_view_player()
                        if not target:
                            return
                        target = players.from_userid(target.userid)
                        if target.team != player.team and not target.dead:
                            player.mana -= 50
                            player.spellCooldown = time.time()
                            if diceCheck((11 + player.getProficiencyBonus(), 'Charisma'), target):
                                messagePlayer('You have failed to Banish!'%target.name, player.index)
                            else:
                                messagePlayer('You have Banished %s back to spawn!'%target.name, player.index)
                                messagePlayer('You were Banished back to spawn!', target.index)
                                target.origin = target.spawnloc
                                
                    if ability.lower() == 'spirit guardians':
                        if not player.getLevel() >= 15:
                            return
                        if not player.mana >= 50:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 50), player.index)
                            return
                        
                        if hasattr(player, 'spiritguardians'):
                            if player.spiritguardians:
                                messagePlayer('Your Spirit Guardians are still active!', player.index)
                                return                        
                    
                        player.mana -= 50
                        player.spellCooldown = time.time()
                        weapons = []
                        for x in range(0,10):
                            weapons.append(newWeapon())
                        floatWeapons(player, weapons)
                        player.spiritguardians = True
                        messagePlayer('You are protected for the next 2 seconds by your ancestors', player.index)
                        
                    if ability.lower() == 'true resurrection':
                    
                        def confirmRes(menu, index, choice):
                            target = players.from_userid(userid_from_index(index))
                            cleric = target.savior
                            if choice.value == 1:
                                if not cleric.dead and target.dead and target.get_team() == cleric.get_team():
                                    if cleric.getClass() == cleric.name and cleric.getLevel() >= 20 and cleric.mana >= 200:
                                        target.spawn()
                                        target.origin = target.deathspot
                                        messagePlayer('You have been brought back to life!', target.index)
                                        messagePlayer('You have brought %s back to life!'%target.name, cleric.index)                                        
                                        cleric.mana -= 100
                            else:
                                messagePlayer('%s does not want to return from the land of the dead'%target.name, cleric.index)
                    
                        def resSelection(menu, index, choice):
                            player = players.from_userid(userid_from_index(index))
                            if player.getClass() == 'Cleric' and player.getLevel() >= 20 and player.mana >= 100:
                                target = choice.value
                                target = players.from_userid(userid_from_index(choice.value))
                                if target in list(PlayerIter()):

                                    if target.get_team() == player.get_team() and target.dead:
                                        if target.is_bot():
                                            target.spawn()
                                            target.origin = target.deathspot
                                            messagePlayer('You have been brought back to life!', target.index)
                                            messagePlayer('You have brought %s back to life!'%target.name, player.index)                                        
                                            player.mana -= 100
                                        else:                                    
                                            target.savior = player
                                            resAsk = PagedMenu(title='[D&D] Confirm resurrection')
                                            resAsk.append('%s wants to Resurrect you. Accept?'%player.name)
                                            resAsk.append(PagedOption('Yes', 1))
                                            resAsk.append(PagedOption('No', 0))
                                            resAsk.select_callback = confirmRes
                                            resAsk.send(target.index)
                    
                        if not player.getLevel() >= 20:
                            return
                        if not player.mana >= 100:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 100), player.index)
                            return
                        
                        resMenu = PagedMenu(title="[D&D] Resurrection Menu")
                        for p in PlayerIter():
                            if p.dead and p.get_team() == player.get_team():
                                resMenu.append(PagedOption('%s %s'%(p.name, '(BOT)' if getSteamid(p.userid) else '') , p.index))
                        resMenu.select_callback = resSelection
                        resMenu.send(player.index)
                        
                if player.getClass() == sorcerer.name:
                
                    if ability.lower() == 'prestidigitation':
                        if not player.getLevel() >= 1:
                            return
                        if not player.mana >= 10:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 10), player.index)
                            return
                        
                        player.mana -= 10
                        player.spellCooldown = time.time()                        
                        fakeFlash(player)
                        
                    if ability.lower() == 'mage armor':
                        if not player.getLevel() >= 1:
                            return
                        if not player.mana >= 10:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 10), player.index)
                            return
                        
                        player.mana -= 10
                        player.spellCooldown = time.time()                        
                        player.give_named_item('item_assaultsuit')
                        
                    if ability.lower() == 'magic missile':
                        if not player.getLevel() >= 2:
                            return
                        if not player.mana >= 10:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 10), player.index)
                            return
                        
                        target = player.get_view_player()
                        if not target:
                            return
                            
                        if not target.dead and target.get_team() != player.get_team():
                            player.mana -= 10
                            player.spellCooldown = time.time()        
                            damage = dice(3,4) + 5
                            hurt(player, target, damage)
                            messagePlayer('Your Magic Missiles hit for %s damage!'%damage, player.index)
                            messagePlayer('You were hit by Magic Missiles!', target.index)
                            Sound(sample='physics/flesh/flesh_impact_bullet1.wav', origin=target.origin, direction=player.view_vector, volume=.5).play()
                            
                    if ability.lower() == 'thunderwave':
                        if not player.getLevel() >= 2:
                            return
                        if not player.mana >= 10:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 10), player.index)
                            return
                        
                        player.mana -= 10
                        player.spellCooldown = time.time()    
                        targets = list(PlayerIter())
                        thunder_sound = Sound(sample='weapons/flashbang/flashbang_explode2.wav', origin=player.origin, direction=player.view_vector, volume=.5)
                        if not thunder_sound.is_precached:
                            thunder_sound.precache()
                        thunder_sound.play()
                        for target in targets:
                            if Vector.get_distance(target.origin, player.origin) < 500:
                                target = players.from_userid(target.userid)
                                if not target.dead and target.get_team() != player.get_team():
                                    damage = dice(2,8)
                                    if not diceCheck((11+player.getProficiencyBonus(), 'Constitution'), target, player):
                                        hurt(player, target, damage)
                                        push(player, target)
                                        messagePlayer('A Thunderwave blasts away %s for %s damage!'%(target.name, damage), player.index)
                                    else:
                                        hurt(player, target, damage/2)
                                        messagePlayer('A Thunderwave blasts did %s damage!'%(damage), player.index)
                                        
                    if ability.lower() == 'alter self':
                        if not player.getLevel() >= 3:
                            return
                        if not player.mana >= 10:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 10), player.index)
                            return
                        
                        player.mana -= 10
                        player.spellCooldown = time.time()                        
                        mdl = random.choice(counterTerroristModels if player.get_team() == 2 else terroristModels)
                        player.model = Model('models/player/%s'%mdl)
                        messagePlayer('You have disguised yourself!', player.index)
                        
                    if ability.lower() == 'brightness':
                        if not player.getLevel() >= 3:
                            return
                        if not player.mana >= 20:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 20), player.index)
                            return
                        
                        player.mana -= 20
                        player.spellCooldown = time.time()   
                        
                        for x in range(1,25):
                            Delay(x/10, flashPlayer, (player,))
                            
                    if ability.lower() == 'acid splash':
                        if not player.getLevel() >= 4:
                            return
                        if not player.mana >= 20:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 20), player.index)
                            return
                        
                        target = player.get_view_player()
                        if not target:
                            return
                            
                        player.mana -= 20
                        player.spellCooldown = time.time()   
                        
                        for t in PlayerIter():
                            if t.get_team() != player.get_team() and not t.dead:
                                if Vector.get_distance(player.origin, t.origin) <= 500:
                                    t = players.from_userid(t.userid)
                                    Sound(sample='player/water/pl_wade2.wav', origin=t.origin, volume=.5).play()
                                    if not diceCheck((11+player.getProficiencyBonus(), 'Dexterity'), t, player):
                                        t.armor = 0
                                        t.has_helmet = False
                                        messagePlayer('You melted %s\'s armor!'%t.name, player.index)
                                        messagePlayer('Your armor was melted!',t.index)
                                        
                    if ability.lower() == 'misty step':
                        if not player.getLevel() >= 5:
                            return
                        if not player.mana >= 25:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 25), player.index)
                            return
                        playerStartLoc = player.origin
                        destination = player.eye_location + player.view_vector * 1000
                        # Get a new trace instance
                        trace = GameTrace()
                        # Trace from the player's feet to the destination
                        engine_trace.trace_ray(
                            # This matches the player's bounding box from his feets to
                            # the destination
                            Ray(player.origin, destination, player.mins, player.maxs),
                            # This collides with everything
                            ContentMasks.ALL,
                            # This ignore nothing but the player himself
                            TraceFilterSimple((player,)),
                            # The trace will contains the results
                            trace
                        )

                        # If the trace did hit, that means there was obstruction along the way
                        if trace.did_hit():
                            # So the end of our trace becomes our destination
                            destination = trace.end_position
                        # Teleport the player to the destination
                        player.teleport(destination)
                        
                        if Vector.get_distance(playerStartLoc, player.origin) <= 250:
                            player.origin = playerStartLoc
                            messagePlayer('Your Misty Step failed! (Make sure you look high enough)', player.index)
                        else:
                            sound = Sound(sample='ambient/machines/steam_release_2.wav', origin=playerStartLoc, volume=.5)
                            sound.play()
                            player.mana -= 25
                            player.spellCooldown = time.time()
                            
                    if ability.lower() == 'fireball':
                        if not player.getLevel() >= 5:
                            return
                        if not player.mana >= 30:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 30), player.index)
                            return
                            
                        player.mana -= 30
                        player.spellCooldown = time.time()   
                        
                        point = player.get_view_coordinates()
                        x,y,z = player.get_view_coordinates()
                        vecs = [Vector(x+25,y,z), Vector(x-25,y,z), Vector(x,y+25,z), Vector(x,y-25,z)]
                        sound = Sound(sample='weapons/molotov/fire_ignite_1.wav', origin=Vector(x,y,z), volume=.5)
                        sound.play()
                        Delay(1, sound.stop)
                        for x in range(0,4):
                            createFire(vecs[x], 1)
                        damage = dice(5,8)
                        for t in PlayerIter():
                            if not t.dead:
                                if Vector.get_distance(point, t.origin) <= 500:
                                    t = players.from_userid(t.userid)
                                    if not diceCheck((11+player.getProficiencyBonus(), 'Dexterity'), t, player):
                                        hurt(player, t, damage)
                                        messagePlayer('You hit %s with the full brunt of a Fireball!'%t.name, player.index)
                                        messagePlayer('You were hit with the full brunt of a fireball!',t.index)
                                    else:
                                        hurt(player, t, int(damage/2))
                                        messagePlayer('You hit %s with a Fireball!'%t.name, player.index)
                                        messagePlayer('You were hit by a fireball!',t.index)
                                            
                    if ability.lower() == 'silence':
                        if not player.getLevel() >= 7:
                            return
                        if not player.mana >= 35:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 35), player.index)
                            return
                            
                        player.mana -= 35
                        player.spellCooldown = time.time()   
                        
                        point = player.get_view_coordinates()                            
                        for t in PlayerIter():
                            if not t.dead:
                                if Vector.get_distance(point, t.origin) <= 500:
                                    t = players.from_userid(t.userid)
                                    t.spellCooldown = time.time() + 5
                                    messagePlayer('You have been silenced for 5 seconds!', t.index)   

                    if ability.lower() == 'confusion':
                        if not player.getLevel() >= 7:
                            return
                        if not player.mana >= 35:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 35), player.index)
                            return
                            
                        player.mana -= 35
                        player.spellCooldown = time.time()   
                        
                        point = player.get_view_coordinates()                            
                        messageServer('You have become confused!')
                        for t in PlayerIter():
                            if not t.dead:
                                models = list(chain(counterTerroristModels, terroristModels))
                                t.model = Model('models/player/%s'%random.choice(models))
                                    
                    if ability.lower() == 'greater invisibility':
                        if not player.getLevel() >= 9:
                            return
                        if not player.mana >= 40:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 40), player.index)
                            return
                            
                        player.mana -= 40
                        player.spellCooldown = time.time()   
                        
                        player.color = Color(255,255,255).with_alpha(0)
                        messagePlayer('You are now invisible!', player.index)
                        Delay(3, resetColor, (player,))
                            
                    if ability.lower() == 'polymorph':
                        if not player.getLevel() >= 9:
                            return
                        if not player.mana >= 40:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 40), player.index)
                            return
                            
                        target = player.get_view_player()
                        if not target:
                            return
                        target = players.from_userid(target.userid)
                        if target.get_team() != player.get_team() and not target.dead:
                            player.mana -= 40
                            player.spellCooldown = time.time()   
                            if not diceCheck((11+player.getProficiencyBonus(), 'Wisdom'), target, player):
                        
                                mdl = target.model
                                target.model = Model('models/chicken/chicken.mdl')
                                Sound(sample='ambient/creatures/chicken_panic_03.wav', origin=target.origin).play()
                                for weapon in target.weapons():
                                    Delay(3, target.give_named_item, (weapon.weapon_name, 0, None, False, NULL))
                                    weapon.remove()
                                Delay(3, resetModel, (target, mdl))       
                                messagePlayer('You have been Polymorphed into a chicken!', target.index)
                                    
                    if ability.lower() == 'wall of fire':
                        if not player.getLevel() >= 11:
                            return
                        if not player.mana >= 50:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 50), player.index)
                            return
                            
                        player.mana -= 50
                        player.spellCooldown = time.time()   
                        wallOfFire(player)        

                    if ability.lower() == 'stoneshape':
                        if not player.getLevel() >= 11:
                            return
                        if not player.mana >= 40:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 40), player.index)
                            return
                            
                        player.mana -= 40
                        player.spellCooldown = time.time()   
                        Sound(sample='physics/destruction/smash_rockcollapse1.wav', origin=player.get_view_coordinates(), volume=.5).play()
                        door = Entity.create('prop_physics_multiplayer')    
                        door.model = Model('models/props_fortifications/concrete_wall001_140_reference.mdl')
                        door.angles = QAngle(270,player.angles[1],0)
                        door.spawn()
                        door.teleport(player.get_view_coordinates())
                        door.call_input('SetHealth', 450)
                        door.set_property_uchar('m_takedamage', 2)
                        
                    if ability.lower() == 'chain lightning':
                        if not player.getLevel() >= 15:
                            return
                        if not player.mana >= 80:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 80), player.index)
                            return
                            
                        target = player.get_view_player()
                        if not target:
                            return
                        target = players.from_userid(target.userid)
                        targets = []
                        if target.get_team() != player.get_team() and not target.dead:
                            player.mana -= 80
                            player.spellCooldown = time.time()   
                            
                            damage = dice(7,8)
                            targets.append(target)
                            for t in PlayerIter():
                                if len(targets) >= 4:
                                    break
                                if t.get_team() != player.get_team() and not t.dead and t != target:
                                    if Vector.get_distance(t.origin, target.origin) <= 700:
                                        targets.append(t)
                            for t in targets:
                                t = players.from_userid(t.userid)
                                Sound(sample='weapons/taser/taser_hit.wav', origin=t.origin, volume=.5).play()
                                messagePlayer('Your Chain Lightning bounced from %s!'%t.name, player.index)
                                if not diceCheck((11+player.getProficiencyBonus(), 'Dexterity'), t, player):
                                    hurt(player, t, damage)
                                    messagePlayer('You were electrocuted! Shocking!', t.index)
                                else:
                                    hurt(player, t, int(damage/2))
                                    messagePlayer('You were shocked!', t.index)
                                    
                    if ability.lower() == 'true seeing':
                        if not player.getLevel() >= 13:
                            return
                        if not player.mana >= 40:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 40), player.index)
                            return
                        
                        trueSeeing(player, 10)
                    
                    if ability.lower() == 'delayed blast fireball':
                        if not player.getLevel() >= 17:
                            return
                        if not player.mana >= 100:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 100), player.index)
                            return
                            
                        player.mana -= 100
                        player.spellCooldown = time.time()
                        
                        def checkMissile(missile, player):
                            if missile in EntityIter():
                                damage = dice(12,8)
                                Sound(sample='weapons/c4/c4_exp_deb1.wav', origin=missile.origin).play()
                                createFire(missile.origin,2)
                                for target in PlayerIter():
                                    if not target.dead:
                                        if Vector.get_distance(missile.origin, player.origin) <= 700:
                                            target = players.from_userid(target.userid)
                                            if diceCheck((11+ player.getProficiencyBonus(), 'Dexterity'), target, player):
                                                messagePlayer('You caught the tail-end of a Delayed Fireball!', target.index)
                                                hurt(player,target,int(damage/2))
                                            else:
                                                messagePlayer('You got toasted by a Delayed Fireball!', target.index)
                                                hurt(player, target, damage)   
                                missile.take_damage(20)
                        
                        flashbang = Entity.create('prop_physics_multiplayer')
                        flashbang.model = Model('models/props/de_inferno/hr_i/missile/missile_02.mdl')
                        flashbang.spawn()
                        flashbang.angles = QAngle(0,(player.angles[1]-90)%360,0)
                        flashbang.origin = player.eye_location + player.view_vector * 30
                        flashbang.teleport(None, flashbang.angles, player.view_vector * 1500)
                        flashbang.health = 1
                        flashbang.set_property_uchar('m_takedamage', 20)
                        flashbang.thrower = player.owner_handle
                        Delay(3, checkMissile, (flashbang, player))
                        
                if ability.lower() == 'fly':
                        if not player.getLevel() >= 20:
                            return
                        if not player.mana >= 120:
                            messagePlayer('You do not have enough mana for this spell %s/%s'%(player.mana, 120), player.index)
                            return
                            
                        player.mana -= 120
                        player.spellCooldown = time.time()
                        player.set_jetpack(True)
                                
                    
            else:
                messagePlayer('Your spells and abilities are on cooldown!', index)
                
    #=======================================================================================================================================================
    #is a toggle
    else:
        if time.time() - player.toggleDelay > 0.1:
            
            if player.getClass() == fighter.name:
                if not player.dead:
                    if ability.lower() == 'disarm':
                        if player.disarms > 0:
                            player.disarm = not player.disarm
                            if player.disarm:
                                messagePlayer('You are now disarming enemies', index)  
                            else: 
                                messagePlayer('You are no longer disarming enemies', index)
                            player.toggleDelay = time.time()
                        else:
                            messagePlayer('You have no more disarms', index)
                        
            if player.getClass() == cleric.name:
                if ability.lower() in ['evil', 'good']:
                    if player.dead:
                        player.alignment = ability.lower()
                        messagePlayer('You are now a %s Cleric'%ability, player.index)
                        player.toggleDelay = time.time()
                    else:
                        messagePlayer('You must be dead to change your alignment', player.index)
                        
    
    return CommandReturn.BLOCK
    
def trueSeeing(player, duration=10):
    if not player.dead:
        for target in PlayerIter():
            if not target.dead and target.get_team() != player.get_team():
                if Vector.get_distance(target.origin, player.origin) <= 900:
                    if target.stealthed():
                        target.stealth = time.time() + 10
                        messagePlayer('You spotted a Rogue!', player.index)
                        messagePlayer('You were spotted with a glowing eye!', target.index)
                        break
                    if target.color.a == 0:
                        target.color.a = 255
                        messagePlayer('You spotted an invisible enemy!', player.index)
                        messagePlayer('You noticed someone looking directly at you!', target.index)
    if duration > 0:
        Delay(duration - 1, trueSeeing, (player, duration-1))
    
def wallBurn(attacker, points, duration):
    damage = dice(5,8)    
    ps = list(PlayerIter())
    for player in ps:
        for point in points:
            if not player.dead:
                if Vector.get_distance(point, player.origin) <= 150:
                    player = players.from_userid(player.userid)
                    if diceCheck((11+attacker.getProficiencyBonus(), 'Dexterity'), player, attacker):
                        hurt(attacker, player, int(damage/2))
                        messagePlayer('You jumped through a fire wall!', player.index)
                    else:
                        hurt(attacker, player, damage)
                        messagePlayer('You sat in a fire wall!', player.index)
                    break
                    
    if duration > 0:
        Delay(.75, wallBurn, (attacker, points, duration - .75))
    
def wallOfFire(player):
    duration = 3
    firePoints = [player.get_view_coordinates()]
    Ax,Ay,Az = player.origin
    Bx,By,Bz = player.get_view_coordinates()
    createFire(player.get_view_coordinates(), duration)
    sound = Sound(sample='weapons/molotov/fire_ignite_1.wav', origin=player.get_view_coordinates(), volume=.5).play()
    for i in range(25,int(500/2),25):                
        BC = i
        AB = Vector.get_distance(Vector(Bx,By,Bz), Vector(Ax,Ay,Az))
        AC = math.sqrt(BC**2 + AB**2)
        a = math.asin(BC/AC)
        r = AC
        theta = player.angles[1] * (math.pi/180) - a
        
        Cx = r * math.cos(theta)
        Cy = r * math.sin(theta)
        Cz = Bz
        C = Vector(Cx+Ax, Cy+Ay, Cz)        
        createFire(C, duration)        
        
        theta = player.angles[1] * (math.pi/180) + a        
        Cx = r * math.cos(theta)
        Cy = r * math.sin(theta)
        C = Vector(Cx+Ax, Cy+Ay, Cz)        
        firePoints.append(C)
        createFire(C, duration)
    wallBurn(player, firePoints, duration)
        
def createFire(point, duration):
    particle2 = Entity.create('info_particle_system')
    particle2.effect_name = ('molotov_groundfire')
    particle2.origin = point
    particle2.effect_index = string_tables.ParticleEffectNames.add_string('molotov_groundfire')
    particle2.start_active = 1
    particle2.start()
    Delay(duration, particle2.remove)
    
def resetModel(player, mdl):
    player.model = mdl
    
def resetColor(player):
    player.color = Color(255,255,255).with_alpha(255)
    messagePlayer('You are visible again!',player.index)
    
def flashPlayer(player):
    flashbang = Entity.create('flashbang_projectile')
    flashbang.spawn()
    flashbang.origin = player.get_eye_location()
    flashbang.detonate()
    
def floatWeapons(player, weapons, iteration=275):    
    if not iteration:
        if hasattr(player, 'spiritguardians'):
            player.spiritguardians = 0
        for weapon in weapons:                    
            weapon.remove()
        print('ended')
        return
    degree = (2*math.pi)/len(weapons) + iteration * .005
    x,y,z = player.get_eye_location()
    weapons[-1].origin = Vector(x+30,y,z)
    for i in range(0,len(weapons)):
        if i == 0:
            weapon = weapons[-1]
        else:
            weapon = weapons[i-1]
        
        x2,y2,z2 = weapon.origin
        x3 = (x2-x) * math.cos(degree) - (y2-y) * math.sin(degree)
        y3 = (y2-y) * math.cos(degree) + (x2-x) * math.sin(degree)
        
        weapons[i].origin = Vector(x3+x,y3+y,z)
        weapons[i].angles = QAngle(270,0,0)
    
    Delay(.005, floatWeapons, (player,weapons,iteration-1))
    
def push(player, target):
    x,y,z = player.view_vector
    x2,y2,z2 = target.origin
    target.origin = Vector(x2,y2,z2+20)
    target.teleport(None, target.angles, Vector(x,y,z)*1500)
    
def fakeFlash(player):
    flashbang = Entity.create('flashbang_projectile')
    flashbang.spawn()
    flashbang.origin = player.eye_location + player.view_vector * 30
    flashbang.teleport(None, flashbang.angles, player.view_vector * 1500)
    Delay(1.6, flashbang.remove)
            
def newWeapon():
    m4a1 = ('weapon_m4a1', Model('models/weapons/w_rif_m4a1.mdl'))
    ak47 = ('weapon_ak47', Model('models/weapons/w_rif_ak47.mdl'))
    sg553 = ('weapon_sg556', Model('models/weapons/w_rif_sg556.mdl'))
    aug = ('weapon_sg556', Model('models/weapons/w_rif_aug.mdl'))
    awp = ('weapon_awp', Model('models/weapons/w_snip_awp.mdl'))
    g3sg1 = ('weapon_g3sg1', Model('models/weapons/w_snip_g3sg1.mdl'))
    scar20 = ('weapon_scar20', Model('models/weapons/w_snip_scar20.mdl'))
    nova = ('weapon_scar20', Model('models/weapons/w_shot_nova.mdl'))
    xm1014 = ('weapon_scar20', Model('models/weapons/w_shot_xm1014.mdl'))
    choice = random.choice([m4a1,ak47,sg553,aug, awp, g3sg1, scar20, nova, xm1014])
    entity = Entity.create(choice[0])
    entity.model = choice[1]
    massScale = 1.0    

    entity.set_key_value_string("Damagetype", "1")
    entity.set_key_value_float("massScale", massScale * 8)

    entity.spawn()
    return entity
    
Base = declarative_base()
class DNDDBUser(Base):
    __tablename__ = 'DNDUSER'
    
    ID = sql.Column('ID', sql.Integer(), primary_key=True)
    STEAMID = sql.Column('STEAMID', sql.String(25))
    NAME = sql.Column('NAME', sql.String(30))
    LAST_PLAYED = sql.Column('LAST_PLAYED', sql.DateTime)
    
    def __repr__(self):
        return "<DNDUser(STEAMID='{0}', NAME='{1}', LAST_PLAYED='{2}')>".format(
                            self.STEAMID, self.NAME, self.LAST_PLAYED)

class DNDDBClass(Base):
    __tablename__ = 'DNDCLASS'
    
    ID = sql.Column('ID', sql.Integer(), primary_key=True)
    NAME = sql.Column('NAME', sql.String(25))
    
    def __repr__(self):
        return "<DNDClass(NAME='{0}')>".format(
            self.NAME)

class DNDDBXP(Base):
    __tablename__ = 'DNDXP'
    
    ID = sql.Column('ID', sql.Integer(), primary_key=True)     
    DNDUSERID = sql.Column('DNDUSERID', sql.Integer())
    DNDCLASSID = sql.Column('DNDCLASSID', sql.Integer())
    LEVEL = sql.Column('LEVEL', sql.Integer())
    XP = sql.Column('XP', sql.Integer())
        
    def __repr__(self):
        return "<DNDXP(DNDUSERID='{0}', DNDCLASSID='{1}', LEVEL='{2}', XP='{3}')>".format(
            self.DNDUSERID, self.DNDCLASSID, self.LEVEL, self.XP)
    
    
def saveWebDB(first=None):

    jsonDB = {}
    with open(databaseLocation, 'r') as f:
        jsonDB = json.load(f)
        
    dbCredentialsFile = join(dirname(__file__), 'databasecreds.txt')
    if not os.path.exists(dbCredentialsFile):
        return
        
    with open(dbCredentialsFile, 'r') as f:
        host = f.readline().strip()
        user = f.readline().strip()
        password = f.readline().strip()
        db = f.readline().strip()        
    
    messageServer('trying to connect')
    engine = sql.create_engine('mysql+pymysql://%s:%s@%s/%s'%(user,password,host,db))
    connection = engine.connect()    
        
    metadata = sql.MetaData()
    
    Base.metadata.create_all(engine)

    Session = sql.orm.sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    
    for dndclass in DNDClass.classes:
        
        if not session.query(DNDDBClass.NAME).filter_by(NAME=dndclass.name).scalar():
            #print('%s does not exist'%dndclass)
            newClass = DNDDBClass(NAME=dndclass.name)
            session.add(newClass)
    thread = GameThread(target=session.commit())
    thread.start()
    
    for steamid in jsonDB.keys():
        t = datetime.datetime.fromtimestamp(jsonDB[steamid]['Last Played'])
        if not session.query(DNDDBUser.STEAMID).filter_by(STEAMID=steamid).scalar():
            
            newPlayer = DNDDBUser(
                STEAMID=steamid, 
                NAME=jsonDB[steamid]['name'], 
                LAST_PLAYED=t
            )
            
            session.add(newPlayer)
            session.commit()
            
            for c in DNDClass.classes:
                cls = c.name
                    
                dndclass = session.query(DNDDBClass).filter_by(NAME=cls).first()
                
                newXP = DNDDBXP(
                    DNDUSERID=newPlayer.ID, 
                    DNDCLASSID=dndclass.ID, 
                    LEVEL=jsonDB[steamid][cls]['Level'], 
                    XP=jsonDB[steamid][cls]['XP']
                )
                
                session.add(newXP)
                session.commit()
        else:
            
            session.query(DNDDBUser).filter(
                    DNDDBUser.STEAMID == steamid
                ).update(
                { 
                    DNDDBUser.NAME : jsonDB[steamid]['name'], 
                    DNDDBUser.LAST_PLAYED : t 
                }, 
                synchronize_session='fetch')
            session.commit()
            
            for c in DNDClass.classes:
                cls = c.name
                dnduser = session.query(DNDDBUser).filter_by(STEAMID=steamid).first()
                dndclass = session.query(DNDDBClass).filter_by(NAME=cls).first()
                
                session.query(DNDDBXP).filter(
                        DNDDBXP.DNDUSERID == dnduser.ID, 
                        DNDDBXP.DNDCLASSID == dndclass.ID
                    ).update(
                    {
                        DNDDBXP.LEVEL : jsonDB[steamid][cls]['Level'],
                        DNDDBXP.XP : jsonDB[steamid][cls]['XP'],
                    }, 
                    synchronize_session='fetch')
                session.commit()
                thread = GameThread(target=session.commit())
                thread.start()
    messageServer('Web Info Updated')