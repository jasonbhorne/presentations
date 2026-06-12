-- Export a .pptx to PDF using Microsoft PowerPoint.
-- Args: <absolute POSIX path to .pptx> <output filename, lands in ~/Downloads>
-- Notes:
--  * PowerPoint is sandboxed: the `in` parameter needs a valid HFS path, so we
--    build it from `path to downloads folder` (a folder PowerPoint can write to).
--  * `open` does not return a usable reference in this build, so we read
--    `active presentation` after a short delay to let the document settle.
on run argv
  set inPath to item 1 of argv
  set outName to item 2 of argv
  try
    set dl to (path to downloads folder) as text
    set hfsOut to dl & outName
    with timeout of 600 seconds
      tell application "Microsoft PowerPoint"
        activate
        open (POSIX file inPath)
        delay 2
        set theDoc to active presentation
        save theDoc in hfsOut as save as PDF
        close theDoc saving no
      end tell
    end timeout
    return "DONE:" & hfsOut
  on error errMsg number errNum
    return "ERROR " & errNum & ": " & errMsg
  end try
end run
