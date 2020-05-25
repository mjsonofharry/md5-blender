param(
    [String]$blender_path="C:\Program Files (x86)\Steam\steamapps\common\Blender",
    [String]$blender_version="2.82"
)

$project_path = (get-item $PSScriptRoot).parent.FullName
$sources_path = "$project_path\md5model"

$install_path = "$blender_path\$blender_version\scripts\addons\io_scene_md5model"
If (Test-Path $install_path) {
    Remove-Item -Path $install_path -Recurse -Force
}

New-Item -Path $install_path -ItemType directory -Force
New-Item -Path $install_path\plugin -ItemType directory -Force
Copy-Item -Path $sources_path\*.py -Destination $install_path -Force
Copy-Item -Path $sources_path\plugin\*.py -Destination $install_path\plugin -Force