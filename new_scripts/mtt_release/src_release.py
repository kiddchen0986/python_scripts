# -*- coding: utf-8 -*-
'''
Prepare for MTT release source code package
usage: src_release.py [-h] src dst

positional arguments:
src MTT gerrit source dir
dst MTT src package destination dir

optional arguments:
-h, --help show this help message and exit
'''
import argparse
import os
import shutil
import re
import fnmatch

reserved_projects = (
    'ModuleTestTool',
    'SensorApiNet',
    'TestsModule',
    'Sequencer',
    'HW_Test',
    'CacImageScoring',
    'sensor_api (sub repository)',
    'hal_ftdi',
    'hal_interface',
    'logging',
)

c_folders = (
    'prodtestlib/prodtestlib',
    'prodtestlib/prodtestlib/capacitance_estimator/include',
    'ctl/ctl/include/public',
    'fpc_c_core/include/public',
    'tools_core/include/public',
    'sensor_api/sensor_api/include/public',
    'sensor_api/common',
    'sensor_api/hal_linux_spi',
    'sensor_api/hal_mtc_2',
    'sensor_api/hal_ftdi',
    'sensor_api/hal_interface',
    'tools_core/logging',
)

external_libs = ('ctl.dll',
                 'CtlNet.dll',
                 'DotNetZip.dll',
                 'FixtureControl.Dummy.dll',
                 'FixtureControl.Factory.dll',
                 'FixtureControl.Interface.dll',
                 'FpcCCore.dll',
                 'fpc_c_core.dll',
                 'hal_mtc_2.dll',
                 'hal_sc.dll',
                 'Imaging.dll',
                 'Imaging.Interop.Desktop.dll',
                 'Integration.Sensor.dll',
                 'libce.dll',
                 'libcenet.dll',
                 'libusb-1.0.dll',
                 'log4net.dll',
                 'Logger.dll',
                 'Logger.Log4Net.dll',
                 'MathNet.Numerics.dll',
                 'ModuleTestCardController.dll',
                 'ModuleTestCardControllerNet.dll',
                 'ModuleTestCardFixtureControl.dll',
                 'Newtonsoft.Json.dll',
                 'prodtestlib.dll',
                 'ProdTestLibNet.dll',
                 'SensorApi2Net.dll',
                 'SensorApiNet.dll',
                 'sensor_api.dll',
                 'Shared.Desktop.dll',
                 'Shared.dll',
                 'SharedTypes.dll',
                 'SharpDX.Direct2D1.dll',
                 'SharpDX.dll',
                 'SharpDX.DXGI.dll',
                 'System.Reflection.TypeExtensions.dll',
                 'TestsCore.dll',
                 'ToolsBioNet.dll',
                 'ToolsCoreNet.dll',
                 'tools_bio.dll',
                 'tools_core.dll',
                 'tools_core.lib',
                 'BiometryNet.dll',
                 'sensor_api_cac2.dll',
                 'sensor_api_cac2_bep.dll',
                 'fpc_bio.dll',
                 'tools_hcp_api.dll',
                 'Integration.dll',
                 'sensor_api_cac2.dll',
                 'sensor_api_cac2_bep.dll',
                 'tools_reg.lib',
                 'ctl_sensor_adapters.dll'
                 )

ModuleTestTool_libs = ('fpc_c_core.dll',
                       'hal_mtc_2.dll',
                       'hal_sc.conf',
                       'hal_sc.dll',
                       'libce.dll',
                       'ModuleTestCardController.dll',
                       'prodtestlib.dll',
                       'sensor_api.dll',
                       'tools_bio.dll',
                       'tools_core.dll',
                       'tools_core.lib')

