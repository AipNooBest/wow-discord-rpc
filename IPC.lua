frame_count = 0
frames = {}

function IPC_CreateFrames()

    frame_count = GetScreenWidth()

    for i=1, frame_count do
        frames[i] = CreateFrame("Frame", nil, UIParent)
        frames[i]:SetFrameStrata("TOOLTIP")
        frames[i]:SetWidth(1)
        frames[i]:SetHeight(1)

        -- initialise it as black
        local t = frames[i]:CreateTexture(nil, "TOOLTIP")
        t:SetTexture(0, 0, 0, 0)
        t:SetAllPoints(frames[i])
        frames[i].texture = t

        frames[i]:SetPoint("TOPLEFT", (i - 1), 0)
        frames[i]:Show()
    end

    return frames
end

function IPC_PaintFrame(frame, r, g, b, force)
    -- turn them into black if they are null
    if r == nil then r = 0 end
    if g == nil then g = 0 end
    if b == nil then b = 0 end

    -- from 0-255 to 0.0-1.0
    r = r / 255
    g = g / 255
    b = b / 255

    -- set alpha to 1 if this pixel is black and force is 0 or null
    if r == 0 and g == 0 and b == 0 and (force == 0 or force == nil) then a = 0 else a = 1 end

    -- and now paint it
    frame.texture:SetTexture(r, g, b, a)
    frame.texture:SetAllPoints(frame)
end

function IPC_CleanFrames()
    for i=1, frame_count do
        IPC_PaintFrame(frames[i], 0, 0, 0, 0)
    end
end

function IPC_PaintSomething(text)
    --local max_bytes = (frame_count - 1) * 3
    --if text:len() >= max_bytes then
    --    return
    --end

    -- clean all
    IPC_CleanFrames()

    local squares_painted = 0

    for trio in text:gmatch".?.?.?" do
        r = 0; g = 0; b = 0
        r = string.byte(trio:sub(1,1))
        if #trio > 1 then g = string.byte(trio:sub(2,2)) end
        if #trio > 2 then b = string.byte(trio:sub(3,3)) end
        squares_painted = squares_painted + 1
        IPC_PaintFrame(frames[squares_painted*2-1], r, g, b)
    end
    squares_painted = 0
    for _ in text:gmatch".?.?.?" do
        squares_painted = squares_painted + 1
        IPC_PaintFrame(frames[squares_painted*2], 0, 0, 0, 1)
    end
    -- and then paint the last one white
    IPC_PaintFrame(frames[squares_painted*2-2], 255, 255, 255, 1)
end

function IPC_EncodeZoneType()
    local _, instanceType, _, difficultyName, _,
    _, _, _, _, _ = GetInstanceInfo()
    local locClass, engClass, locRace, _, _, playerName, _ = GetPlayerInfoByGUID(UnitGUID("player"))
    if locClass == nil then return "___" end
    local playerLevel = UnitLevel("player")
    local zoneName = GetRealZoneText()
    local subZone = GetSubZoneText()
    local memberCount = GetNumGroupMembers() -- Use GetNumPartyMembers() for <5.0.4
    local mapID, _ = GetCurrentMapAreaID()
    local details
    if zoneName == nil then zoneName = UnknownZoneName end
    if instanceType == 'party' then
        zoneName = string.format(zoneName .. '(%s)', difficultyName)
    elseif instanceType == 'raid' then
        zoneName = string.format(zoneName .. '(%s)', difficultyName)
    elseif instanceType == 'pvp' then
        zoneName = playerOnBattleGround
    else
        if UnitIsDeadOrGhost("player") and not UnitIsDead("player") then
            playerName = playerName .. playerIsDead
        end
        if subZone ~= "" then zoneName = zoneName .. ", " .. subZone end
    end
    if memberCount == 0 then
        local maxXP = UnitXPMax("player")
        local XP = UnitXP("player")
        if maxXP ~= 0 then
            if maxXP%100 ~= 0 then maxXP = string.format("%.01f", maxXP/1000) else maxXP = maxXP/1000 end
            if XP > 1000 then
                details = string.format("%.01f", XP/1000) .. "k" .. "/" .. maxXP .. "k XP"
            end
        else details = math.ceil(GetAverageItemLevel() - 0.5) .. itemLevel
        end
    else
        details = inGroupOfSomePeople()
    end
    local playerInfo = locRace .. ", " .. locClass
    return "$$$" .. zoneName .. "|" .. playerLevel .. "|" .. playerName .. "|" .. playerInfo .. "|" .. engClass .. "|" .. details .. "|" .. mapID .. "$$$"
end

-- received addon events.
function IPC_OnEvent(event, ...)
    if event == "PLAYER_LOGIN" then
        IPC_CreateFrames()
    elseif event == "PLAYER_LOGIN" or event == "ZONE_CHANGED_NEW_AREA" or event == "WORLD_MAP_UPDATE" then
        local encoded = IPC_EncodeZoneType()
        if encoded ~= nil then IPC_PaintSomething(encoded) end
    end
end

function IPC_OnLoad()
    IPCFrame:RegisterEvent("PLAYER_LOGIN")
    --IPCFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
    IPCFrame:RegisterEvent("ZONE_CHANGED_NEW_AREA")
    IPCFrame:RegisterEvent("WORLD_MAP_UPDATE")
    SlashCmdList["IPC"] = IPC_PaintSomething
    SLASH_IPC1 = "/ipc"
    SlashCmdList["CLEAN"] = IPC_CleanFrames
    SLASH_CLEAN1 = "/clean"
end