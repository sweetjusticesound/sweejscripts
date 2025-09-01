-- JBSFX
-- joshadambell.com
-- Spot Media Explorer Selection Through Selected Track and Bake FX into Item (preserves whole file)
-- Takes the last played file from Media Explorer, places it on the selected track,
-- renders it through track/take FX, and trims the result to match Media Explorer time selection

function main()
    -- Get the currently selected track
    local track = reaper.GetSelectedTrack(0, 0)
    if not track then
        reaper.ShowMessageBox("Please select a track first", "Error", 0)
        return
    end
    
    -- Get media explorer last played file info using API documentation
    local retval, filename, filemode, selstart, selend, pitchshift, voladj, rateadj, sourcebpm, extrainfo = reaper.MediaExplorerGetLastPlayedFileInfo()

    if not retval then
        reaper.ShowMessageBox("No file selected in Media Explorer", "Error", 0)
        return
    end

    -- Begin undo block
    reaper.Undo_BeginBlock()
    
    -- Get current edit cursor position
    local cursor_pos = reaper.GetCursorPosition()
    
    -- Create new media item on the selected track at cursor position
    local item = reaper.AddMediaItemToTrack(track)
    local take = reaper.AddTakeToMediaItem(item)
    
    -- Set the source file for the take
    local source = reaper.PCM_Source_CreateFromFile(filename)
    if source then
        reaper.SetMediaItemTake_Source(take, source)
    else
        reaper.ShowMessageBox("Failed to create source from file", "Error", 0)
        return
    end
    
    -- Set item position at cursor
    reaper.SetMediaItemInfo_Value(item, "D_POSITION", cursor_pos)
    
    -- Set item length to full source length
    local source_length = reaper.GetMediaSourceLength(source, false)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", source_length)
    
    -- Set item name to just the filename (without path)
    local just_filename = filename:match("([^\\]+)$")
    reaper.GetSetMediaItemTakeInfo_String(take, "P_NAME", just_filename, true)
    
    -- Apply Media Explorer rate and volume settings BEFORE rendering FX
    reaper.SetMediaItemTakeInfo_Value(take, "D_PLAYRATE", rateadj)
    reaper.SetMediaItemTakeInfo_Value(take, "D_VOL", voladj)
    
    -- Select the item and render it through track/take FX (this bakes in the rate/volume)
    reaper.SetMediaItemSelected(item, true)
    reaper.Main_OnCommand(40209, 0) -- Item: Apply track/take FX to items
    
    -- Store original position for later restoration
    local original_position = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
    
    -- Remove the original take, keeping only the rendered one
    local original_take = reaper.GetMediaItemTake(item, 0)
    if original_take then
        reaper.GetSetMediaItemTakeInfo_String(original_take, "P_NAME", "", false)
        reaper.Main_OnCommand(40131, 0) -- Take: Delete active take from items
    end
    
    -- Get original source length for accurate percentage calculations
    local original_source = reaper.PCM_Source_CreateFromFile(filename)
    local full_source_length = reaper.GetMediaSourceLength(original_source, false)
    local rendered_take = reaper.GetActiveTake(item)
    
    -- Convert Media Explorer percentage-based selection to actual time values
    local actual_start_time = selstart * full_source_length
    local actual_end_time = selend * full_source_length
    local selection_length = actual_end_time - actual_start_time
    
    -- Adjust for playback rate: faster rate = shorter rendered duration
    local rate_adjusted_start_time = actual_start_time / rateadj
    local rate_adjusted_selection_length = selection_length / rateadj

    -- Trim item to Media Explorer time selection if one exists
    if selection_length > 0 and selection_length < full_source_length then
        -- reaper.ShowConsoleMsg("Trimming item to selection\n") -- Debug
        if rendered_take then
            -- Set item length using rate-adjusted duration
            reaper.SetMediaItemInfo_Value(item, "D_LENGTH", rate_adjusted_selection_length)
            
            -- Set take start offset using rate-adjusted start time
            reaper.SetMediaItemTakeInfo_Value(rendered_take, "D_STARTOFFS", rate_adjusted_start_time)
            
            -- Only apply pitch shift (rate and volume were baked in during render)
            reaper.SetMediaItemTakeInfo_Value(rendered_take, "D_PITCH", pitchshift)
            
            -- Reset rate and volume to default since they're now baked into the audio
            reaper.SetMediaItemTakeInfo_Value(rendered_take, "D_PLAYRATE", 1.0)
            reaper.SetMediaItemTakeInfo_Value(rendered_take, "D_VOL", 1.0)
            
            -- Restore item to original position
            reaper.SetMediaItemInfo_Value(item, "D_POSITION", original_position)
        end
    end
    
    -- Update the timeline
    reaper.UpdateTimeline()
    
    -- End undo block
    reaper.Undo_EndBlock("Spot Media Explorer selection through track with FX", -1)
end

-- Run the script
main()