module_test_tool_project_copy = '    <Content Include="../external/ctl.dll">\n      <Link>ctl.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/fpc_c_core.dll">\n      <Link>fpc_c_core.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/hal_mtc_2.dll">\n      <Link>hal_mtc_2.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/libce.dll">\n      <Link>libce.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/libusb-1.0.dll">\n      <Link>libusb-1.0.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/ModuleTestCardController.dll">\n      <Link>ModuleTestCardController.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/prodtestlib.dll">\n      <Link>prodtestlib.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/sensor_api.dll">\n      <Link>sensor_api.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/tools_bio.dll">\n      <Link>tools_bio.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/tools_core.dll">\n      <Link>tools_core.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/sensor_api_cac2.dll">\n      <Link>sensor_api_cac2.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/sensor_api_cac2_bep.dll">\n      <Link>sensor_api_cac2_bep.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/ctl_sensor_adapters.dll">\n      <Link>ctl_sensor_adapters.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="TestStationConfiguration.xml">\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n      <SubType>Designer</SubType>\n    </Content>\n'

CacImageScoring_project_copy = '    <Content Include="../external/fpc_bio.dll">\n      <Link>fpc_bio.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    ' \
                                '<Content Include="../external/fpc_c_core.dll">\n      <Link>fpc_c_core.dll</Link>\n      <CopyToOutputDirectory>Always</CopyToOutputDirectory>\n    </Content>\n    '

def gen_find(log_pattern, log_path):
    for path, d, file_list in os.walk(log_path):
        if 'internal' in path or 'block_noise_calibration' in path:
            continue
        for name in fnmatch.filter(file_list, log_pattern):
            yield os.path.join(path, name)

def update_solution(src, dst, add_hw_test, add_image_score):
    print('3. Updating solution...')
    sln_path = os.path.join(src, 'ModuleTestTool.sln')
    words = []
    with open(sln_path) as sln_file:
        remove_end_project = False
        for line in sln_file:
            words.append(line)
            if line.startswith('Project'):
                cur_project = line.split('"')[3]
                if cur_project not in reserved_projects:
                    words.remove(line)
                    remove_end_project = True
                    continue

                if cur_project == 'HW_Test' and not add_hw_test:
                    words.remove(line)
                    remove_end_project = True
                    continue

                if cur_project == 'CacImageScoring' and not add_image_score:
                    words.remove(line)
                    remove_end_project = True
                    continue

            if remove_end_project:
                if line.startswith('EndProject'):
                    words.reverse()
                    words.remove(line)
                    words.reverse()
                    remove_end_project = False
                else:
                    words.remove(line)

    record_line = 0
    for i, word in enumerate(words):
        if 'ModuleTestTool' in word:
            #print("line number is", i, "and line is ", words[i])
            words.insert(i + 1, "\tProjectSection(ProjectDependencies) = postProject\n")
            words.insert(i + 2, "\tEndProjectSection\n")
            record_line = i + 2
            break

    for i, word in enumerate(words):
        if 'hal_ftdi' in word:
            text1 = word.split(",")[-1].replace('"', '').strip()
            text1 = "\t\t" + text1 + "=" + text1 + "\n"
            #print(text1)

        if 'hal_interface' in word:
            text2 = word.split(",")[-1].replace('"', '').strip()
            text2 = "\t\t" + text2 + "=" + text2 + "\n"
            #print(text2)

        if 'logging' in word:
            text3 = word.split(",")[-1].replace('"', '').strip()
            text3 = "\t\t" + text3 + "=" + text3 + "\n"
            #print(text3)

    if text1:
        #print(record_line)
        words.insert(record_line, text1)
        record_line = record_line + 1

    if text2:
        #print(record_line)
        words.insert(record_line, text2)
        record_line = record_line + 1

    if text3:
        #print(record_line)
        words.insert(record_line, text3)

    with open(os.path.join(dst, 'ModuleTestTool.sln'), 'w') as f:
        f.writelines(words)

    print('Done')

