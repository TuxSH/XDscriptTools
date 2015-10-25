# See LICENSE for license
"""
FunctionInfo

List of operators (complete) and class methods 

**Priority of types when implicitely converting**:
       string < int < float < (not always convertible, like for ex. in the vector methods) vector

**Calling convention for operators**:

	(top of stack)
	param 2 (if it exists)
	param 1

=>

	(top of stack) 
	result

**Calling convention for script functions and methods**:
	(top of stack)
	etc ...
	param 1
	param 2

=>
	result in $lastResult (for standard functions/methods, this is int(0) by default (i.e unless otherwise mentionned))

^This applies for both standard (callstd) and script-coded (call) function calls
	
Only the first class (clsID = 0, which is not really a class) does not need a first parameter, but uses 'reserve 0' nevertheless.

All other classes need a instance, be it fake or not. Fake instances are either uninitialized local variables (created along with other local variables,
with 'reserve n'), or most of the time, (still unitialized) singletons (refer to Instruction).

For a script function, the stack has the following layout:

	local variable no. n
	...
	local variable no. 0
	return address			($stack[0])
	parameter no. 1
	...
	parameter no. n
	(etc ...)


Special callbacks:
(signature : 4 ints)

	Map scripts:
		pushpop_postprocess,
		modify_floor,
		preprocess,
		hero_main,
		postprocesss,
		pushpop_preprocess,
		talk_follower,
		sound,
		anywaysave_callback, (when trying to save)
		anywaysave_restart, (when saving map data)
		etc...

	Common script:
	(need to be verified)
		Function #8 (0x59600008): when the map starts to change
		Function #9 (0x59600009): when the map finishes to change
"""
import collections

OperatorInfo = collections.namedtuple("OperatorInfo", "name index nbOperands")
FunctionInfo = collections.namedtuple("FunctionInfo", "name index nbParams variadic")
ClassInfo = collections.namedtuple("ClassInfo", "name index funcs")

Category = collections.namedtuple("Category", "name start nb")



operators = (
	#------------------------------------------------------------------
	Category(name = "Unary operators", start = 16, nb = 10),

	OperatorInfo(name = "not", index = 16, nbOperands = 1),
	OperatorInfo(name = "neg", index = 17, nbOperands = 1),
	OperatorInfo(name = "hex", index = 18, nbOperands = 1),
	OperatorInfo(name = "str", index = 19, nbOperands = 1),
	OperatorInfo(name = "int", index = 20, nbOperands = 1),
	OperatorInfo(name = "float", index = 21, nbOperands = 1),
	OperatorInfo(name = "getvx", index = 22, nbOperands = 1),
	OperatorInfo(name = "getvy", index = 23, nbOperands = 1),
	OperatorInfo(name = "getvz", index = 24, nbOperands = 1),
	OperatorInfo(name = "zerofloat", index = 25, nbOperands = 1), # always returns 0.0 ...
	#------------------------------------------------------------------
	Category(name = "Binary non-comparison operators", start = 32, nb = 8),

	OperatorInfo(name = "xor", index = 32, nbOperands = 2),
	OperatorInfo(name = "or",  index = 33, nbOperands = 2),
	OperatorInfo(name = "and", index = 34, nbOperands = 2),
	OperatorInfo(name = "add", index = 35, nbOperands = 2), # str + str is defined => concatenation
	OperatorInfo(name = "sub", index = 36, nbOperands = 2),
	OperatorInfo(name = "mul", index = 37, nbOperands = 2), # int * str or str * int is defined. For vectors = <a,b,c>*<c,d,e> = <a*c, b*d, c*e> 
	OperatorInfo(name = "div", index = 38, nbOperands = 2), # you cannot /0 for ints and floats but for vectors you can ... 
	OperatorInfo(name = "mod", index = 39, nbOperands = 2), # operands are implicitly converted to int, if possible.
	#------------------------------------------------------------------
	Category(name = "Comparison operators", start = 48, nb = 6),

	OperatorInfo(name = "equ", index = 48, nbOperands = 2), # For string equality comparison: '?' every character goes, '*' everything goes after here
	OperatorInfo(name = "gt", index = 49, nbOperands = 2), # ordering of strings is done comparing their respective lengths
	OperatorInfo(name = "ge", index = 50, nbOperands = 2),
	OperatorInfo(name = "lt", index = 51, nbOperands = 2),
	OperatorInfo(name = "le", index = 52, nbOperands = 2),
	OperatorInfo(name = "neq", index = 53, nbOperands = 2)
	#------------------------------------------------------------------
)

