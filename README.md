name: Auto Build Executable

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests pygame pyinstaller

    - name: Build Executable with PyInstaller
      run: |
        pyinstaller --onefile --noconsole --name="QuranPageQuizApp" main.py

    # ایجاد یا بروزرسانی مداوم نسخه انتشار با نام latest در بخش Releases
    - name: Update Latest Release
      uses: softprops/action-gh-release@v2
      with:
        tag_name: latest
        name: "Latest Auto-Build"
        body: "Automated build of the latest commit on main branch."
        draft: false
        prerelease: false
        files: dist/QuranPageQuizApp.exe
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}