def update_project_reference(src, dst):
    print('4. Updating C# projects reference...')
    for files in os.walk(src):
        for item in files:
            if type(item) is list:
                for i in item:
                    projects = i.split('.')
                    if i.endswith('csproj') and len(projects) == 2 and projects[0] in reserved_projects[:6]:
                        #Find all reference projects
                        print('Updating', i.split('.')[0])
                        with open(os.path.join(files[0], i)) as f:
                            text = f.read()
                            reference_projects = re.findall('<Name>(.*)</Name>', text)
                            if 'log4net' not in reference_projects:
                                reference_projects.append('log4net')

                            for p in reserved_projects[:6]:
                                if p in reference_projects:
                                    reference_projects.remove(p)

                        is_ModuleTestTool = i.startswith('ModuleTestTool')
                        is_CacImageScoring = i.startswith('CacImageScoring')
                        first_adding_copy = True
                        #Remove ProjectReference
                        new_words = []
                        with open(os.path.join(files[0], i)) as f:
                            found_reference = False
                            found_content = False
                            first_adding_copy = True
                            for line in f:
                                if line.strip().startswith("<ProjectReference") and \
                                                reserved_projects[1] not in line and \
                                                reserved_projects[2] not in line and \
                                                reserved_projects[3] not in line:
                                    found_reference = True
                                if found_reference:
                                    if line.strip().endswith('</ProjectReference>'):
                                        found_reference = False
                                else:
                                    if is_ModuleTestTool:
                                        if line.strip().startswith('<Content') and first_adding_copy:
                                            new_words.append(module_test_tool_project_copy)
                                            first_adding_copy = False
                                            found_content = True
                                        if found_content:
                                            if line.strip().endswith('</Content>'):
                                                found_content = False
                                        else:
                                            new_words.append(line)
                                    elif is_CacImageScoring:
                                        if line.strip().startswith('<Content') and first_adding_copy:
                                            new_words.append(CacImageScoring_project_copy)
                                            if "xml" not in line:
                                                found_content = True
                                            else:
                                                found_content = False
                                            first_adding_copy = False
                                        if found_content:
                                            if line.strip().endswith('</Content>'):
                                                found_content = False
                                        else:
                                            new_words.append(line)

                                    else:
                                        new_words.append(line)

                        #Add Reference
                        #for index, word in enumerate(new_words):
                        #    if word.strip().startswith('<ItemGroup>') and new_words[index + 1].strip().startswith('</ItemGroup>'):
                                #print(i, index, word)
                        #        break

                        index = len(new_words)
                        for p in reference_projects:
                            reference_name = 'FpcCCore' if p.startswith('FpcCCore') else p

                            new_words.insert(index - 1, '\n <ItemGroup>\n')
                            new_words.insert(index, '   <Reference Include="' + reference_name + '">\n')
                            if files[0].endswith('SensorApiNet'):
                                new_words.insert(index + 1, '       <HintPath>../../external/' + reference_name + '.dll</HintPath>\n')
                            else:
                                new_words.insert(index + 1, '       <HintPath>../external/' + reference_name + '.dll</HintPath>\n')
                            new_words.insert(index + 2, '   </Reference>\n')
                            new_words.insert(index + 3, ' </ItemGroup>\n')

                        target_folder = dst + files[0].split(src)[-1]
                        if os.path.exists(target_folder):
                            shutil.rmtree(target_folder)

                        shutil.copytree(files[0], target_folder)

                        #Write
                        with open(os.path.join(target_folder, i), 'w') as f:
                            f.writelines(new_words)

                        break

    print('Done')

def copy_libraries(src, dst):
    print('2. Copying libraries...')
    external_folder = os.path.join(dst, "external")
    if not os.path.exists(external_folder):
        os.mkdir(external_folder)

    src_release_folder = os.path.join(src, r'out\desktop\x86\release')
    lower_external_libs = [i.lower() for i in external_libs]
    for file in os.listdir(src_release_folder):
        if file.lower() in lower_external_libs:
            print('Copying', file)
            shutil.copy(os.path.join(src_release_folder, file), external_folder)


    for lib in gen_find('*.lib', src_release_folder):
        shutil.copy(lib, external_folder)

    print('Done')

def copy_part_of_libraries(src, dst):
    print('Copying part of the libraries to main project...')
    module_test_tool_folder = os.path.join(dst, 'ModuleTestTool')

    src_release_folder = os.path.join(src, r'out\desktop\x86\release')
    lower_libs = [a.lower() for a in ModuleTestTool_libs]
    for file in os.listdir(src_release_folder):
        if file.lower() in lower_libs:
            shutil.copy(os.path.join(src_release_folder, file), module_test_tool_folder)

    print('Done')

