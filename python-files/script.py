-- Recoil Presets with vertical adjustments only
local recoilPresets = {
    {strength = 1, description = "low"},
    {strength = 2, description = "medium"},
    {strength = 3, description = "high"}
}
 
local selectedPresetIndex = 1
local noRecoilEnabled = true
 
function OnEvent(event, arg)
    OutputLogMessage("event = %s, arg = %s\n", event, arg)
 
    -- Enable Mouse Button Events when profile is activated
    if (event == "PROFILE_ACTIVATED") then
        EnablePrimaryMouseButtonEvents(true)
    end
 
    -- Toggle No Recoil on/off with Mouse Button 7
    if (event == "MOUSE_BUTTON_PRESSED" and arg == 7) then
        noRecoilEnabled = not noRecoilEnabled
        if (noRecoilEnabled) then
            OutputLogMessage("[+] No recoil is on\n")
        else
            OutputLogMessage("[-] No recoil is off\n")
        end
    end
 
    -- Cycle through recoil presets with Mouse Button 5
    if (event == "MOUSE_BUTTON_PRESSED" and arg == 5) then
        selectedPresetIndex = (selectedPresetIndex % #recoilPresets) + 1
        OutputLogMessage("[+] Selected recoil preset: %s\n", recoilPresets[selectedPresetIndex].description)
    end
 
    -- Apply recoil compensation when Mouse 1 (shoot) and Mouse 3 (ADS) are pressed
    if (noRecoilEnabled and event == "MOUSE_BUTTON_PRESSED" and arg == 1 and IsMouseButtonPressed(1) and IsMouseButtonPressed(3)) then
        local recoil = recoilPresets[selectedPresetIndex]
 
        -- Apply recoil compensation in a continuous loop
        repeat
            -- Apply vertical recoil (downwards) at the selected strength
            MoveMouseRelative(0, recoil.strength)  -- Vertical recoil only (no horizontal)
 
            Sleep(14)  -- Small delay to control the speed of recoil compensation
        until not (IsMouseButtonPressed(1) and IsMouseButtonPressed(3))  -- Stop when Mouse 1 and Mouse 3 are released
    end
end