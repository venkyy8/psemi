from pywinauto.application import Application
import os
import shutil
from pywinauto import  Desktop
import time
import pyautogui
import pyperclip
import re
import subprocess
from logger import setup_logger



def copy_all_files_in_a_folder():
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')   

def delete_all_files_in_a_folder():
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete') 
        

def get_base_path_from_user():
    """
    Prompts the user to input the base path.

    Returns:
        str: The base path provided by the user.
    """
    print() 
    print("Please provide the path where your project is located.")
    print("For example, if your project is located at 'C:\\Downloads\\Psemi_2024-0.55.0_D1\\muratastudio',")
    print("you should enter 'C:\\Download\\Psemi_2024-0.55.0_D1\\muratastudio'.")
    print() 

    # Prompt the user to input the base path
    base_path = input("Enter the Project Path: ")   
    return base_path


def select_version_type_to_increment():
    try:
        print() 
        print("Which part of the version number do you want to increment?")
        print("1. Major version (e.g., 0.55.2 -> 1.55.2)")
        print("2. Minor version (e.g., 0.55.2 -> 0.56.2)")
        print("3. Patch version (e.g., 0.55.2 -> 0.55.3)")
        print() 

        selection = input("Enter the number corresponding to your choice: ")
        print()
        if selection == "1":
            return "major"
        elif selection == "2":
            return "minor"
        elif selection == "3":
            return "patch"
        else:
            print()
            print("Invalid selection. Please enter a number between 1 and 3.")
            return select_version_type_to_increment()

       
    except Exception as e:
        logger.error('Error in selecting version type')
        raise




def connect_or_open_vscode(vsCodePath, filePath):
    try:
        # Try to connect to an existing instance of Visual Studio Code
        app = Application(backend="uia").connect(path=vsCodePath, timeout=10)
        logger.debug('Connected to the existing instance of Visual Studio Code')
        # Activate and focus the window
        app.window().set_focus()
        return app.window()
    except Exception as e:
        logger.debug(f'There is no Visual Studio Code instance existing... {e}')
        logger.debug('Opening a new instance of Visual Studio Code...')

        try:
            subprocess.Popen([vsCodePath, filePath])
            logger.debug('New Visual Studio Code opened successfully')
            # Wait for the new instance to start
            time.sleep(10)  # Adjust the sleep time as needed
            app = Application(backend="uia").connect(path=vsCodePath, timeout=10)
            return app.window()
        except Exception as e:
            logger.critical('An error occurred while opening Visual Studio Code')            
            raise

def open_solution_explorer(muRataAppInVSCode):
    try:
        logger.debug('Opening Solution Explorer window')
        # Check if Solution Explorer is already open
        solution_explorer = muRataAppInVSCode.child_window(title="Solution Explorer", control_type="Pane", found_index=0)
        if solution_explorer.exists():
            logger.debug('Solution Explorer is already opened')
            solution_explorer.set_focus()
            return
        else:
            # Find the parent menu containing the "View" menu item
            
            #Find and click on the "View" menu item
            view_menu = muRataAppInVSCode.child_window(title="View", control_type="MenuItem")
            view_menu.click_input()
            time.sleep(2)

            # Find and click on the "Solution Explorer" menu item under the "View" menu
            solution_explorer_menu = muRataAppInVSCode.child_window(title="Solution Explorer", control_type="MenuItem")
            solution_explorer_menu.click_input()
            logger.debug('Solution Explorer is Opened')
    except Exception as e:
        logger.critical('An error occurred while opening Solution Explorer')            
        raise
    
        


def capture_the_result_of_build(muRataAppInVSCode):
    try:
        ### Capture the output
        time.sleep(10)
        customControl=muRataAppInVSCode.Output.Custom
        buildedResult=customControl.child_window(title_re=".*Build started*.", auto_id="WpfTextView", control_type="Edit").window_text()
        logger.debug(f'Output of Build: {buildedResult}')
        time.sleep(10)
        if "0 failed" in buildedResult:
            logger.debug('Build is succeeded')
            muRataAppInVSCode.Output.CloseButton.click_input()
        else:
            raise Exception("Build failed. Consider it as an error.")
    except Exception as e:
        
        logger.critical('Error in capture the build result')
        raise