def copy_source_code(src, dst):
    print('1. Copying source code...')
    for folder in c_folders:
        dst_path = os.path.join(dst, folder)
        print('Copying', folder)
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)

        if 'prodtestlib' in folder:
            if 'capacitance_estimator' in folder:
                shutil.copytree(os.path.join(src, folder), dst_path, ignore=shutil.ignore_patterns('internal'))
            else:
                shutil.copytree(os.path.join(src, folder), dst_path, ignore=shutil.ignore_patterns('*.c',
                                                                                               '*.cpp',
                                                                                               '*.bat',
                                                                                               '*.txt',
                                                                                               '*.mk',
                                                                                               'prodtestlib.*',
                                                                                               '*.vcxproj',
                                                                                               '*.hpp',
                                                                                               '*file',
                                                                                               'capacitance_estimator',
                                                                                               'block_noise_calibration',
                                                                                               'build',
                                                                                               'Debug',
                                                                                               'external_config',
                                                                                               'lib',
                                                                                               'Release'))
        else:
            shutil.copytree(os.path.join(src, folder), dst_path)

    print('Done')

def update_project_link(dst):
    print('5. Updating C projects link...')
    updated_dependency = None
    for c_project in c_folders[-3:]:
        print('Updating', c_project)
        with open(os.path.join(dst, c_project, c_project.split('/')[-1] + '.vcxproj')) as f:
            text = f.read()
            if c_project.endswith('ftdi'):
                dependency_list = re.findall('<AdditionalDependencies>(.*)</AdditionalDependencies>', text)
                if dependency_list:
                    updated_dependency_list = dependency_list[0].split(';')
                    updated_dependency_list.insert(1, '$(SolutionDir)external/tools_core.lib')
                    updated_dependency = ';'.join(updated_dependency_list)

        with open(os.path.join(dst, c_project, c_project.split('/')[-1] + '.vcxproj')) as f:
            new_words = []
            found_reference = False
            for line in f:
                if line.strip().startswith("<ProjectReference") and 'tools_core.vcxproj' in line:
                    found_reference = True
                if found_reference:
                    if line.strip().endswith('</ProjectReference>'):
                        found_reference = False
                else:
                    if line.strip().startswith("<AdditionalDependencies>"):
                        new_words.append('          <AdditionalDependencies>' + updated_dependency + '</AdditionalDependencies>\n')
                    else:
                        new_words.append(line)

        with open(os.path.join(dst, c_project, c_project.split('/')[-1] + '.vcxproj'), 'w') as f:
            f.writelines(new_words)


def update_folder(src, dst, add_huawei_test, add_image_score):
    if not add_huawei_test:
        huawei_path = os.path.join(dst, "HW_test")
        shutil.rmtree(huawei_path)
    if not add_image_score:
        image_score_path = os.path.join(dst, "CacImageScoring")
        shutil.rmtree(image_score_path)

    print('Done')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="MTT gerrit source dir", type=str)
    parser.add_argument("dst", help="MTT src package destination dir", type=str)
    parser.add_argument('--add_hw_test', help="Add huawei test", type=str, default='False')
    parser.add_argument('--add_image_score', help="Add image_score test",type=str, default='False')

    args = parser.parse_args()

    if(args.add_hw_test.upper() == 'TRUE'):
        args.add_hw_test = True
    else:
        args.add_hw_test = False

    if(args.add_image_score.upper() == 'TRUE'):
        args.add_image_score = True
    else:
        args.add_image_score = False

    print("Build {} release x86 before running the script!".format(args.src))

    copy_source_code(args.src, args.dst)
    copy_libraries(args.src, args.dst)

    update_solution(args.src, args.dst, args.add_hw_test, args.add_image_score)
    update_project_reference(args.src, args.dst)
    copy_part_of_libraries(args.src, args.dst)
    update_project_link(args.dst)
    update_folder(args.src, args.dst, args.add_hw_test, args.add_image_score)

    print('Finished, please build Release/Debug x86 and run default test!')