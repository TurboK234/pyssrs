print('Running pyssrs (Python String Search and Replace Script)')

import sys
import os

PYTHON_MAJORVERSION_REQUIRED = 3
PYTHON_MINORVERSION_REQUIRED = 7
py_maj = sys.version_info[0]
py_min = sys.version_info[1]

def py_report():
    report = str('Python version is ' + str(py_maj) + '.' + str(py_min) +
                 ', Python ' + str(PYTHON_MAJORVERSION_REQUIRED) + '.' +
                 str(PYTHON_MINORVERSION_REQUIRED) + '+ required')
    return report

if py_maj < PYTHON_MAJORVERSION_REQUIRED:
    print(py_report() + ', quitting.')
    sys.exit()
elif py_maj == PYTHON_MAJORVERSION_REQUIRED:
    if py_min < PYTHON_MINORVERSION_REQUIRED:
        print(py_report() + ', quitting.')
        sys.exit()
    elif py_min >= PYTHON_MINORVERSION_REQUIRED:
        print(py_report() + ', continuing.')
else:
    print(py_report() + ', continuing.')


print('The script file is: ' + __file__)
script_dir = os.path.dirname(os.path.realpath(__file__))
print('The script directory is: ' + script_dir)
print('The script arguments are: ')
print(sys.argv)
if len(sys.argv) == 1:
    print('No arguments were provided, assuming settings.txt to be in the script folder.')
    settings_dir = script_dir
    print('The settings directory is: ' + settings_dir)
    settings_file = os.path.join(settings_dir, 'settings.txt')
    if (os.path.exists(settings_file)):
        print('A settings.txt file was found in the script folder')
    else:
        print('No settings.txt file was found in the script folder, exiting')
        sys.exit()
elif len(sys.argv) == 2:
    print('One argument was provided, checking if the argument is an existing file.')
    if (os.path.isfile(os.path.realpath(sys.argv[1]))):
        print('The provided argument is an existing file, assuming to be a valid settings file.')
        settings_dir = os.path.dirname(os.path.realpath(sys.argv[1]))
        print('The settings directory is: ' + settings_dir)
        settings_file = sys.argv[1]
        print('The settings file is: ' + settings_file)
    else:
        print('The provided argument is not an existing file, exiting the script.')
        sys.exit()
else:
    print('Wrong number of arguments provided. The script can only take one argument (the settings file).')
    sys.exit()

# Importing rest of the needed modules.
import configparser
import shutil
import time
import datetime

print('Continuing after 10 seconds. Press Ctrl+C to abort the script now (not recommended later).')
time.sleep(10)

g_config = configparser.ConfigParser()
g_config.read(settings_file, encoding='utf-8')

if (g_config['GENERAL']['DIR_ROOT_FILES']) == '':
    print('Source directory is not set (DIR_REC), exiting. Check the settings.')
    sys.exit()

if g_config['GENERAL']['DIR_LOG'] == '':
    g_config['GENERAL']['DIR_LOG'] = g_config['GENERAL']['DIR_ROOT_FILES']

def is_writable(directory):
    try:
        temptestfile_prefix = 'write_tester'
        count = 0
        filename = os.path.join(directory, temptestfile_prefix)
        while (os.path.exists(filename)):
            filename = '{}.{}'.format(os.path.join(directory, temptestfile_prefix), count)
            count = count + 1
        f = open(filename, 'w')
        f.close()
        os.remove(filename)
        return True
    except Exception as e:
        print('{}'.format(e))
        return False

if (is_writable(g_config['GENERAL']['DIR_LOG'])):
    print('Log directory is writable (required), proceeding.')
else:
    print('Log directory is not writable (required), check permissions and settings.txt. The script will now exit.')
    sys.exit()

current_year = time.strftime('%Y', time.localtime())
logfile = '{}'.format(os.path.join(g_config['GENERAL']['DIR_LOG'], 'pyssrs_log-' + current_year + '.txt'))

def get_timestamp():
    timestamp = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
    return timestamp

