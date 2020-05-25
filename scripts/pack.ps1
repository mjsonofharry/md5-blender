$project_path = (get-item $PSScriptRoot).parent.FullName
$sources_path = "$project_path\md5model"

$tmp_path = "$project_path\scripts\io_scene_md5model"
If (Test-Path $tmp_path) {
    Remove-Item -Path $tmp_path -Recurse -Force
}
New-Item -Path $tmp_path -ItemType directory -Force
New-Item -Path $tmp_path\plugin -ItemType directory -Force
Copy-Item -Path $sources_path\*.py -Destination $tmp_path -Force
Copy-Item -Path $sources_path\plugin\*.py -Destination $tmp_path\plugin -Force

$zip_path = "$project_path\io_scene_md5model.zip"
If (Test-Path $zip_path) {
    Remove-Item -Path $zip_path -Force
}
Compress-Archive -Path $tmp_path\* -DestinationPath $zip_path
Remove-Item -Path $tmp_path -Recurse -Force
