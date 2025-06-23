import os
import zipfile

# Define the folder structure
project_name = "MRTK_HoloLens_Android_iOS_AR"
structure = [
    f"{project_name}/Assets/MRTK/",
    f"{project_name}/Assets/ARFoundation/",
    f"{project_name}/Assets/Scenes/",
    f"{project_name}/Packages/",
    f"{project_name}/ProjectSettings/"
]

# Content for manifest.json
manifest_content = """{
  "dependencies": {
    "com.unity.xr.arcore": "5.1.0",
    "com.unity.xr.arkit": "5.1.0",
    "com.unity.xr.arsubsystems": "5.1.0",
    "com.unity.xr.management": "4.4.0",
    "com.unity.xr.openxr": "1.9.1",
    "com.microsoft.mrtk.core": "3.0.0-pre.17",
    "com.microsoft.mrtk.input": "3.0.0-pre.17",
    "com.microsoft.mrtk.ux": "3.0.0-pre.17",
    "com.microsoft.mrtk.tools": "3.0.0-pre.17",
    "com.microsoft.mrtk.graphics.tools": "3.0.0-pre.17",
    "com.unity.inputsystem": "1.6.1"
  },
  "registry": "https://packages.unity.com",
  "scopedRegistries": [
    {
      "name": "Microsoft Mixed Reality",
      "url": "https://pkgs.dev.azure.com/UnityMixedReality/UnityMixedReality/_packaging/MixedRealityToolkit%403/npm/registry/",
      "scopes": [
        "com.microsoft.mrtk"
      ]
    }
  ]
}
"""

# Content for ProjectVersion.txt
project_version_content = """m_EditorVersion: 2022.3.0f1
m_EditorVersionWithRevision: 2022.3.0f1 (0b819aca6f6d)
"""

# Create the zip
zip_filename = f"{project_name}.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for folder in structure:
        zipf.writestr(f"{folder}", "")
    zipf.writestr(f"{project_name}/Packages/manifest.json", manifest_content)
    zipf.writestr(f"{project_name}/ProjectSettings/ProjectVersion.txt", project_version_content)
    zipf.writestr(f"{project_name}/.gitignore", "*.csproj\n*.sln\nLibrary/\nTemp/\nobj/\nBuild/\nLogs/\n")
    zipf.writestr(f"{project_name}/MRTK_ReadMe.md", "# MRTK HoloLens + Android + iOS Project\n\nUnity 2022.3.0f1 setup with MRTK3, OpenXR, and AR Foundation.")