# Logging with loglevel parameter is used throughout the script with this function.
# loglevel = 0 : No logging, but prints the string when running.
# loglevel = 1 : Minimal logging, only errors and main events (like script start, finished conversion and script end).
# loglevel = 2 : Reasonable logging with all errors and the important checkpoints.
# loglevel = 3 : All steps that are notified with print are also logged. Most useful only when writing / debugging the script.
def log(logstring, c_loglevel):
    str_logstring = str(logstring)
    print(str_logstring)
    if int(g_config['GENERAL']['LOGLEVEL']) >= c_loglevel:
        f = open(logfile, 'a', encoding='utf-8')
        f.write(get_timestamp() + ' : ' + str_logstring + '\n')
        f.close
        return
    else:
        return None

# As logging is now defined and tested, the script should call this end1() function when exiting.
def end1():
    log('End of the script.', 2)
    sys.exit()

# The first log entry.
log('Script initializing.', 1)
log('Settings file is ' + os.path.join(settings_dir, settings_file) + ' .', 2)

# Function to check if rule keys exist.
def dict_key_check(dict, key):
    if key in dict:
        return True
    else:
        log('No ' + key + ' found in rule "' + dict['RULE_DESCRIPTION'] + '"', 3)
        return False

# Read the rules for string evaluation.
rules_raw = []
rules = []
COMMENT_CHAR = '###'
RULE_CHAR =  '='
RULE_TAG = '[RULE]'
RULE_CLOSE_TAG = '[/RULE]'

def parse_rules(filename):
    current_ruledict = {}
    rule_started = False
    rule_finished = True
    f = open(filename, encoding='utf-8')
    for line in f:
        if COMMENT_CHAR in line:
            line, comment = line.split(COMMENT_CHAR, 1)
        if RULE_TAG in line:
            if rule_finished == False:
                log('Rule tag found but previous rule was not finished, check the rules.txt file', 1)
                log('Starting a new rule and ignoring the unfinished one.', 1)
                current_ruledict = {}
                rule_started = True
                continue
            else:
                rule_started = True
                rule_finished = False
                continue
        # Find lines with rule = value
        if RULE_CHAR in line:
            value = None
            valuelist = []
            rule, value_raw = line.split(RULE_CHAR, 1)
            rule = rule.strip()
            value_raw = value_raw.strip()
            if value_raw:
                valuelist = value_raw.split("'")
                for valuelist_item in valuelist:
                    if not valuelist_item == '':
                        # The first non-empty value is considered as the value.
                        value = valuelist_item
                        break
                if not value:
                    value = ''
            else:
                value = ''
            # Store in dictionary
            current_ruledict[rule] = value
            continue
        if RULE_CLOSE_TAG in line:
            if rule_started == False:
                log('Rule end-tag found but no rule was being read, check the rules.txt file', 1)
                log('Ignoring the current rule and continuing.', 1)
                current_ruledict = {}
                rule_finished = True
                continue
            else:
                rules_raw.append(current_ruledict)
                current_ruledict = {}
                rule_started = False
                rule_finished = True
    f.close()
    # Clean up the rules by only accepting those with valid (and required) keys and sort them.
    for ruledict in rules_raw:
        if not dict_key_check(ruledict, 'RULE_DESCRIPTION'):
            ruledict['RULE_DESCRIPTION'] = 'NO DESCRIPTION'
        if ruledict['RULE_DESCRIPTION'] == '':
            ruledict['RULE_DESCRIPTION'] = 'NO DESCRIPTION'
        if not dict_key_check(ruledict, 'STRING_SEARCH'):
            log('The rule "' + ruledict['RULE_DESCRIPTION'] + '" is missing the STRING_SEARCH key, skipping the rule.', 1)
            continue
        if ruledict['STRING_SEARCH'] == '':
            log('The rule "' + ruledict['RULE_DESCRIPTION'] + '" has empty STRING_SEARCH, skipping the rule.', 1)
            continue        
        if not dict_key_check(ruledict, 'STRING_REPLACE'):
            log('The rule "' + ruledict['RULE_DESCRIPTION'] + '" is missing the STRING_REPLACE key, skipping the rule.', 1)
            continue
        if ruledict['STRING_SEARCH'] == ruledict['STRING_REPLACE']:
            log('The rule "' + ruledict['RULE_DESCRIPTION'] + '" has identical search and replace values, skipping the rule.', 1)
            continue
        ruledict_cleaned = {}
        ruledict_cleaned['RULE_DESCRIPTION'] = ruledict['RULE_DESCRIPTION']
        ruledict_cleaned['STRING_SEARCH'] = ruledict['STRING_SEARCH']
        ruledict_cleaned['STRING_REPLACE'] = ruledict['STRING_REPLACE']
        if 'STRING_EXCLUSION_RULE' in ruledict:
            if not ruledict['STRING_EXCLUSION_RULE'] == '':
                ruledict_cleaned['STRING_EXCLUSION_RULE'] = ruledict['STRING_EXCLUSION_RULE']
        rules.append(ruledict_cleaned)
    return rules