def build_solution(muRataAppInVSCode):
    try:
        buildWindow= muRataAppInVSCode.child_window(title="Build", control_type="MenuItem")
        buildWindow.click_input()
        time.sleep(2)
        ### Click Build solution ###
        pyautogui.press('down')
        pyautogui.press('enter')
        logger.debug('Build process is started')
        capture_the_result_of_build(muRataAppInVSCode)

        # ### Capture the output
        # time.sleep(10)
        # customControl=muRataAppInVSCode.Output.Custom
        # buildedResult=customControl.child_window(title_re=".*Build started*.", auto_id="WpfTextView", control_type="Edit").window_text()
        # print()
        # print("Output of Build:", buildedResult)

        # time.sleep(10)
        # if "0 failed" in buildedResult:
        #     print()
        #     print("Build is succeeded")
        #     muRataAppInVSCode.Output.CloseButton.click_input()
        # else:
        #     raise Exception("Build failed. Consider it as an error.")
    except Exception as e:
        logger.critical('Error in build solution')
        raise


def build_process_in_release_mode(muRataAppInVSCode,sourceFolder1, sourceFolder2, desinationFolderRelease):

    try:
        ### Change from Debug to Release Mode ###
        muRataAppInVSCode.solutionConfigurations.select("Release")

        logger.debug('Mode is changed from debug to release')

        ### Copy Devices and Plugins folders from Debug to Release ###

        if os.path.exists(desinationFolderRelease):
            shutil.rmtree(desinationFolderRelease)

        # Create destination folder if it does not exist
        os.makedirs(desinationFolderRelease)
        shutil.copytree(sourceFolder1,os.path.join(desinationFolderRelease, os.path.basename(sourceFolder1)))
        logger.debug(f'All files are copied from {sourceFolder1} to  {desinationFolderRelease}')
        shutil.copytree(sourceFolder2,os.path.join(desinationFolderRelease,os.path.basename(sourceFolder2)))
        logger.debug(f'All files are copied from {sourceFolder1} to  {desinationFolderRelease}')
        
        ### Build Solution ###
        build_solution(muRataAppInVSCode)
        
    except Exception as e:
        logger.critical('Error while building solution in release mode')
        raise
        