#======================================================================================
#======================================================================================
#======================================================================================

classes = (
	#======================================================================================
	ClassInfo(name = "", index = 0, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Timer-related functions", start = 17, nb = 6),

		FunctionInfo(name = "pause", index = 17, nbParams = 1, variadic = False),
		FunctionInfo(name = "yield", index = 18, nbParams = 1, variadic = False), # nb of consecutive yields
		FunctionInfo(name = "setTimer", index = 19, nbParams = 1, variadic = False),
		FunctionInfo(name = "getTimer", index = 20, nbParams = 1, variadic = False),
		FunctionInfo(name = "waitUntil", index = 21, nbParams = 2, variadic = False), # timerNb (0,1,2 or 3), timerValue (seconds as float)
		FunctionInfo(name = "printString", index = 22, nbParams = 1, variadic = False),
		#------------------------------------------------------------------------------------
		Category(name = "String and bit manipulation functions", start = 29, nb = 8),

		FunctionInfo(name = "typename", index = 29, nbParams = 1, variadic = False), # A bit inconsistent (well, most results seem invalid)
		FunctionInfo(name = "getCharacter", index = 30, nbParams = 2, variadic = False), # (str, index)
		FunctionInfo(name = "setCharacter", index = 31, nbParams = 1, variadic = False),
		FunctionInfo(name = "findSubstring", index = 32, nbParams = 2, variadic = False), #BUGGED, returns -1
		FunctionInfo(name = "setBit", index = 33, nbParams = 2, variadic = False),
		FunctionInfo(name = "clearBit", index = 34, nbParams = 2, variadic = False),
		FunctionInfo(name = "mergeBits", index = 35, nbParams = 2, variadic = False),
		FunctionInfo(name = "nand", index = 36, nbParams = 2, variadic = False),
		#------------------------------------------------------------------------------------
		Category(name = "Math functions", start = 48, nb = 6),

		FunctionInfo(name = "sin", index = 48, nbParams = 1, variadic = False), # trigo. function below work with degrees
		FunctionInfo(name = "cos", index = 49, nbParams = 1, variadic = False),
		FunctionInfo(name = "tan", index = 50, nbParams = 1, variadic = False),
		FunctionInfo(name = "atan2", index = 51, nbParams = 1, variadic = False),
		FunctionInfo(name = "acos", index = 52, nbParams = 1, variadic = False),
		FunctionInfo(name = "sqrt", index = 53, nbParams = 1, variadic = False),
		#------------------------------------------------------------------------------------
		Category(name = "Functions manipulating a single flag", start = 129, nb = 5),

		FunctionInfo(name = "setFlagToTrue", index = 129, nbParams = 1, variadic = False),
		FunctionInfo(name = "setFlagToFalse", index = 130, nbParams = 1, variadic = False),
		FunctionInfo(name = "setFlag", index = 131, nbParams = 1, variadic = False),
		FunctionInfo(name = "checkFlag", index = 132, nbParams = 1, variadic = False),
		FunctionInfo(name = "getFlag", index = 133, nbParams = 1, variadic = False),
		
		#------------------------------------------------------------------------------------
		Category(name = "Misc. 1", start = 136, nb = 5),

		FunctionInfo(name = "printf", index = 136, nbParams = 1, variadic = True),
		FunctionInfo(name = "rand", index = 137, nbParams = 0, variadic = False),
		FunctionInfo(name = "setShadowPkmStatus", index = 138, nbParams = 2, variadic = False),
		FunctionInfo(name = "checkMultiFlagsInv", index = 139, nbParams = 1, variadic = True),
		FunctionInfo(name = "checkMultiFlags", index = 140, nbParams = 1, variadic = True),
		#------------------------------------------------------------------------------------
		Category(name = "Debugging functions", start = 142, nb = 2),

		FunctionInfo(name = "syncTaskFromLibraryScript", index = 142, nbParams = 3, variadic = True), #nbArgs, function ID, ... (args)
		FunctionInfo(name = "setDebugMenuVisibility", index = 143, nbParams = 1, variadic = False), # not sure it works on release builds

		Category(name = "Misc. 2", start = 145, nb = 16),

		FunctionInfo(name = "setPreviousMapID", index = 145, nbParams = 1, variadic = False), # the game uses the term "floor"
		FunctionInfo(name = "getPreviousMapID", index = 146, nbParams = 0, variadic = False),
		FunctionInfo(name = "unknownFunction147", index = 147, nbParams = 2, variadic = False), # (int, float)
		FunctionInfo(name = "getPkmSpeciesName", index = 148, nbParams = 1, variadic = False),
		FunctionInfo(name = "unknownFunction147", index = 149, nbParams = 1, variadic = False), # some map related function; returns a reference to a character
		FunctionInfo(name = "speciesRelatedFunction148", index = 150, nbParams = 1, variadic = False), # take the species index as arg
		FunctionInfo(name = "getPkmRelatedArrayElement", index = 151, nbParams = 1, variadic = False), # (array, index)
		FunctionInfo(name = "unknownFunction152", index = 152, nbParams = 1, variadic = False), 
		FunctionInfo(name = "distance", index = 153, nbParams = 2, variadic = False),  # between the two points whose coordinates are the vector args
		FunctionInfo(name = "unknownFunction154", index = 154, nbParams = 1, variadic = False), # (character), returns 0 by default
		FunctionInfo(name = "unknownFunction155", index = 155, nbParams = 6, variadic = False),  # (float, int, int, int, int, int) -> 0
		FunctionInfo(name = "GCComListenerDestroy", index = 154, nbParams = 0, variadic = False), # so says Dolphin-Emu
		FunctionInfo(name = "unknownFunction155", index = 155, nbParams = 5, variadic = False),  # (int, float, float, float, float) -> 0
		FunctionInfo(name = "unknownFunction156", index = 156, nbParams = 1, variadic = False), # return type: (int) -> character
		FunctionInfo(name = "getScreenResfreshRate", index = 157, nbParams = 0, variadic = False), # FPS as float
		FunctionInfo(name = "getRegion", index = 158, nbParams = 0, variadic = False),
		FunctionInfo(name = "getLanguage", index = 159, nbParams = 0, variadic = False)
	)),


	ClassInfo(name = "Vector", index = 4, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Type conversions", start = 3, nb = 1),

		FunctionInfo(name = "toString", index = 3, nbParams = 1, variadic = False),
		#------------------------------------------------------------------------------------

		Category(name = "Methods", start = 16, nb = 13),

		FunctionInfo(name = "clear", index = 16, nbParams = 1, variadic = False),
		FunctionInfo(name = "normalize", index = 17, nbParams = 1, variadic = False),
		FunctionInfo(name = "set", index = 18, nbParams = 4, variadic = False),
		FunctionInfo(name = "set2", index = 19, nbParams = 4, variadic = False),
		FunctionInfo(name = "fill", index = 20, nbParams = 2, variadic = False),
		FunctionInfo(name = "abs", index = 21, nbParams = 1, variadic = False), #in place
		FunctionInfo(name = "negate", index = 22, nbParams = 1, variadic = False), #in place
		FunctionInfo(name = "isZero", index = 23, nbParams = 1, variadic = False),
		FunctionInfo(name = "crossProduct", index = 24, nbParams = 2, variadic = False),
		FunctionInfo(name = "dotProduct", index = 25, nbParams = 2, variadic = False),
		FunctionInfo(name = "norm", index = 26, nbParams = 1, variadic = False),
		FunctionInfo(name = "squaredNorm", index = 27, nbParams = 1, variadic = False),
		FunctionInfo(name = "angle", index = 28, nbParams = 2, variadic = False)
	)),


	ClassInfo(name = "Array", index = 7, funcs = (
		#------------------------------------------------------------------------------------
		FunctionInfo(name = "invalidFunction0", index = 0, nbParams = None, variadic = None),
		FunctionInfo(name = "invalidFunction1", index = 1, nbParams = None, variadic = None),
		FunctionInfo(name = "invalidFunction2", index = 2, nbParams = None, variadic = None),
		#------------------------------------------------------------------------------------
		Category(name = "Type conversions", start = 3, nb = 1),

		FunctionInfo(name = "toString", index = 3, nbParams = 1, variadic = False),
		#------------------------------------------------------------------------------------
		Category(name = "Methods (1)", start = 16, nb = 5),

		FunctionInfo(name = "get", index = 16, nbParams = 2, variadic = False),
		FunctionInfo(name = "set", index = 17, nbParams = 3, variadic = False),
		FunctionInfo(name = "size", index = 18, nbParams = 1, variadic = False),
		FunctionInfo(name = "resize", index = 19, nbParams = 2, variadic = False), #REMOVED
		FunctionInfo(name = "extend", index = 20, nbParams = 2, variadic = False), #REMOVED
		#------------------------------------------------------------------------------------
		Category(name = "Methods (2) : iterator functions", start = 22, nb = 4),

		FunctionInfo(name = "resetIterator", index = 22, nbParams = 1, variadic = False),
		FunctionInfo(name = "derefIterator", index = 23, nbParams = 2, variadic = False),
		FunctionInfo(name = "getIteratorPos", index = 24, nbParams = 2, variadic = False),
		FunctionInfo(name = "append", index = 25, nbParams = 2, variadic = True) #REMOVED
	)),


	ClassInfo(name = "UnknownClass33", index = 33, funcs = (None,)),
	
	ClassInfo(name = "Character", index = 35, funcs = (
		# The biggest class out there, there are 99 functions

		#------------------------------------------------------------------------------------
		Category(name = "Known methods", start = 16, nb=-1),

		FunctionInfo(name = "setVisibility", index = 16, nbParams = 2, variadic = False), # (int visible)
		FunctionInfo(name = "displayMsgWithSpeciesSound", index = 21, nbParams = 2, variadic = False), # (int msgID, int unk ?)
		# Uses the species cry from Dialogs::setMsgVar($dialogs, 50, species)

		FunctionInfo(name = "setCharacterFlags", index = 40, nbParams = 2, variadic = False), # (int flags ?) 
		FunctionInfo(name = "clearCharacterFlags", index = 41, nbParams = 2, variadic = False), # (int flags ?)  

		FunctionInfo(name = "talk", index = 73, nbParams = 2, variadic = True), # (int type, ...)
		# Some type of character dialogs (total: 22):
		# (Valid values for type : 1-3, 6-21). 
		#	(1, msgID): normal msg
		#	(2, msgID): the character comes at you, then talks, then goes away (to be verified; anyways he/she moves)
		#	(8, msgID): yes/no question
		#	(15, species): plays the species' cry
		#	(16, msgID): informative dialog with no sound

	)),

	ClassInfo(name = "Pokemon", index = 37, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Known methods", start = 16, nb=-1),

		FunctionInfo(name = "playSpecifiedSpeciesCry", index = 16, nbParams = 2, variadic = False), # (int species)

		FunctionInfo(name = "playCry", index = 16, nbParams = 1, variadic = False),

		FunctionInfo(name = "getPokeballCaughtWith", nbParams = 1, index = 21, variadic = False),
		FunctionInfo(name = "getNickname", nbParams = 1, index = 22, variadic = False),

		# index = 23 does not exist

		FunctionInfo(name = "isShadow", index = 24, nbParams = 1, variadic = False),

		FunctionInfo(name = "getCurrentHP", index  = 26, nbParams = 1, variadic = False),
		FunctionInfo(name = "getCurrentPurifCtr", index = 27, nbParams = 1, variadic = False),
		FunctionInfo(name = "getSpeciesIndex", index = 28, nbParams = 1, variadic = False),
		FunctionInfo(name = "isLegendary", index = 29, nbParams = 1, variadic = False),
		FunctionInfo(name = "getHappiness", index = 30, nbParams = 1, variadic = False),
		FunctionInfo(name = "getSomeSpeciesRelatedIndex", index = 31, nbParams = 1, variadic = False), # if it's 0 the species is invalid
		FunctionInfo(name = "getHeldItem", index = 32, nbParams = 1, variadic = False),
		FunctionInfo(name = "getSIDTID", index = 33, nbParams = 1, variadic = False),


	)),
	ClassInfo(name = "UnknownClass38", index = 38, funcs = (None,)),

	ClassInfo(name = "Tasks", index = 39, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Task creation functions", start = 16, nb = 4),
		# Function IDs : if (id & 0x59600000) != 0 : current script, otherwise common script (mask = 0x10000000 iirc)

		FunctionInfo(name = "createSyncTaskByID", index = 16, nbParams = 6, variadic = False), # (functionID, then 4 ints passed as parameters)
		FunctionInfo(name = "createSyncTaskByName", index = 17, nbParams = 6, variadic = False), # the function is selected by its name in the CURRENT script.
																								# HEAD sec. must be present
		FunctionInfo(name = "createAsyncTaskByID", index = 18, nbParams = 6, variadic = False), # (functionID, then 4 ints passed as parameters)
		FunctionInfo(name = "createAsyncTaskByName", index = 19, nbParams = 6, variadic = False), # the function is selected by its name in the CURRENT script.
																								  # HEAD sec. must be present

		FunctionInfo(name = "getLastReturnedInt", index = 20, nbParams = 1, variadic = False),
		FunctionInfo(name = "sleep", index = 21, nbParams = 2, variadic = False) # (float) (miliseconds)
	)),

	ClassInfo(name = "Dialogs", index = 40, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Known methods", start = 16, nb=-1),

		FunctionInfo(name = "displatSilentMsgBox", index = 16, nbParams = 4, variadic = False), # (int msgID, int isInForeground, int dontDisplayCharByChar) 
		FunctionInfo(name = "displayMsgBox", index = 17, nbParams = 5, variadic = False), # (int msgID, int isInForeground, int dontDisplayCharByChar,
																		# int textSoundPitchLevel)
		FunctionInfo(name = "displayYesNoQuestion", index = 21, nbParams = 2, variadic = False), # (int msgID)

		FunctionInfo(name = "setMsgVar", index = 28, nbParams = 3, variadic = False), # (int type, var val)
		
		FunctionInfo(name = "promptPartyPokemon2", index = 32, nbParams = 1, variadic = False), # these functions are **exactly** the same
		FunctionInfo(name = "promptPartyPokemon", index = 33, nbParams = 1, variadic = False),
		FunctionInfo(name = "openPokemonSummary", index = 34, nbParams = 1, variadic = False), # no arg ...

		FunctionInfo(name = "promptName", index = 36, nbParams = 2, variadic = False), # (int forWho, var target, int mode)
		# forWho: 0 for Player, 1 for Sister, 2 for Poké. mode: 0 = enter pkm name, 1 = player name, 2 = sister name (not verified) 
		FunctionInfo(name = "doOpenNamePrompt", index = 37, nbParams = 3, variadic = False), # used by the common script only. Don't use this otherwise

		FunctionInfo(name = "openPokemartMenu", index = 39, nbParams = 2, variadic = False), # (int)
		
		FunctionInfo(name = "openPADMenu", index = 41, nbParams = 1, variadic = False),
		FunctionInfo(name = "yesOrNoPrompt", index = 42, nbParams = 1, variadic = False),

		FunctionInfo(name = "openItemMenu", index = 50, nbParams = 1, variadic = False),

		FunctionInfo(name = "moveRelearner", index = 64, nbParams = 2, variadic = False), # (int partyIndex)

		FunctionInfo(name = "openMoneyWindow", index = 67, nbParams = 3, variadic = False), # (int x, int y)
		FunctionInfo(name = "closeMoneyWindow", index = 68, nbParams = 1, variadic = False),
		
		FunctionInfo(name = "openPkCouponsWindow", index = 70, nbParams = 3, variadic = False), # (int x, int y)
		FunctionInfo(name = "closePkCouponsWindow", index = 71, nbParams = 1, variadic = False),

	)),
	
	ClassInfo(name = "Transition", index = 41, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Methods", start = 16, nb = 2),

		FunctionInfo(name = "setup", index = 16, nbParams = 3, variadic = False), #$transition, int flags, float duration
		FunctionInfo(name = "checkStatus", index = 17, nbParams = 2, variadic = False) #$transition, int waitForCompletion
	)),
	
	ClassInfo(name = "UnknownClass42", index = 42, funcs = (None,)),
	ClassInfo(name = "Player", index = 43, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Known methods", start = 16, nb=-1),

		FunctionInfo(name = "processEvents", index = 17, nbParams = 1, variadic = False), # MUST BE CALLED IN THE IDLE LOOP (usually 'hero_main')

		FunctionInfo(name = "receiveMoney", index = 29, nbParams = 2, variadic = False), # (int amount) (can be < 0)
		FunctionInfo(name = "getMoney", index = 30, nbParams = 1, variadic = False),
		
		FunctionInfo(name = "countPartyPkm", index = 34, nbParams = 1, variadic = False), # (int amount)
		FunctionInfo(name = "countShadowPartyPkm", index = 35, nbParams = 1, variadic = False), # (int amount)

		FunctionInfo(name = "getPartyPkmNameAsStr", index = 36, nbParams = 2, variadic = False), # (int partyIndex)

		FunctionInfo(name = "receiveGiftOrEventPkm", index = 37, nbParams = 2, variadic = False), # (int ID)
		# 1 to 14: 
		# Male Jolteon (cannot be shiny), Male Vaporeon (cannot), Duking's Plusle (cannot),
		# Mt. Battle Ho-oh (cannot), Bonus Disc Pikachu (cannot), AGETO Celebi (cannot)
		# 
		# shadow Togepi (XD) (cannot be shiny), Elekid (can), Meditite (can), Shuckle (can), Larvitar (can),
		# Chikorita (can), Cyndaquil (can), Totodile (can)

		FunctionInfo(name = "countPurifiablePartyPkm", index = 38, nbParams = 1, variadic = False),
		FunctionInfo(name = "healParty", index = 39, nbParams = 1, variadic = False),
		FunctionInfo(name = "startGroupBattle", index = 40, nbParams = 2, variadic = False), # (int)
		FunctionInfo(name = "countNotFaintedPartyPkm", index = 41, nbParams = 1, variadic = False),
		FunctionInfo(name = "getFirstInvalidPartyPkmIndex", index = 42, nbParams = 1, variadic = False), # -1 if no invalid pkm
		FunctionInfo(name = "countValidPartyPkm", index = 43, nbParams = 1, variadic = False),
		FunctionInfo(name = "getPartyPkm", index = 44, nbParams = 2, variadic = False), # (int index)
		FunctionInfo(name = "checkPkmOwnership", index = 45, nbParams = 2, variadic = False), # (int index)

		FunctionInfo(name = "isPCFull", index = 52, nbParams = 1, variadic = False),
		FunctionInfo(name = "countLegendaryPartyPkm", index = 53, nbParams = 1, variadic = False),

		FunctionInfo(name = "countPurfiedPkm", index = 59, nbParams = 1, variadic = False),
		FunctionInfo(name = "awardMtBattleRibbons", index = 60, nbParams = 1, variadic = False),
		FunctionInfo(name = "getPkCoupons", index = 61, nbParams = 1, variadic = False),
		FunctionInfo(name = "setPkCoupons", index = 62, nbParams = 2, variadic = False), # (int nb)
		FunctionInfo(name = "receivePkCoupons", index = 63, nbParams = 2, variadic = False), # (int amount) (can be < 0)
		FunctionInfo(name = "countShadowPkm", index = 64, nbParams = 1, variadic = False),

		FunctionInfo(name = "isSpeciesInPC", index = 68, nbParams = 2, variadic = False), # (int species)
		FunctionInfo(name = "releasePartyPkm", index = 69, nbParams = 2, variadic = False), # (int index). Returns 1 iff there was a valid Pokémon, 0 otherwise.
		

	)),

	ClassInfo(name = "UnknownClass44", index = 44, funcs = (None,)),
	ClassInfo(name = "UnknownClass45", index = 45, funcs = (None,)),
	ClassInfo(name = "UnknownClass46", index = 46, funcs = (None,)),
	ClassInfo(name = "Sound", index = 47, funcs = (None,)),
	ClassInfo(name = "UnknownClass48", index = 48, funcs = (None,)),
	ClassInfo(name = "UnknownClass49", index = 49, funcs = (None,)),
	ClassInfo(name = "UnknownClass50", index = 50, funcs = (None,)),
	ClassInfo(name = "UnknownClass51", index = 51, funcs = (None,)),

	ClassInfo(name = "Daycare", index = 52, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Methods (1) ", start = 16, nb = 4),

		FunctionInfo(name = "getLevelsGained", index = 17, nbParams = 1, variadic = False),
		FunctionInfo(name = "getNbOfHundredsOfShadowCtrLost", index = 18, nbParams = 1, variadic = False), # int((shadowPkmCounter - initialShadowPkmCounter)/100)
		FunctionInfo(name = "depositPkm", index = 19, nbParams = 2, variadic = False),
		FunctionInfo(name = "withdrawPkm", index = 20, nbParams = 2, variadic = False),
		#------------------------------------------------------------------------------------
		Category(name = "Methods (2) : checking the daycare status", start = 21, nb = 3),

		FunctionInfo(name = "calculateCost", index = 21, nbParams = 2, variadic = False), # Cost of daycare : 100*(1 + (currentLevel - initialLevel) + 1 + 
																						  # int((purifCtr - initialPurifCtr)/100)) 
																						  # or 100*(1 + currentLevel - initialLvl) if (purifCtr - initialPurifCtr) < 100. 
																						  # 0 if status != PkmDeposited
		FunctionInfo(name = "checkDaycareStatus", index = 22, nbParams = 1, variadic = False), # NotVisited (or any other unassigned value) = -1,  
																							   # NoPkmDeposited = 0, PkmDeposited = 1  
		FunctionInfo(name = "getPkm", index = 22, nbParams = 1, variadic = False)
	)),
	
	ClassInfo(name = "TaskManager", index = 54, funcs = (
		#------------------------------------------------------------------------------------
		Category(name = "Methods", start = 16, nb = 8),

		FunctionInfo(name = "allocateTask", index = 16, nbParams = 2, variadic = False), # returns taskUID ... allocates a task but seems to do nothing ... BROKEN ?
		FunctionInfo(name = "zeroFunction17", index = 17, nbParams = 1, variadic = False), # arg : taskUID
		FunctionInfo(name = "getTaskCounter", index = 18, nbParams = 1, variadic = False),
		FunctionInfo(name = "stopTask", index = 19, nbParams = 2, variadic = False), # unusable
		FunctionInfo(name = "unknownFunction20", index = 20, nbParams = 2, variadic = False), #set
		FunctionInfo(name = "unknownFunction21", index = 21, nbParams = 2, variadic = False), #get
		FunctionInfo(name = "unknownFunction22", index = 22, nbParams = 3, variadic = False),
		FunctionInfo(name = "unknownFunction23", index = 23, nbParams = 3, variadic = False)
	)),

	ClassInfo(name = "UnknownClass58", index = 58, funcs = (None,)),
	ClassInfo(name = "ShadowPokemons", index = 59, funcs = (
	   #------------------------------------------------------------------------------------
		Category(name = "Methods", start = 16, nb = 8),

		# Shadow Pkm status: 
						# 0 : not seen
						# 1 : seen, as spectator (not battled against)
						# 2 : seen and battled against
						# 3 : caught
						# 4 : purified
		FunctionInfo(name = "isShadowPkmPurified", index = 16, nbParams = 2, variadic = False),
		FunctionInfo(name = "isShadowPkmCaught", index = 17, nbParams = 2, variadic = False),
		FunctionInfo(name = "setShadowPkmStatus", index = 18, nbParams = 3, variadic = False),
		FunctionInfo(name = "getShadowPkmSpecies", index = 19, nbParams = 2, variadic = False),
		FunctionInfo(name = "getShadowPkmStatus", index = 20, nbParams = 2, variadic = False),
		FunctionInfo(name = "unknownFunction21", index = 21, nbParams = 2, variadic = False),
		FunctionInfo(name = "setShadowPkmStorageUnit", index = 22, nbParams = 4, variadic = False), # (int index, int subIndex)


	)),
	ClassInfo(name = "UnknownClass60", index = 60, funcs = (None,))

	#------------------------------------------------------------------------------------
	#======================================================================================
)

#======================================================================================
#======================================================================================
#======================================================================================

operators_name_dict = { entry.index: entry.name for entry in operators if isinstance(entry, OperatorInfo) }

stdfunctions_name_dict = { c.index: (c.name, 
								{ f.index: f.name for f in c.funcs if isinstance(f, FunctionInfo)} if c.funcs is not None else {}
								) for c in classes if isinstance(c, ClassInfo) 
					 }

def getOperatorName(index):
	return operators_name_dict.get(index, str(index))

def getStdFunctionName(clsID, funcID):
	if stdfunctions_name_dict.get(clsID) is None:
		return "{0}::{1}".format(clsID, funcID)
	else:
		cls_info = stdfunctions_name_dict[clsID]
		if clsID == 0:
			return cls_info[1].get(funcID, str(funcID))
		else:
			return "{0}::{1}".format(cls_info[0], cls_info[1].get(funcID, str(funcID))) 