if (g_config['GENERAL']['DIR_RULES']) == '':
    rules_dir = settings_dir
else:
    rules_dir = g_config['GENERAL']['DIR_RULES']

rules_file = os.path.join(rules_dir, 'rules.txt')

if os.path.exists(rules_file):
    log('Parsing the rules from the rules.txt file...', 3)
    rules = parse_rules(rules_file)
    log(str(len(rules)) + ' valid rules were read from rules.txt .', 3)
    if len(rules) < 1:
        log('Since there were no valid rules found in rules.txt, there will be nothing to search (and replace). Continuing.', 1)
else:
    log('No rules file found (rules.txt). The script is still functional, but there will be nothing to search (and replace). Continuing.', 1)

# Get the list of files of specified filetype (with their real paths),
# either recursively or nonrecursively as set in the settings.

filelist = []

if g_config['GENERAL']['RECURSIVE_PYSSRS'] == 'yes':
    tree = []
    for i in os.walk(g_config['GENERAL']['DIR_ROOT_FILES']):
        tree.append(i)
    for foldercontent in tree:
        for file in foldercontent[2]:
            if os.path.isfile(os.path.join(foldercontent[0], file)):
                filelist.append(os.path.realpath(os.path.join(foldercontent[0], file)))
else:
    rootdirlist = os.listdir(g_config['GENERAL']['DIR_ROOT_FILES'])
    for item in rootdirlist:
        if os.path.isfile(os.path.join(g_config['GENERAL']['DIR_ROOT_FILES'], item)):
            filelist.append(os.path.realpath(os.path.join(g_config['GENERAL']['DIR_ROOT_FILES'], item)))

filelist_filtered = []

for file in filelist:
    if file.endswith('.' + g_config['GENERAL']['EXTENSION_FILES']):
        if file == os.path.realpath(__file__):
            log('Found the currently running pyssrs file (' + __file__ + '), skipping.', 3)
            continue
        if file == settings_file:
            log('Found the current pyssrs settings file (' + settings_file + '), skipping.', 3)
            continue
        if file == rules_file:
            log('Found the current pyssrs rules file (' + rules_file + '), skipping.', 3)
            continue
        if file == logfile:
            log('Found the current pyssrs log file (' + logfile + '), skipping.', 3)
            continue        
        filelist_filtered.append(file)

log(str(len(filelist_filtered)) + ' files with the correct extension (' + g_config['GENERAL']['EXTENSION_FILES'] + ') were found.', 3)

# Function to test if a file can be read (for handling errors with wrong encodings etc.)
def is_readable(file, encoding):
    try:
        f = open(file, 'r', encoding=encoding)
        testlist = f.readlines()
        f.close()
        return True
    except Exception as e:
        print('{}'.format(e))
        return False

# The actual loop for searching and replacing text inside text files.

path_prevfile = ''
dir_writeaccess = True
files_edited = 0