def update_folders_of_application_folder(muRataAppInVSCode, solutionMuRataAppWindow, devicesFolderOfRelease, pluginsFolderOfRelease):
    try:
        ### Click File System Editor ###
        solutionMuRataAppWindow.child_window(title="muRataStudioSetup", control_type="TreeItem").click_input()
        time.sleep(5)
        muRataAppInVSCode.child_window(title="&File System", control_type="Button").click_input()
        logger.debug('File system sditor button is clicked')

	    ###  Delete all the files from Devices of Application Folder and copy from Devices of Release Folder ###
        fileSystemWindow=muRataAppInVSCode.child_window(title="File System (muRataStudioSetup)", auto_id="D:0:0:|File System (muRataStudioSetup)||{00000000-0000-0000-0000-000000000000}|", control_type="Pane")
        applicationFolder=fileSystemWindow.child_window(title="Application Folder", control_type="TreeItem")
        applicationFolder.double_click_input()
        applicationFolder.child_window(title="Devices", control_type="TreeItem").double_click_input()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        deleteProcess=muRataAppInVSCode.child_window(title="Microsoft Visual Studio", control_type="Window")
        deleteProcess.YesButton.click_input()
        logger.debug('All files are deleted from devices folder (File System on Targer Machine-> Application Folder->Devices)')


        explorer=Application(backend="uia").start("explorer.exe")
        fileExplorer = Desktop(backend="uia").window(title='File Explorer')
        fileExplorer.wait('ready', timeout=10)
        logger.debug('File Explorer is Opened')

        addressBar=fileExplorer.child_window(title="Address: Quick access", auto_id="1001", control_type="ToolBar")
        addressBar.click_input()

        pyautogui.write(devicesFolderOfRelease)
        pyautogui.press('enter')
        time.sleep(10)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        logger.debug('All files are copied from devicesFolderOfRelease')
    
        
        muRataAppInVSCode.set_focus()
        pyautogui.hotkey('ctrl', 'v')
        logger.debug('All files are pasted to devices folder (File System on Targer Machine-> Application Folder->Devices) ')
        


        ### Delete all the files from Plugins of Application Folder and copy from Plugins of Release Folder ###
        applicationFolder.child_window(title="Plugins", control_type="TreeItem").double_click_input()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        deleteProcess=muRataAppInVSCode.child_window(title="Microsoft Visual Studio", control_type="Window")
        deleteProcess.YesButton.click_input()
        logger.debug('All files are deleted from plugins folder (File System on Targer Machine-> Application Folder->Plugins)')
        

        # pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        explorer=Application(backend="uia").start("explorer.exe")
        fileExplorer = Desktop(backend="uia").window(title='File Explorer')
        fileExplorer.wait('ready', timeout=10)
        time.sleep(5)
        logger.debug('File Explorer is Opened')
        addressBar=fileExplorer.child_window(title="Address: Quick access", auto_id="1001", control_type="ToolBar")
        addressBar.click_input()

        pyautogui.write(pluginsFolderOfRelease)
        pyautogui.press('enter')
        time.sleep(5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        logger.debug('All files are copied from pluginsFolderOfRelease')
        muRataAppInVSCode.set_focus()
        pyautogui.hotkey('ctrl', 'v')
        logger.debug('All files are pasted to plugins folder (File System on Targer Machine-> Application Folder->Plugins)')


    except Exception as e:
        logger.critical('Error occurred while updating folders of Application Folder')
        raise



def delete_primary_output_and_shortcuts(fileSystemWindow,muRataAppInVSCode,applicationFolder):
    try:
        ### Delete Primary Output from Murata ###
        applicationFolder.double_click_input()
        fileSystemWindow.child_window(title="Primary output from muRata (Active)", control_type="Edit").click_input()
        pyautogui.press('delete')
        logger.debug('Deleted Primary Output from Murata (File System on Targer Machine-> Application Folder)')

        ### Delete muRata Studio shortcut from Application folder ###
        muRataAppInVSCode.child_window(title="muRata Studio", control_type="ListItem").click_input()
        pyautogui.press('delete')
        logger.debug('Deleted muRata Studio shortcut from Murata (File System on Targer Machine-> Application Folder)')


        ###  Delete muRata Studio shortcut from User's Desktop ###
        usersDesktop=fileSystemWindow.child_window(title="User's Desktop", control_type="TreeItem")
        usersDesktop.double_click_input()
        muRataAppInVSCode.child_window(title="muRata Studio", control_type="ListItem").click_input()
        pyautogui.press('delete')
        logger.debug("Deleted muRata Studio shortcut from Murata (File System on Targer Machine-> User's Desktop)")


        ### Delete muRata Studio shortcut from User's Program Menu->muRata corporation ->muRata Studio ###
        usersProgramsMenu=fileSystemWindow.child_window(title="User's Programs Menu", control_type="TreeItem")
        usersProgramsMenu.double_click_input()
        usersProgramsMenu.MuRataCorporation.double_click_input()
        usersProgramsMenu.MuRataCorporation.MuRataStudio.double_click_input()
        muRataAppInVSCode.child_window(title="muRata Studio", control_type="ListItem").click_input()
        pyautogui.press('delete')
        logger.debug("Deleted muRata Studio shortcut from Murata (File System on Targer Machine->User's Program Menu->muRata corporation)")


    except Exception as e:
        logger.critical('Error while deleting primary output and shortcuts')
        raise


def create_primary_output_from_muRata(muRataAppInVSCode,applicationFolder):
    try:
         ### Create Primary Output from MuRata in Application folder ###
        applicationFolder.right_click_input()

       # Send keys to navigate the context menu
        pyautogui.press('down')  # Move down to "Add" option
        pyautogui.press('enter')  # Select "Add" option
        time.sleep(1)

        # Send keys to navigate to "Primary output"
        pyautogui.press('down') 
        # pyautogui.press('down') # Move down to "Project output"
        pyautogui.press('enter')  # Select "Project output"
        time.sleep(1)
    
        addProjectOutputGroup=muRataAppInVSCode.child_window(title="Add Project Output Group", control_type="Window")

        project=addProjectOutputGroup.child_window(title="Project:", auto_id="240", control_type="ComboBox")
        dropDownOfProject=project.child_window(title="Open", auto_id="DropDown", control_type="Button")
        dropDownOfProject.click_input()
        project.child_window(title="muRata", control_type="ListItem").click_input()

        
        time.sleep(1)
        outputGroups=addProjectOutputGroup.child_window(title="Output Groups:", auto_id="241", control_type="List")
        # outputGroups.child_window(title="Localized resources", control_type="Text").click_input()
        # time.sleep(1)
        outputGroups.child_window(title="Primary output", control_type="Text").click_input()

        time.sleep(1)
        configuration=addProjectOutputGroup.child_window(title="Configuration:", auto_id="242", control_type="ComboBox")
        dropDownOfConfiguration=configuration.child_window(title="Open", auto_id="DropDown", control_type="Button")
        dropDownOfConfiguration.click_input()
        configuration.child_window(title="(Active)", control_type="ListItem").click_input()


        time.sleep(1)
        addProjectOutputGroup.OKButton.click_input()
        logger.debug('Created primary output from muRata')
        
    except Exception as e:
        logger.critical('Error in creating primary output from muRata')
        raise


def create_muRata_shortcut(applicationFolder, fileSystemWindow, muRataAppInVSCode):
    try:
        applicationFolder.double_click_input()
        primaryOutputFromMuRataActive=fileSystemWindow.child_window(title="Primary output from muRata (Active)", control_type="Edit")

        primaryOutputFromMuRataActive.right_click_input()

        time.sleep(1)
        pyautogui.press('down')  # Move down to "Add" option
        time.sleep(1)
        pyautogui.press('enter')  # Select "Add" option
        time.sleep(1)

        shortcutToPrimaryOutputFromMuRataActive=fileSystemWindow.child_window(title="Shortcut to Primary output from muRata (Active)", control_type="Edit")
        shortcutToPrimaryOutputFromMuRataActive.right_click_input()
        time.sleep(1)
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')  
        pyautogui.press('down')
        pyautogui.press('enter')

        properties = muRataAppInVSCode.child_window(title="Properties", control_type="Window")


        properties.child_window(title="(Name)", control_type="TreeItem").double_click_input()
        name=properties.child_window(title="(Name)", control_type="Edit")
        name.type_keys('muRata{SPACE}Studio')
        time.sleep(1)


        icon=properties.child_window(title="Icon", control_type="TreeItem")
        icon.double_click_input()
        time.sleep(0.5)


        iconWindow=muRataAppInVSCode.child_window(title="Icon", control_type="Window")
        time.sleep(0.5)
        iconWindow.child_window(title="Browse...", control_type="Button").click_input()

        time.sleep(0.5)
        selectItemInProject=muRataAppInVSCode.child_window(title="Select Item in Project", control_type="Window")
        selectItemInProject.child_window(title="Application Folder", control_type="ListItem").double_click_input()
        time.sleep(0.5)
        selectItemInProject.child_window(title="muRata.ico", control_type="ListItem").click_input()
        time.sleep(0.5)
        selectItemInProject.OKButton.click_input()


        currentIcon=iconWindow.child_window(title="Current icon:", control_type="List")
        currentIcon.child_window(title="0", control_type="ListItem").click_input()
        time.sleep(0.5)
        iconWindow.OKButton.click_input()


        properties.CloseButton.click_input()  
        logger.debug('Created muRata shortcut with name as muRata and selected icon as muRata.ico')  

    except Exception as e:
        logger.critical('Error in creating muRata shortcut')
        raise

def create_primary_output_and_shortcuts(muRataAppInVSCode,applicationFolder,fileSystemWindow ):
    try:
        create_primary_output_from_muRata(muRataAppInVSCode,applicationFolder)
        create_muRata_shortcut(applicationFolder, fileSystemWindow, muRataAppInVSCode)

        ## Move file from Application Folder to User's Desktop
        muRataAppInVSCode.child_window(title="muRata Studio", control_type="Edit").click_input()
        muRataAppInVSCode.type_keys("^x")
        usersDesktop=fileSystemWindow.child_window(title="User's Desktop", control_type="TreeItem")
        usersDesktop.double_click_input()
        muRataAppInVSCode.type_keys("^v")
        logger.debug("Moved muRata Studio shortcut file from Application folder to User's Desktop")

        create_muRata_shortcut(applicationFolder, fileSystemWindow, muRataAppInVSCode)

        ## Copy file from Application Folder to usersProgramsMenu
        muRataAppInVSCode.child_window(title="muRata Studio", control_type="Edit").click_input()
        muRataAppInVSCode.type_keys("^x")
        usersProgramsMenu=fileSystemWindow.child_window(title="User's Programs Menu", control_type="TreeItem")
        # usersProgramsMenu.double_click_input()
        # usersProgramsMenu.MuRataCorporation.double_click_input()
        usersProgramsMenu.MuRataCorporation.MuRataStudio.double_click_input()
        muRataAppInVSCode.type_keys("^v")
        logger.debug("Moved muRata Studio shortcut file from Application folder to User's Programs Menu->MuRataCorporation-> muRataStudio")

        create_muRata_shortcut(applicationFolder, fileSystemWindow, muRataAppInVSCode)

    
        
    except Exception as e:
        logger.critical('Error creating primary output and shortcuts')
        raise



def get_initial_version_from_assembly_info_cs_file(assemblyInfoFilePath):
    """
    Reads the initial version from the specified file.

    Args:
        filepath: The path to the file containing the initial version.

    Returns:
        The initial version string.
    """
    try:
        with open(assemblyInfoFilePath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "AssemblyVersion" in line:
                    version_string = re.search(r'\d+\.\d+\.\d+\.\d+', line)
                    if version_string:
                        print()
                        print("Initial Version in Assembly info.cs file", version_string.group() )
                        return version_string.group()
    except Exception as e:
        print()
        print(f"Error reading version from assembly_info_cs file: {e}")
        raise
    

def change_version_in_assembly_files(file_paths_dict_for_plugins_and_actual_assembly_file, version_type, muRataAppInVSCode, solutionMuRataAppWindow):
    """
    Updates the version number in the specified files.

    Args:
        file_paths_dict: A dictionary containing file paths for various files.
        version_type: The type of version to update ("major", "minor", or "patch").
    """
    try:
        for category, paths in file_paths_dict_for_plugins_and_actual_assembly_file.items():
            for plugin, file_path in paths.items():
                Assemblyinfo_FileVersion = get_initial_version_from_muRata_studio_properties(muRataAppInVSCode, solutionMuRataAppWindow)

                # Split the initial version into segments
                version_segments = list(map(int, Assemblyinfo_FileVersion.split('.')))

                # Ensure there are four segments in the version string
                while len(version_segments) < 4:
                    version_segments.append(0)

                # Map input to version type if it's an integer
                if isinstance(version_type, int):
                    if version_type == 1:  # Major update
                        version_segments[0] += 1
                        version_segments[1:] = [0, 0, 0]
                    elif version_type == 2:  # Minor update
                        version_segments[1] += 1
                        version_segments[2:] = [0, 0]
                    elif version_type == 3:  # Patch update
                        version_segments[2] += 1
                        version_segments[3] = 0
                    else:
                        raise ValueError("Invalid version type. Must be 1 for 'major', 2 for 'minor', or 3 for 'patch'.")
                elif version_type == "major":  # Major update
                    version_segments[0] += 1
                    version_segments[1:] = [0, 0, 0]
                elif version_type == "minor":  # Minor update
                    version_segments[1] += 1
                    version_segments[2:] = [0, 0]
                elif version_type == "patch":  # Patch update
                    version_segments[2] += 1
                    version_segments[3] = 0
                else:
                    raise ValueError("Invalid version type. Must be 'major', 'minor', or 'patch'.")

                # Construct the updated version string
                updated_version = '.'.join(map(str, version_segments))

                with open(file_path, 'r') as file:
                    lines = file.readlines()
                with open(file_path, 'w') as file:
                    for line in lines:
                        if "AssemblyVersion" in line or "AssemblyFileVersion" in line:
                            line = re.sub(r'\d+\.\d+\.\d+\.\d+', updated_version, line)
                        file.write(line)
                print()
                print(f" Updated {plugin} {version_type.capitalize()} version in {category} Assembly info file is {updated_version}")
    except Exception as e:
        print()
        print(f"Error changing version in AssemblyInfo.cs files: {e}")
        raise


def change_version_in_muRata_studio_properties(muRataAppInVSCode, solutionMuRataAppWindow, version_type):
    try:
        initial_version = get_initial_version_from_muRata_studio_properties(muRataAppInVSCode, solutionMuRataAppWindow)

        muRataAppInVSCode.type_keys("{F4}")

        solutionMuRataAppWindow.child_window(title="muRataStudioSetup", control_type="TreeItem").click_input()
        time.sleep(10)

        properties_window = muRataAppInVSCode.child_window(title="Properties", control_type="Window")
        properties_window.child_window(title="Version", control_type="TreeItem").click_input()
        properties_window.child_window(title="Version", control_type="Edit").double_click_input()

        major, minor, patch = map(int, initial_version.split("."))

        if version_type == 1 or version_type == "major":  # Major update
            major += 1
            minor = 0
            patch = 0
        elif version_type == 2 or version_type == "minor":  # Minor update
            minor += 1
            patch = 0
        elif version_type == 3 or version_type == "patch":  # Patch update
            patch += 1
        else:
            print()
            print("Invalid version type. Must be 1, 2, or 3 for 'major', 'minor', or 'patch' respectively, or their string representations.")
            return

        new_version = f"{major}.{minor}.{patch}"

        version_edit = properties_window.child_window(title="Version", control_type="Edit")
        version_edit.type_keys(new_version)
        print()
        print(f" Updated {'Major' if version_type == 1 or version_type == 'major' else 'Minor' if version_type == 2 or version_type == 'minor' else 'Patch'} version in MuRata Studio Property is {new_version}")
        time.sleep(1)

        properties_window.CloseButton.click_input()
        time.sleep(0.5)
        muRataAppInVSCode.MicrosoftVisualStudio.YesButton.click_input()
        time.sleep(1)
        properties_window.CloseButton.click_input()

    except Exception as e:
        print()
        print(f"Error changing version in muRata Studio properties: {e}")
        raise




def get_initial_version_from_muRata_studio_properties(muRataAppInVSCode, solutionMuRataAppWindow ):

    try:
        # Open the Properties window using the F4 key shortcut
        muRataAppInVSCode.type_keys("{F4}")

        solutionMuRataAppWindow.child_window(title="muRataStudioSetup", control_type="TreeItem").click_input()
        time.sleep(2)

        propertiesWindow=muRataAppInVSCode.child_window(title="Properties", control_type="Window")
        # propertiesWindow=muRataAppInVSCode.child_window(title="Properties Window", control_type="Table")
        propertiesWindow.child_window(title="Version", control_type="TreeItem").click_input()
        propertiesWindow.child_window(title="Version",  control_type="Edit").double_click_input()

        # Copy the selected text to the clipboard
        pyautogui.hotkey('ctrl', 'c')

        # Wait briefly for the clipboard to update
        time.sleep(0.5)

        # Retrieve the selected text from the clipboard
        initialVersion = pyperclip.paste()
        print()
        print("Initial Version in MuRata Studio Property is", initialVersion)
        propertiesWindow.CloseButton.click_input()
        return initialVersion
    
    except Exception as e:
        print()
        print(f"Error occurred while getting initial version from muRata Studio properties: {e}")
        raise


def compare_versions(assembly_version, initial_version):
    """
    Compare the assembly_version with the initial_version,
    ignoring the last segment of the assembly_version.

    Args:
        assembly_version: The version obtained from AssemblyInfo.cs.
        initial_version: The initial version.

    Returns:
        True if the versions match, False otherwise.
    """
    # Split the versions into segments
    assembly_segments = assembly_version.split('.')
    initial_segments = initial_version.split('.')

    # Ignore the last segment of the assembly_version
    assembly_segments = assembly_segments[:-1]

    # Compare the versions
    if assembly_segments == initial_segments:
        return True
    else:
        return False

def change_version(muRataAppInVSCode, solutionMuRataAppWindow, assemblyInfoFilePath, version_type,file_paths_dict_for_plugins_and_actual_assembly_file):
    try:
        initial_version = get_initial_version_from_muRata_studio_properties(muRataAppInVSCode, solutionMuRataAppWindow)
        assembly_version= get_initial_version_from_assembly_info_cs_file(assemblyInfoFilePath)
        
        if compare_versions(assembly_version, initial_version):
             change_version_in_muRata_studio_properties(muRataAppInVSCode, solutionMuRataAppWindow, version_type)
             change_version_in_assembly_files(file_paths_dict_for_plugins_and_actual_assembly_file, version_type, muRataAppInVSCode, solutionMuRataAppWindow)
        else:
            raise Exception("Versions does not match.")

    except Exception as e:
        print()
        print(f"Error in changing version: {e}")
        raise


def install_muRata_studio_setup(solutionMuRataAppWindow, solutionExplorerWindow):
    try:
        solutionExplorerWindow.child_window(title="Collapse All", control_type="Button").click_input()
        solutionMuRataAppWindow.child_window(title="muRataStudioSetup", control_type="TreeItem").right_click_input()
        for _ in range(5):
            pyautogui.press("down")
        time.sleep(1)
        pyautogui.press("enter")
        # fileExplorer=Application(backend="uia").connect(title="muRataStudioSetup")
        # time.sleep(5)
        # muRataStudioSetupInFileExplorer=fileExplorer.MuRataStudioSetup
        # muRataStudioSetupInFileExplorer.Release.double_click_input()
        # fileExplorer=Application(backend="uia").connect(title="Release")
        # releaseFolderInFileExplorer=fileExplorer.Release
        # releaseFolderInFileExplorer.set_focus()
        # releaseFolderInFileExplorer.child_window(title="muRataStudioSetup",  control_type="ListItem").double_click_input()

        time.sleep(1)
        muRataStudioWindow=Application(backend="uia").connect(title="muRata Studio")
        muRataStudioInstallationWindow=muRataStudioWindow.MuRataStudio
        muRataStudioInstallationWindow.set_focus()
        muRataStudioInstallationWindow.child_window(title="Next >", control_type="Button").click_input()
        time.sleep(1)
        muRataStudioInstallationWindow.child_window(title="I Agree", control_type="RadioButton").click_input()
        time.sleep(1)
        muRataStudioInstallationWindow.child_window(title="Next >",  control_type="Button").click_input()
        time.sleep(1)
        muRataStudioInstallationWindow.child_window(title="Next >", control_type="Button").click_input()
        time.sleep(1)
        muRataStudioInstallationWindow.child_window(title="Next >", control_type="Button").click_input()
        time.sleep(10)
        message='muRata Studio has been successfully installed.\r\n\r\nClick "Close" to exit.'
        successResponse=muRataStudioInstallationWindow.child_window(title=message,  control_type="Text")
        if successResponse.exists():

            muRataStudioInstallationWindow.CloseButton2.click_input()
            response=message.split('.', 1)[0].strip() + "." 
            logger.debug(response)
        else:
             raise Exception("Erro in the Installation of muRata Studio")
    except Exception as e:
       logger.critical('Error in installing muRata Studio setup')
   

def build_muRata_studio_Setup(muRataAppInVSCode, solutionMuRataAppWindow, solutionExplorerWindow):
    try:
        ### Build muRata Studio Setup ###
        solutionExplorerWindow.child_window(title="Collapse All", control_type="Button").click_input()
        solutionMuRataAppWindow.child_window(title="muRataStudioSetup", control_type="TreeItem").right_click_input()
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        logger.debug('Build muRata Studio Setup project is started ')
        capture_the_result_of_build(muRataAppInVSCode)
        logger.debug('Build muRata Studio Setup project is completed')

    except Exception as e:
        logger.critical('Error in building muRataStudio Setup')
        raise

def muRata_studio_installer_packaging(muRataAppInVSCode, solutionMuRataAppWindow, solutionExplorerWindow):
    try:
        build_solution(muRataAppInVSCode)
        build_muRata_studio_Setup(muRataAppInVSCode, solutionMuRataAppWindow, solutionExplorerWindow)
        install_muRata_studio_setup(solutionMuRataAppWindow, solutionExplorerWindow, )

    except Exception as e:
        logger.critical('Error in muRataStudio installer packaging')
        raise

def main(vsCodePath):

    try:

        logger.info('Initial Message of Packaging Process !!!')

        ###  Get Project Location Path
        base_path = get_base_path_from_user()
        # Construct the full paths using the provided base path
        sourceFolder1 = fr"{base_path}\Apps\muRata\bin\Debug\Devices"
        sourceFolder2 = fr"{base_path}\Apps\muRata\bin\Debug\Plugins"
        desinationFolderRelease = fr"{base_path}\Apps\muRata\bin\Release"
        devicesFolderOfRelease = fr"{base_path}\Apps\muRata\bin\Release\Devices"
        pluginsFolderOfRelease = fr"{base_path}\Apps\muRata\bin\Release\Plugins"
        assemblyInfoFilePath = fr"{base_path}\Apps\muRata\Properties\AssemblyInfo.cs"
        filePath = fr"{base_path}\Solutions\muRata.Applications\muRata.Applications.sln"

        ### Get Version Type
        version_type=select_version_type_to_increment()

        logger.debug(f'Project Folder is, {base_path}')
        logger.debug(f'Version Type is {version_type}')

        logger.info('Packaging Process is Started')

        
        muRataAppInVSCode = connect_or_open_vscode(vsCodePath, filePath)
        time.sleep(10)

        open_solution_explorer(muRataAppInVSCode)

        solutionExplorerWindow=muRataAppInVSCode.child_window(title="Solution Explorer", control_type="Window")
        solutionMuRataAppWindow=solutionExplorerWindow.child_window(title_re=".*Solution 'muRata.Applications'.*", control_type="TreeItem")
        #final_assemblyfile_path
		 # Define the dictionary containing paths for HardwareAccessFramework
        HardwareAccessFramework = {
            "AdapterAccess": rf"{base_path}\Apps\AdapterAccess\Properties\AssemblyInfo.cs",
            "DeviceAccess": rf"{base_path}\Apps\DeviceAccess\Properties\AssemblyInfo.cs",
            "HardwareInterfaces": rf"{base_path}\Apps\HardwareInterfaces\Properties\AssemblyInfo.cs",
        }
        
        # Define the dictionary containing paths for PluginInterface
        PluginInterface_file_paths = {
            "PluginFramework_file_path": rf"{base_path}\Apps\PluginFramework\Properties\AssemblyInfo.cs",
        }
        
        # Define the dictionary containing paths for plugins
        # Define plugins_file_paths
        plugins_file_paths = {
            "AdapterControl": rf"{base_path}\Apps\Plugins\AdapterControl\Properties\AssemblyInfo.cs",
            "ARC1C0608Control": rf"{base_path}\Apps\Plugins\ARC1C0608Control\Properties\AssemblyInfo.cs",
            "ARCxCCxxControl": rf"{base_path}\Apps\Plugins\ARCxCCxxControl\Properties\AssemblyInfo.cs",
            "DocumentViewerControl": rf"{base_path}\Apps\Plugins\DocumentViewerControl\Properties\AssemblyInfo.cs",
            "HelpViewerControl": rf"{base_path}\Apps\Plugins\HelpViewerControl\Properties\AssemblyInfo.cs",
            "MPQ7920Control": rf"{base_path}\Apps\Plugins\MPQ7920Control\Properties\AssemblyInfo.cs",
            "MPQChartControl": rf"{base_path}\Apps\Plugins\MPQChartControl\Properties\AssemblyInfo.cs",
            "MPQControl": rf"{base_path}\Apps\Plugins\MPQControl\Properties\AssemblyInfo.cs",
            "PE24103Control": rf"{base_path}\Apps\Plugins\PE24103Control\Properties\AssemblyInfo.cs",
            "PE24103i2cControl": rf"{base_path}\Apps\Plugins\PE24103i2cControl\Properties\AssemblyInfo.cs",
            "PE24106Control": rf"{base_path}\Apps\Plugins\PE24106Control\Properties\AssemblyInfo.cs",
            "PE26100Control": rf"{base_path}\Apps\Plugins\PE26100Control\Properties\AssemblyInfo.cs",
            "RegisterControl": rf"{base_path}\Apps\Plugins\RegisterControl\Properties\AssemblyInfo.cs",
            "VADERControl": rf"{base_path}\Apps\Plugins\VADERControl\Properties\AssemblyInfo.cs",
        }
        
        # Define the dictionary containing the path for the main assembly file
        actual_assemblyfile_path = {
            "assemblypath": fr"{base_path}\Apps\muRata\Properties\AssemblyInfo.cs",
        }
        # Define a dictionary to hold all file path dictionaries
        file_paths_dict_for_plugins_and_actual_assembly_file = {
           "Plugins": plugins_file_paths,
           "AssemblyFile": actual_assemblyfile_path,
        }
        
        
        
        build_process_in_release_mode(muRataAppInVSCode,sourceFolder1, sourceFolder2, desinationFolderRelease)
        update_folders_of_application_folder(muRataAppInVSCode, solutionMuRataAppWindow, devicesFolderOfRelease, pluginsFolderOfRelease)

        ### Capturing Window
        fileSystemWindow=muRataAppInVSCode.child_window(title="File System (muRataStudioSetup)", auto_id="D:0:0:|File System (muRataStudioSetup)||{00000000-0000-0000-0000-000000000000}|", control_type="Pane")

        

        ### Capturing Window
        applicationFolder=fileSystemWindow.child_window(title="Application Folder", control_type="TreeItem")

        delete_primary_output_and_shortcuts(fileSystemWindow,muRataAppInVSCode,applicationFolder)

        create_primary_output_and_shortcuts(muRataAppInVSCode,applicationFolder,fileSystemWindow )

        
        
        change_version(muRataAppInVSCode, solutionMuRataAppWindow, assemblyInfoFilePath, version_type, file_paths_dict_for_plugins_and_actual_assembly_file)
        muRata_studio_installer_packaging(muRataAppInVSCode, solutionMuRataAppWindow, solutionExplorerWindow)

        muRataAppInVSCode.CloseButton.click_input()
        devicesWindowInfileExplorer = Desktop(backend="uia").window(title='Devices')
        logger.debug('Visual Studio Code is closed')
        devicesWindowInfileExplorer.set_focus()
        devicesWindowInfileExplorer.CloseButton.click_input()
        pluginsWindowInfileExplorer = Desktop(backend="uia").window(title='Devices')
        pluginsWindowInfileExplorer.set_focus()
        pluginsWindowInfileExplorer.CloseButton.click_input()
   


    except Exception as e:
            logger.critical(f'An error occurred: {e}')
            # fileExplorer.set_focus()
            # fileExplorer.close_file_explorer()
            # muRataAppInVSCode.set_focus()
            # muRataAppInVSCode.CloseButton()
            pyautogui.hotkey('ctrl', 'f4')
            return


if __name__=="__main__":

     # Set up logging
    logger = setup_logger('psemi_packagaing_automation.log')

    ### Delcare VScode path and File Path ###
    vsCodePath=r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\IDE\devenv.exe"
    currentWindowTitle="File Explorer"
    main (vsCodePath)


 