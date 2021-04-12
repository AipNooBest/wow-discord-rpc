unknownZoneName = "Unknown"
playerOnBattleGround = "In battleground"
playerIsDead = " (Dead)"
itemLevel = " item level"
function inGroupOfSomePeople()
    return "In group of " .. GetNumGroupMembers() .. " people" end -- Use GetNumPartyMembers()+1 [didn't test yet for +1 thing] for <5.0.4