log('Starting the loop to look for strings inside text files', 3)
for filefullname in filelist_filtered:

    log('Examining file ' + filefullname, 3)
    path_currentfile, filename_currentfile = os.path.split(filefullname)

    # Check the days (since modification) before considering the file for search.
    days_since_modification = (datetime.date.today() - datetime.date.fromtimestamp(os.path.getmtime(filefullname))).days
    if (days_since_modification < int(g_config['GENERAL']['DAYS_BEFORE_SEARCH'])):
        log('The file is newer (' + str(days_since_modification) + ' day(s) since modified) than DAYS_BEFORE_SEARCH defines, skipping the file.', 2)
        continue
    else:
        log('The file is older or equal (' + str(days_since_modification) + ' day(s) since modified) to what DAYS_BEFORE_SEARCH defines, continuing.', 3) 

    if not path_currentfile == path_prevfile:   
        if is_writable(path_currentfile):
            log('The directory ' + path_currentfile + ' is writable, continuing.', 3)
            path_prevfile = path_currentfile
            dir_writeaccess = True
        else:
            log('Unable to write to directory ' + path_currentfile + ' , check permissions. Skipping to the next folder.', 1)
            path_prevfile = path_currentfile
            dir_writeaccess = False
            continue
    else:
        if dir_writeaccess == False:
            continue

    if g_config['GENERAL']['TEXTFILE_ENCODING'] == '':
        text_encoding = 'utf-8'
    else:
        text_encoding = str(g_config['GENERAL']['TEXTFILE_ENCODING'])

    if not is_readable(filefullname, text_encoding):
        log('The file ' + filefullname + ' could not be read, maybe wrong encoding? Check the settings. Skipping the file.', 1)
        continue
        
    currentfile = open(filefullname, 'r', encoding=text_encoding)
    currentfile_list = currentfile.readlines()
    currentfile.close()

    currentfile_list_final = []

    lines_edited = 0

    for line in currentfile_list:

        line_final = line
        for rule in rules:
            if 'STRING_EXCLUSION_RULE' in rule:
                if line_final.find(rule['STRING_EXCLUSION_RULE']) >= 0:
                    log('Exclusion string (>' + rule['STRING_EXCLUSION_RULE'] + '<, in rule "' + rule['RULE_DESCRIPTION'] + '") found on line >' + line_final.strip() + '<, skipping the rule.', 3)
                    continue
            if line_final.find(rule['STRING_SEARCH']) >= 0:
                log('Hit on line >' + line_final.strip() + '< (rule "' + rule['RULE_DESCRIPTION'] + '", searched for >' + rule['STRING_SEARCH'] + '<, replacing with >' + rule['STRING_REPLACE'] + '<).', 2)
                line_final = line_final.replace(rule['STRING_SEARCH'], rule['STRING_REPLACE'])
                lines_edited += 1

        currentfile_list_final.append(line_final)        
    
    if currentfile_list_final == currentfile_list:
        log('Nothing to edit in the file ' + filefullname + ', continuing', 3)
        continue
    else:
        # If the file contents was edited the replacing is done step-by-step to allow proper debugging.
        log('The file was edited, trying to replace the old file', 3)

        tempfilecount = 0
        tempfile = '{}.{}-{}'.format(filefullname, 'TEMP', tempfilecount)
        while (os.path.exists(tempfile)):
            tempfile = '{}.{}-{}'.format(filefullname, 'TEMP', tempfilecount)
            tempfilecount = tempfilecount + 1

        try:
            tempf = open(filefullname, 'w', encoding=text_encoding)
            tempf.close()
        except Exception as e:
            print('{}'.format(e))
            log('The source file + ' + filefullname + ' could not be written (check rights), cancelling the overwriting', 1)
            continue
            
        try:
            # The temp file is copied from the original file to preserve all (easily) preservable properties.
            shutil.copy(filefullname, tempfile)
        except Exception as e:
            print('{}'.format(e))
            log('The source file + ' + filefullname + ' could not be copied to a temporary file (check rights), cancelling the overwriting.', 1)
            if os.path.exists(tempfile):
                os.remove(tempfile)
            continue

        tempf = open(tempfile, 'w', encoding=text_encoding)
        tempf.writelines(currentfile_list_final)
        tempf.close()

        tempf_readtest = open(tempfile, 'r', encoding=text_encoding)
        tempf_readtest_lines = tempf_readtest.readlines()
        tempf_readtest.close()

        if tempf_readtest_lines == currentfile_list_final:
            log('The temporary file was successfully written, trying to replace the old file.', 3)
            oldfile_movecount = 0
            oldfile = '{}.{}-{}'.format(filefullname, 'OLD', oldfile_movecount)
            while (os.path.exists(oldfile)):
                oldfile = '{}.{}-{}'.format(filefullname, 'OLD', oldfile_movecount)
                oldfile_movecount = oldfile_movecount + 1                
            try:
                shutil.move(filefullname, oldfile)
            except Exception as e:
                print('{}'.format(e))
                log('The source file + ' + filefullname + ' could not be moved or renamed, cancelling the overwriting', 1)
                if os.path.exists(oldfile):
                    os.remove(oldfile)
                if os.path.exists(tempfile):
                    os.remove(tempfile)                    
                continue

            if not os.path.exists(filefullname):
                try:
                    shutil.copy(tempfile, filefullname)
                except Exception as e:
                    print('{}'.format(e))
                    log('The temp file + ' + tempfile + ' could not be copied to as the original file, cancelling the overwriting', 1)
                    if os.path.exists(oldfile):
                        os.remove(oldfile)
                    if os.path.exists(tempfile):
                        os.remove(tempfile)                    
                    continue
            
                if os.path.exists(filefullname):
                    log('The new file succesfully replaced the original file, continuing to the next file after cleaning up.', 3)
                    log(str(lines_edited) + ' line(s) were edited in the file ' + filefullname + ' succesfully.', 2)
                    files_edited += 1
                    if os.path.exists(oldfile):
                        os.remove(oldfile)
                    if os.path.exists(tempfile):
                        os.remove(tempfile)                        
                else:
                    log('The new file could not be renamed as the original file, reverting to the old file.', 2)
                    shutil.move(oldfile, filefullname)
                    if os.path.exists(tempfile):
                        os.remove(tempfile)
            else:
                log('The old file was not properly moved, cancelling and skipping the file', 1)
                if os.path.exists(tempfile):
                    os.remove(tempfile)
                if os.path.exists(oldfile):
                    os.remove(oldfile)
        else:
            log('The temporary file did not mirror the edited contents, skipping the conversion and keeping the old file', 1)
            if os.path.exists(tempfile):
                os.remove(tempfile)


# The actual loop for renaming files.

path_prevfile = ''
dir_writeaccess = True
files_renamed = 0

log('Starting the loop to rename files.', 3)
for filefullname in filelist_filtered:

    log('Examining file ' + filefullname, 3)
    path_currentfile, filename_currentfile = os.path.split(filefullname)

    # Check the days (since modification) before considering the file for search.
    days_since_modification = (datetime.date.today() - datetime.date.fromtimestamp(os.path.getmtime(filefullname))).days
    if (days_since_modification < int(g_config['GENERAL']['DAYS_BEFORE_SEARCH'])):
        log('The file is newer (' + str(days_since_modification) + ' day(s) since modified) than DAYS_BEFORE_SEARCH defines, skipping the file.', 2)
        continue
    else:
        log('The file is older or equal (' + str(days_since_modification) + ' day(s) since modified) to what DAYS_BEFORE_SEARCH defines, continuing.', 3) 

    if not path_currentfile == path_prevfile:   
        if is_writable(path_currentfile):
            log('The directory ' + path_currentfile + ' is writable, continuing.', 3)
            path_prevfile = path_currentfile
            dir_writeaccess = True
        else:
            log('Unable to write to directory ' + path_currentfile + ' , check permissions. Skipping to the next folder.', 1)
            path_prevfile = path_currentfile
            dir_writeaccess = False
            continue
    else:
        if dir_writeaccess == False:
            continue
 

    filename_currentfile_final = filename_currentfile
    
    for rule in rules:
        if 'STRING_EXCLUSION_RULE' in rule:
            if filename_currentfile_final.find(rule['STRING_EXCLUSION_RULE']) >= 0:
                log('Exclusion string (>' + rule['STRING_EXCLUSION_RULE'] + '<, in rule "' + rule['RULE_DESCRIPTION'] + '") found in file name >' + filename_currentfile_final + '<, skipping the rule.', 3)
                continue
        if filename_currentfile_final.find(rule['STRING_SEARCH']) >= 0:
            log('Hit in file name >' + filename_currentfile_final + '< (rule "' + rule['RULE_DESCRIPTION'] + '", searched for >' + rule['STRING_SEARCH'] + '<, replacing with >' + rule['STRING_REPLACE'] + '<).', 2)
            filename_currentfile_final = filename_currentfile_final.replace(rule['STRING_SEARCH'], rule['STRING_REPLACE'])    
    
    if filename_currentfile_final == filename_currentfile:
        log('Nothing to edit in the file name ' + filefullname + ', continuing', 3)
        continue
    else:

        filefullname_final = os.path.join(path_currentfile, filename_currentfile_final)
        
        try:
            shutil.move(filefullname, filefullname_final)
            files_renamed += 1  
            log('The file name was edited, renamed the file ' + filefullname + ' to ' + filefullname_final + '.', 2)
        except Exception as e:
            print('{}'.format(e))
            log('The source file + ' + filefullname + ' could not be renamed, cancelling the renaming for this file', 1)
            continue

log('Done, ' + str(files_edited) + ' files edited, ' + str(files_renamed) + ' files renamed.', 1)
end1()
