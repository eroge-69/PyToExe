# 2.0 Hashes updates by HammyCatte

# Originally written by petrascyll
# Thanks to Leotorrez, CaveRabbit, and SilentNightSound for help
# Join AGMG: discord.gg/agmg

import os
import re
import time
import struct
import argparse
import traceback

from dataclasses import dataclass, field
from pathlib import Path

# extra precaution to not 'fix' 
# the same buffer multiple times
global_modified_buffers: dict[str, list[str]] = {}


def main():
    parser = argparse.ArgumentParser(
        prog="ZZZ Fix 2.0 by HammyCatte",
        description=('')
    )

    parser.add_argument('ini_filepath', nargs='?', default=None, type=str)
    args = parser.parse_args()

    if args.ini_filepath:
        if args.ini_filepath.endswith('.ini'):
            print('Passed .ini file:', args.ini_filepath)
            upgrade_ini(args.ini_filepath)
        else:
            raise Exception('Passed file is not an Ini')

    else:
        # Change the CWD to the directory this script is in
        # Nuitka: "Onefile: Finding files" in https://nuitka.net/doc/user-manual.pdf 
        # I'm not using Nuitka anymore but this distinction (probably) also applies for pyinstaller
        # os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
        print('CWD: {}'.format(os.path.abspath('.')))
        process_folder('.')

    print('Done!')


# SHAMELESSLY (mostly) ripped from genshin fix script
def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.upper().startswith('DISABLED') and filename.lower().endswith('.ini'):
            continue
        if filename.upper().startswith('DESKTOP'):
            continue

        filepath = os.path.join(folder_path, filename)
        if os.path.isdir(filepath):
            process_folder(filepath)
        elif filename.endswith('.ini'):
            print('Found .ini file:', filepath)
            upgrade_ini(filepath)


def upgrade_ini(filepath):
    try:
        # Errors occuring here is fine as no write operations to the ini nor any buffers are performed
        ini = Ini(filepath).upgrade()
    except Exception as x:
        print('Error occurred: {}'.format(x))
        print('No changes have been applied to {}!'.format(filepath))
        print()
        print(traceback.format_exc())
        print()
        return False

    try:
        # Content of the ini and any modified buffers get written to disk in this function
        # Since the code for this function is more concise and predictable, the chance of it failing
        # is low, but it can happen if Windows doesn't want to cooperate and write for whatever reason.
        ini.save()
    except Exception as X:
        print('Fatal error occurred while saving changes for {}!'.format(filepath))
        print('Its likely that your mod has been corrupted. You must redownload it from the source before attempting to fix it again.')
        print()
        print(traceback.format_exc())
        print()
        return False

    return True


# MARK: Ini
class Ini():
    def __init__(self, filepath):
        self.filepath = filepath
        try:
            self.content  = Path(self.filepath).read_text(encoding='utf-8')
            self.encoding = 'utf-8'
        except UnicodeDecodeError:
            self.content  = Path(self.filepath).read_text(encoding='gb2312')
            self.encoding = 'gb2312'
        

        # The random ordering of sets is annoying
        # Use a list for the hashes that will be iterated on
        # and a set for the hashes I already iterated on
        self._hashes = []
        self._touched = False
        self._done_hashes = set()

        # Only write the modified buffers at the very end after the ini is saved, since
        # the ini can be backed up, while backing up buffers is not not reasonable.
        # Buffer with multiple fixes: will be read from the mod directory for the first
        # fix, and from this dict in memory for subsequent fixes 
        self.modified_buffers = {
            # buffer_filepath: buffer_data
        }

        # Get all (uncommented) hashes in the ini
        pattern = re.compile(r'\n\s*hash\s*=\s*([a-f0-9]*)', flags=re.IGNORECASE)
        self._hashes = pattern.findall(self.content)
    
    def upgrade(self):
        while len(self._hashes) > 0:
            hash = self._hashes.pop()
            if hash not in self._done_hashes:
                if hash in hash_commands:
                    print(f'\tProcessing {hash}:')
                    default_args = DefaultArgs(hash=hash, ini=self, data={}, tabs=2)
                    self.execute(hash_commands[hash], default_args)
                else:
                    print(f'\tSkipping {hash}: No tasks available')
            else:
                print(f'\tSkipping {hash}: Already Checked/Processed')

            self._done_hashes.add(hash)

        return self

    def execute(self, commands, default_args):
        for command in commands:
            clss = command[0]
            args = command[1] if len(command) > 1 else {}
            instance = clss(**args) if type(args) is dict else clss(*args) 
            result: ExecutionResult = instance.execute(default_args)

            self._touched = self._touched or result.touched
            if result.failed:
                print()
                return

            if result.queue_hashes:
                # Only add the hashes that I haven't already iterated on
                self._hashes.extend(set(result.queue_hashes).difference(self._done_hashes))

            if result.queue_commands:
                # sub_default_args = DefaultArgs(
                #     hash = default_args.hash,
                #     ini  = default_args.ini,
                #     data = default_args.data,
                #     tabs = default_args.tabs
                # )
                self.execute(result.queue_commands, default_args)

            if result.signal_break:
                return

        return default_args

    def save(self):
        if self._touched:
            basename = os.path.basename(self.filepath).split('.ini')[0]
            dir_path = os.path.abspath(self.filepath.split(basename+'.ini')[0])
            backup_filename = f'DISABLED_BACKUP_{int(time.time())}.{basename}.ini'
            backup_fullpath = os.path.join(dir_path, backup_filename)

            os.rename(self.filepath, backup_fullpath)
            print(f'Created Backup: {backup_filename} at {dir_path}')
            with open(self.filepath, 'w', encoding=self.encoding) as updated_ini:
                updated_ini.write(self.content)
            # with open('DISABLED_BACKUP_debug.ini', 'w', encoding='utf-8') as updated_ini:
            #     updated_ini.write(self.content)

            if len(self.modified_buffers) > 0:
                print('Writing updated buffers')
                for filepath, data in self.modified_buffers.items():
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    print('\tSaved: {}'.format(filepath))

            print('Updates applied')
        else:
            print('No changes applied')
        print()

    def has_hash(self, hash):
        return (
            (hash in self._hashes)
            or (hash in self._done_hashes)
        )


# MARK: Commands

def get_critical_content(section):
    hash = None
    match_first_index = None
    critical_lines = []
    pattern = re.compile(r'^\s*(.*?)\s*=\s*(.*?)\s*$', flags=re.IGNORECASE)

    for line in section.splitlines():
        line_match = pattern.match(line)
        
        if line.strip().startswith('['):
            continue
        elif line_match and line_match.group(1).lower() == 'hash':
            hash = line_match.group(2)
        elif line_match and line_match.group(1).lower() == 'match_first_index':
            match_first_index = line_match.group(2)
        else:
            critical_lines.append(line)

    return '\n'.join(critical_lines), hash, match_first_index


# Returns all resources used by a commandlist
# Hardcoded to only return vb1 i.e. texcoord resources for now
# (TextureOverride sections are special commandlists)
def process_commandlist(ini_content: str, commandlist: str, target: str):
    line_pattern = re.compile(r'^\s*(run|{})\s*=\s*(.*)\s*$'.format(target), flags=re.IGNORECASE)
    resources = []

    for line in commandlist.splitlines():
        line_match = line_pattern.match(line)
        if not line_match: continue

        if line_match.group(1) == target:
            resources.append(line_match.group(2))

        # Must check the commandlists that are run within the
        # the current commandlist for the resource as well
        # Recursion yay
        elif line_match.group(1) == 'run':
            commandlist_title = line_match.group(2)
            pattern = get_section_title_pattern(commandlist_title)
            commandlist_match = pattern.search(ini_content + '\n[')
            if commandlist_match:
                sub_resources = process_commandlist(ini_content, commandlist_match.group(1), target)
                resources.extend(sub_resources)

    return resources


@dataclass
class DefaultArgs():
    hash : str
    ini  : Ini
    tabs : int
    data : dict[str, str]


@dataclass
class ExecutionResult():
    touched        : bool = False
    failed         : bool = False
    signal_break   : bool = False
    queue_hashes   : tuple[str] = None
    queue_commands : tuple[str] = None


@dataclass(init=False)
class log():
    text: tuple[str]

    def __init__(self, *text):
        self.text = text

    def execute(self, default_args: DefaultArgs):
        tabs        = default_args.tabs

        info  = self.text[0]
        hash  = self.text[1] if len(self.text) > 1 else ''
        title = self.text[2] if len(self.text) > 2 else ''
        rest  = self.text[3:] if len(self.text) > 3 else []

        s = '{}{:34}'.format('\t'*tabs, info)
        if hash  : s += ' - {:8}'.format(hash)
        if title : s += ' - {}'.format(title) 
        if rest  : s += ' - '.join(rest)

        print(s)

        return ExecutionResult(
            touched        = False,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = None
        )


@dataclass
class update_hash():
    new_hash: str

    def execute(self, default_args: DefaultArgs):
        ini         = default_args.ini
        active_hash = default_args.hash

        pattern = re.compile(r'(\n\s*)(hash\s*=\s*{})'.format(active_hash), flags=re.IGNORECASE)
        ini.content, sub_count = pattern.subn(r'\1hash = {}\n; \2'.format(self.new_hash), ini.content)

        default_args.hash = self.new_hash

        return ExecutionResult(
            touched        = True,
            failed         = False,
            signal_break   = False,
            queue_hashes   = (self.new_hash,),
            queue_commands = (
                (log, ('+ Updating {} hash(es) to {}'.format(sub_count, self.new_hash),)),
            )
        )


@dataclass
class comment_sections():

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini
        hash = default_args.hash

        pattern = get_section_hash_pattern(hash)
        new_ini_content = ''   # ini content with all matching sections commented

        prev_j = 0
        commented_count = 0
        section_matches = pattern.finditer(ini.content)
        for section_match in section_matches:
            i, j = section_match.span(1)
            commented_section = '\n'.join(['; ' + line for line in section_match.group(1).splitlines()])
            commented_count  += 1

            new_ini_content += ini.content[prev_j:i] + commented_section
            prev_j = j

        new_ini_content += ini.content[prev_j:]
        
        ini.content = new_ini_content

        return ExecutionResult(
            touched        = True,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = (
                (log, ('- Commented {} relevant section(s)'.format(commented_count),)),
            )
        )


@dataclass
class comment_commandlists():
    commandlist_title: str

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini

        pattern = get_section_title_pattern(self.commandlist_title)
        new_ini_content = ''   # ini content with matching commandlist commented out

        prev_j = 0
        commented_count = 0
        commandlist_matches = pattern.finditer(ini.content)
        for commandlist_match in commandlist_matches:
            i, j = commandlist_match.span(1)
            commented_commandlist = '\n'.join(['; ' + line for line in commandlist_match.group(1).splitlines()])
            commented_count  += 1

            new_ini_content += ini.content[prev_j:i] + commented_commandlist
            prev_j = j

        new_ini_content += ini.content[prev_j:]
        
        ini.content = new_ini_content

        return ExecutionResult(
            touched        = True,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = (
                (log, ('- Commented {} relevant commandlist(s)'.format(commented_count),)),
            )
        )


@dataclass(kw_only=True)
class remove_section():
    capture_content : str = None
    capture_position: str = None

    def execute(self, default_args: DefaultArgs):
        ini         = default_args.ini
        active_hash = default_args.hash
        data        = default_args.data

        pattern = get_section_hash_pattern(active_hash)
        section_match = pattern.search(ini.content)
        if not section_match: raise Exception('Bad regex')
        start, end = section_match.span(1)

        if self.capture_content:
            data[self.capture_content] = get_critical_content(section_match.group(1))[0]
        if self.capture_position:
            data[self.capture_position] = str(start)

        ini.content = ini.content[:start] + ini.content[end:]

        return ExecutionResult(
            touched        = True,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = None
        )


@dataclass(kw_only=True)
class remove_indexed_sections():
    capture_content         : str = None
    capture_indexed_content : str = None
    capture_position        : str = None

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini
        hash = default_args.hash
        data = default_args.data
        
        pattern = get_section_hash_pattern(hash)
        new_ini_content = ''   # ini with ib sections removed
        position        = -1   # First Occurence Deletion Start Position
        prev_end         = 0

        section_matches = pattern.finditer(ini.content)
        for section_match in section_matches:
            if re.search(r'\n\s*match_first_index\s*=', section_match.group(1), flags=re.IGNORECASE):
                if self.capture_indexed_content:
                    critical_content, _, match_first_index = get_critical_content(section_match.group(1))
                    placeholder = '{}{}{}'.format(self.capture_indexed_content, match_first_index, self.capture_indexed_content)
                    data[placeholder] = critical_content
            else:
                if self.capture_content:
                    critical_content = get_critical_content(section_match.group(1))[0]
                    placeholder = self.capture_content
                    data[placeholder] = critical_content

            start, end = section_match.span()
            if position == -1:
                position = start

            new_ini_content += ini.content[prev_end:start]
            prev_end = end

        new_ini_content += ini.content[prev_end:]
        ini.content = new_ini_content

        if self.capture_position:
            data[self.capture_position] = str(position)

        return ExecutionResult(
            touched        = True,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = None
        )


@dataclass(kw_only=True)
class capture_section():
    capture_content  : str = None
    capture_position : str = None

    def execute(self, default_args: DefaultArgs):
        ini         = default_args.ini
        active_hash = default_args.hash
        data        = default_args.data

        pattern = get_section_hash_pattern(active_hash)
        section_match = pattern.search(ini.content)
        if not section_match: raise Exception('Bad regex')
        _, end = section_match.span(1)

        if self.capture_content:
            data[self.capture_content] = get_critical_content(section_match.group(1))[0]
        if self.capture_position:
            data[self.capture_position] = str(end + 1)

        return ExecutionResult(
            touched        = False,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = None
        )


@dataclass(kw_only=True)
class create_new_section():
    section_content  : str
    saved_position   : str = None
    capture_position : str = None

    def execute(self, default_args: DefaultArgs):
        ini         = default_args.ini
        data        = default_args.data

        pos = -1
        if self.saved_position and self.saved_position in data:
            pos = int(data[self.saved_position])

        for placeholder, value in data.items():
            if placeholder.startswith('_'):
                # conditions are not to be used for substitution
                continue
            self.section_content = self.section_content.replace(placeholder, value)

        # Half broken/fixed mods' ini will not have the object indices we're expecting
        # Could also be triggered due to a typo in the hash commands
        for emoji in ['🍰', '🌲', '🤍']:
            if emoji in self.section_content:
                print('Section substitution failed')
                print(self.section_content)
                return ExecutionResult(
                    touched        = False,
                    failed         = True,
                    signal_break   = False,
                    queue_hashes   = None,
                    queue_commands = None
                )
  
        if self.capture_position:
            data[self.capture_position] = str(len(self.section_content) + pos)

        ini.content = ini.content[:pos] + self.section_content + ini.content[pos:]

        return ExecutionResult(
            touched        = True,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = None
        )


@dataclass(kw_only=True)
class transfer_indexed_sections():
    trg_indices: tuple[str] = None
    src_indices: tuple[str] = None

    def execute(self, default_args: DefaultArgs):
        ini         = default_args.ini
        hash        = default_args.hash

        title = None
        p = get_section_hash_pattern(hash)
        ib_matches = p.findall(ini.content)
        indexed_ib_count = 0
        for m in ib_matches:
            if re.search(r'\n\s*match_first_index\s*=', m):
                indexed_ib_count += 1
                if not title: title = re.match(r'^\[TextureOverride(.*?)\]', m, flags=re.IGNORECASE).group(1)[:-1]
            else:
                if not title: title = re.match(r'^\[TextureOverride(.*?)\]', m, flags=re.IGNORECASE).group(1)[:-2]

        if indexed_ib_count == 0:
            return ExecutionResult()

        unindexed_ib_content = '\n'.join([
            f'[TextureOverride{title}IB]',
            f'hash = {hash}',
            '🍰',
            '',
            ''
        ])

        alpha = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z'
        ]
        content = ''
        for i, (trg_index, src_index) in enumerate(zip(self.trg_indices, self.src_indices)):
            content += '\n'.join([
                f'[TextureOverride{title}{alpha[i]}]',
                f'hash = {hash}',
                f'match_first_index = {trg_index}',
                f'🤍{src_index}🤍' if src_index != '-1' else 'ib = null',
                '',
                ''
            ])

        return ExecutionResult(
            touched        = False,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = (
                (remove_indexed_sections, {'capture_content': '🍰', 'capture_indexed_content': '🤍', 'capture_position': '🌲'}),
                (create_new_section,      {'saved_position': '🌲', 'section_content': content}),
                (create_new_section,      {'saved_position': '🌲', 'section_content': unindexed_ib_content}),
            ) if indexed_ib_count < len(ib_matches) else (
                (remove_indexed_sections, {'capture_indexed_content': '🤍', 'capture_position': '🌲'}),
                (create_new_section,      {'saved_position': '🌲', 'section_content': content}),
            ),
        )


@dataclass()
class multiply_section_if_missing():
    equiv_hashes: tuple[str] | str
    extra_title : tuple[str]

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini

        if (type(self.equiv_hashes) is not tuple):
            self.equiv_hashes = (self.equiv_hashes,)
        for equiv_hash in self.equiv_hashes:
            if ini.has_hash(equiv_hash):
                return ExecutionResult(
                    touched        = False,
                    failed         = False,
                    signal_break   = False,
                    queue_hashes   = None,
                    queue_commands = (
                        (log, ('/ Skipping Section Multiplication',  f'{equiv_hash}', f'[...{self.extra_title}]',)),
                    ),
                )
        equiv_hash = self.equiv_hashes[0]

        content = '\n'.join([
            '',
            f'[TextureOverride{self.extra_title}]',
            f'hash = {equiv_hash}',
            '🍰',
            '',
        ])

        return ExecutionResult(
            touched        = False,
            failed         = False,
            signal_break   = False,
            queue_hashes   = (equiv_hash,),
            queue_commands = (
                (log,                ('+ Multiplying Section', f'{equiv_hash}', f'[...{self.extra_title}]')),
                (capture_section,    {'capture_content': '🍰', 'capture_position': '🌲'}),
                (create_new_section, {'saved_position': '🌲', 'section_content': content}),
            ),
        )


@dataclass()
class add_ib_check_if_missing():

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini
        hash = default_args.hash
        
        pattern         = get_section_hash_pattern(hash)
        section_matches = pattern.finditer(ini.content)

        needs_check       = False
        new_sections      = ''
        unindexed_section = ''

        for section_match in section_matches:
            if not re.search(r'\n\s*match_first_index\s*=', section_match.group(1), flags=re.IGNORECASE):
                unindexed_section = section_match.group()
                continue

            if re.search(r'\n\s*run\s*=\s*CommandListSkinTexture', section_match.group(1), flags=re.IGNORECASE):
                new_sections += section_match.group()
                continue

            needs_check = True
            new_sections += re.sub(
                r'\n\s*match_first_index\s*=.*?\n',
                r'\g<0>run = CommandListSkinTexture\n',
                section_match.group(),
                flags=re.IGNORECASE, count=1
            )


        if unindexed_section and not new_sections:
            if not re.search(r'\n\s*run\s*=\s*CommandListSkinTexture', unindexed_section, flags=re.IGNORECASE):
                needs_check = True
                unindexed_section = re.sub(
                    r'\n\s*hash\s*=.*?\n',
                    r'\g<0>run = CommandListSkinTexture\n',
                    unindexed_section,
                    flags=re.IGNORECASE, count=1
                )

        new_sections = unindexed_section + new_sections

        return ExecutionResult(
            touched        = False,
            failed         = False,
            signal_break   = False,
            queue_hashes   = None,
            queue_commands = (
                (log,                     ('+ Adding `run = CommandListSkinTexture`',)),
                (remove_indexed_sections, {'capture_position': '🌲'}),
                (create_new_section,      {'saved_position': '🌲', 'section_content': new_sections}),
            ) if needs_check else (
                (log,                     ('/ Skipping `run = CommandListSkinTexture` Addition',)),
            ),
        )


@dataclass
class add_section_if_missing():
    equiv_hashes    : tuple[str] | str
    section_title   : str = None
    section_content : str = field(default='')

    def execute(self, default_args: DefaultArgs):
        ini = default_args.ini

        if (type(self.equiv_hashes) is not tuple):
            self.equiv_hashes = (self.equiv_hashes,)
        for equiv_hash in self.equiv_hashes:
            if ini.has_hash(equiv_hash):
                return ExecutionResult(
                    touched        = False,
                    failed         = False,
                    signal_break   = False,
                    queue_hashes   = None,
                    queue_commands = (
                        (log, ('/ Skipping Section Addition', equiv_hash, f'[...{self.section_title}]',)),
                    ),
                )
        equiv_hash = self.equiv_hashes[0]

        section = '\n[TextureOverride{}]\n'.format(self.section_title)
        section += 'hash = {}\n'.format(equiv_hash)
        section += self.section_content

        return ExecutionResult(
            touched        = False,
            failed         = False,
            signal_break   = False,
            queue_hashes   = (equiv_hash,),
            queue_commands = (
                (log,                ('+ Adding Section', equiv_hash, f'[...{self.section_title}]',)),
                (capture_section,    {'capture_position': '🌲'}),
                (create_new_section, {'saved_position': '🌲', 'section_content': section}),
            ),
        )


@dataclass
class zzz_13_remap_texcoord():
    id: str
    old_format: tuple[str] # = ('4B','2e','2f','2e')
    new_format: tuple[str] # = ('4B','2f','2f','2f')

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini
        hash = default_args.hash
        tabs = default_args.tabs

        # Precompute new buffer strides and offsets
        # Check if existing buffer stride matches our expectations
        # before remapping it
        if (len(self.old_format) != len(self.new_format)): raise Exception()
        old_stride = struct.calcsize('<' + ''.join(self.old_format))
        new_stride = struct.calcsize('<' + ''.join(self.new_format))

        offset = 0
        offsets = [0]
        for format_chunk in self.old_format:
            offset += struct.calcsize(f'<{format_chunk}')
            offsets.append(offset)

        # Debugging
        # print(f'\t\tOld Format stride: {struct.calcsize('<' + ''.join(self.old_format))}')
        # print(f'\t\tNew Format stride: {struct.calcsize('<' + ''.join(self.new_format))}')
        # print(f'\t\tBuffer Stride: {stride}')
        # print(f'\t\tOffsets: {offsets}')

        # Need to find all Texcoord Resources used by this hash directly
        # through TextureOverrides or run through Commandlists... 
        pattern = get_section_hash_pattern(hash)
        section_match = pattern.search(ini.content)
        resources = process_commandlist(ini.content, section_match.group(1), 'vb1')

        # - Match Resource sections to find filenames of buffers 
        # - Update stride value of resources early instead of iterating again later
        buffer_filenames = set()
        line_pattern = re.compile(r'^\s*(filename|stride)\s*=\s*(.*)\s*$', flags=re.IGNORECASE)
        for resource in resources:
            pattern = get_section_title_pattern(resource)
            resource_section_match = pattern.search(ini.content)
            if not resource_section_match: continue

            modified_resource_section = []
            for line in resource_section_match.group(1).splitlines():
                line_match = line_pattern.match(line)
                if not line_match:
                    modified_resource_section.append(line)

                # Capture buffer filename
                elif line_match.group(1) == 'filename':
                    modified_resource_section.append(line)
                    buffer_filenames.add(line_match.group(2))

                # Update stride value of resource in ini
                elif line_match.group(1) == 'stride':
                    stride = int(line_match.group(2))
                    if stride != old_stride:
                        print('{}X WARNING [{}]! Expected buffer stride {} but got {} instead. Overriding and continuing.'.format('\t'*tabs, resource, old_stride, stride))
                    #     raise Exception('Remap failed for {}! Expected buffer stride {} but got {} instead.'.format(resource, old_stride, stride))

                    modified_resource_section.append('stride = {}'.format(new_stride))
                    modified_resource_section.append(';'+line)

            # Update ini
            modified_resource_section = '\n'.join(modified_resource_section)
            i, j = resource_section_match.span(1)
            ini.content = ini.content[:i] + modified_resource_section + ini.content[j:]

        global global_modified_buffers
        for buffer_filename in buffer_filenames:
            buffer_filepath = Path(Path(ini.filepath).parent/buffer_filename)
            buffer_dict_key = str(buffer_filepath.absolute())

            if buffer_dict_key not in global_modified_buffers:
                global_modified_buffers[buffer_dict_key] = []
            fix_id = f'{self.id}-texcoord_remap'
            if fix_id in global_modified_buffers[buffer_dict_key]: continue
            else: global_modified_buffers[buffer_dict_key].append(fix_id)

            if buffer_dict_key not in ini.modified_buffers:
                buffer = buffer_filepath.read_bytes()
            else:
                buffer = ini.modified_buffers[buffer_dict_key]

            vcount = len(buffer) // stride
            new_buffer = bytearray()
            for i in range(vcount):
                for j, (old_chunk, new_chunk) in enumerate(zip(self.old_format, self.new_format)):

                    if offsets[j] < stride and offsets[j+1] <= stride:

                        if old_chunk != new_chunk:
                            # HardCode VColor Remap
                            if (j == 0 and old_chunk == '4B' and new_chunk == '4f'):
                                new_buffer.extend(struct.pack('<4f', *[b/255 for b in struct.unpack_from('<4B', buffer, i*stride + 0)]))
                            elif (j == 0 and old_chunk == '4f' and new_chunk == '4B'):
                                new_buffer.extend(struct.pack('<4B', *[int(b*255) for b in struct.unpack_from('<4f', buffer, i*stride + 0)]))

                            # General Element Remap
                            else:
                                new_buffer.extend(struct.pack(f'<{new_chunk}', *struct.unpack_from(f'<{old_chunk}', buffer, i*stride+offsets[j])))

                        # No Element Remap Needed
                        else:
                            new_buffer.extend(buffer[i*stride + offsets[j]: i*stride + offsets[j+1]])

                    # Mod texcoord vertex data does not saturate the expected old stride
                    else: # cope
                        new_buffer.extend(struct.pack(f'<{new_chunk}', *([0] * int(new_chunk[0]))))
            
            ini.modified_buffers[buffer_dict_key] = new_buffer    

        return ExecutionResult(
            touched=True
        )


# Deprecated. Use generalized remap_texcoord instead
@dataclass
class zzz_12_shrink_texcoord_color():
    id: str

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini
        hash = default_args.hash
        tabs = default_args.tabs        

        # Need to find all Texcoord Resources used by this hash directly
        # through TextureOverrides or run through Commandlists... 
        pattern = get_section_hash_pattern(hash)
        section_match = pattern.search(ini.content)
        resources = process_commandlist(ini.content, section_match.group(1), 'vb1')

        # - Match Resource sections to find filenames of buffers 
        # - Update stride value of resources early instead of iterating again later
        buffer_filenames = set()
        line_pattern = re.compile(r'^\s*(filename|stride)\s*=\s*(.*)\s*$', flags=re.IGNORECASE)
        for resource in resources:
            pattern = get_section_title_pattern(resource)
            resource_section_match = pattern.search(ini.content)
            if not resource_section_match: continue

            modified_resource_section = []
            for line in resource_section_match.group(1).splitlines():
                line_match = line_pattern.match(line)
                if not line_match:
                    modified_resource_section.append(line)

                # Capture buffer filename
                elif line_match.group(1) == 'filename':
                    modified_resource_section.append(line)
                    buffer_filenames.add(line_match.group(2))

                # Update stride value of resource in ini
                elif line_match.group(1) == 'stride':
                    stride = int(line_match.group(2))
                    modified_resource_section.append('stride = {}'.format(stride - 12))
                    modified_resource_section.append(';'+line)

            # Update ini
            modified_resource_section = '\n'.join(modified_resource_section)
            i, j = resource_section_match.span(1)
            ini.content = ini.content[:i] + modified_resource_section + ini.content[j:]

        global global_modified_buffers
        for buffer_filename in buffer_filenames:
            buffer_filepath = Path(Path(ini.filepath).parent/buffer_filename)
            buffer_dict_key = str(buffer_filepath.absolute())

            if buffer_dict_key not in global_modified_buffers:
                global_modified_buffers[buffer_dict_key] = []
            fix_id = f'{self.id}-zzz_12_shrink_texcoord_color'
            if fix_id in global_modified_buffers[buffer_dict_key]: continue
            else: global_modified_buffers[buffer_dict_key].append(fix_id)

            if buffer_dict_key not in ini.modified_buffers:
                buffer = buffer_filepath.read_bytes()
            else:
                buffer = ini.modified_buffers[buffer_dict_key]

            vcount = len(buffer) // stride
            new_buffer = bytearray()
            for i in range(vcount):
                # print(*[ int((f*255)) for f in struct.unpack_from('<4f', buffer, i*stride + 0)])
                new_buffer.extend(struct.pack(
                        '<4B',
                        *[
                            int(f * 255)
                            for f in struct.unpack_from('<4f', buffer, i*stride + 0)
                        ]
                    ))
                new_buffer.extend(buffer[i*stride + 16: i*stride + stride])
            
            ini.modified_buffers[buffer_dict_key] = new_buffer            

        return ExecutionResult(
            touched=True
        )

@dataclass
class update_buffer_blend_indices():
    hash       : str
    old_indices: tuple[int]
    new_indices: tuple[int]

    def execute(self, default_args: DefaultArgs):
        ini  = default_args.ini

        # Need to find all Texcoord Resources used by this hash directly
        # through TextureOverrides or run through Commandlists... 
        pattern = get_section_hash_pattern(self.hash)
        section_match = pattern.search(ini.content)
        resources = process_commandlist(ini.content, section_match.group(1), 'vb2')

        # - Match Resource sections to find filenames of buffers 
        # - Update stride value of resources early instead of iterating again later
        buffer_filenames = set()
        line_pattern = re.compile(r'^\s*(filename|stride)\s*=\s*(.*)\s*$', flags=re.IGNORECASE)
        for resource in resources:
            pattern = get_section_title_pattern(resource)
            resource_section_match = pattern.search(ini.content)
            if not resource_section_match: continue

            modified_resource_section = []
            for line in resource_section_match.group(1).splitlines():
                line_match = line_pattern.match(line)
                if not line_match:
                    modified_resource_section.append(line)

                # Capture buffer filename
                elif line_match.group(1) == 'filename':
                    modified_resource_section.append(line)
                    buffer_filenames.add(line_match.group(2))

        for buffer_filename in buffer_filenames:
            buffer_filepath = Path(Path(ini.filepath).parent/buffer_filename)
            buffer_dict_key = str(buffer_filepath.absolute())

            if buffer_dict_key not in ini.modified_buffers:
                buffer = buffer_filepath.read_bytes()
            else:
                buffer = ini.modified_buffers[buffer_dict_key]
    
            new_buffer = bytearray()
            blend_stride = 32
            vertex_count = len(buffer)//blend_stride
            for i in range(vertex_count):
                blend_weights  = struct.unpack_from('<4f', buffer, i*blend_stride + 0)
                blend_indices  = struct.unpack_from('<4I', buffer, i*blend_stride + 16)

                new_buffer.extend(struct.pack('<4f4I', *blend_weights, *[
                    vgx if vgx not in self.old_indices
                    else self.new_indices[self.old_indices.index(vgx)]
                    for vgx in blend_indices
                ]))

            ini.modified_buffers[buffer_dict_key] = new_buffer

        return ExecutionResult(
            touched=True
        )

@dataclass
class convert_to_slots():
    hash        : str              # = IB HASH
    slot_hashes : dict[int, tuple] # = {
    #     SLOT: [list of texture hashes that go in this slot...],
    #     ...
    # }
    '''
    If a slot is already overriden in the ib section, then all discovered sections with texture hashes
    corresponding to this slot will be commented out. If the ib section lacks an override for the slot,
    then the first discovered section with texture hash corresponding to this slot will be converted to
    a commandlist and have `this` replaced with `ps-t#`. A `run = CommandList` line will be added to the
    ib override before any drawindexed lines. The remaining sections with texture hashes corresponding
    to this slot will be commented out if they exist.
    '''

    def execute(self, default_args: DefaultArgs):
        pass



hash_commands = {

    # MARK: YiXuan
    'ac8e9ee3': [(log, ('2.0: YiXuan Hair IB Hash',)),         (add_ib_check_if_missing,)],
    '029c1f5a': [(log, ('2.0: YiXuan Body IB Hash',)),         (add_ib_check_if_missing,)],
    '8c2fc05e': [(log, ('2.0: YiXuan Coat IB Hash',)),         (add_ib_check_if_missing,)],
    '8b067f99': [(log, ('2.0: YiXuan Face IB Hash',)),         (add_ib_check_if_missing,)],

    # Face
    '9efd1605': [
        (log,                           ('2.0: YiXuan FaceA Diffuse 1024p Hash',)),
        (add_section_if_missing,        ('8b067f99', 'YiXuan.Face.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('7d9ee001', 'YiXuan.FaceA.Diffuse.2048')),
    ],
    '7d9ee001': [
        (log,                           ('2.0: YiXuan FaceA Diffuse 2048p Hash',)),
        (add_section_if_missing,        ('8b067f99', 'YiXuan.Face.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('9efd1605', 'YiXuan.FaceA.Diffuse.1024')),
    ],

    # Hair
    '84fe943d': [
        (log,                           ('2.0: YiXuan HairA Diffuse 1024p Hash',)),
        (add_section_if_missing,        ('ac8e9ee3', 'YiXuan.Hair.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('7e38b38b', 'YiXuan.HairA.Diffuse.2048')),
    ],
    '7e38b38b': [
        (log,                           ('2.0: YiXuan HairA Diffuse 2048p Hash',)),
        (add_section_if_missing,        ('ac8e9ee3', 'YiXuan.Hair.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('84fe943d', 'YiXuan.HairA.Diffuse.1024')),
    ],
    '5574ca9f': [
        (log,                           ('2.0: YiXuan HairA LightMap 1024p Hash',)),
        (add_section_if_missing,        ('ac8e9ee3', 'YiXuan.Hair.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('086ac064', 'YiXuan.HairA.LightMap.2048')),
    ],
    '086ac064': [
        (log,                           ('2.0: YiXuan HairA LightMap 2048p Hash',)),
        (add_section_if_missing,        ('ac8e9ee3', 'YiXuan.Hair.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('5574ca9f', 'YiXuan.HairA.LightMap.1024')),
    ],
    'f4ac690c': [
        (log,                           ('2.0: YiXuan HairA MaterialMap 1024p Hash',)),
        (add_section_if_missing,        ('ac8e9ee3', 'YiXuan.Hair.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('83b02982', 'YiXuan.HairA.MaterialMap.2048')),
    ],
    '83b02982': [
        (log,                           ('2.0: YiXuan HairA MaterialMap 2048p Hash',)),
        (add_section_if_missing,        ('ac8e9ee3', 'YiXuan.Hair.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('f4ac690c', 'YiXuan.HairA.MaterialMap.1024')),
    ],

    #Body
    'd7db2bc6': [
        (log,                           ('2.0: YiXuan BodyA Diffuse 1024p Hash',)),
        (add_section_if_missing,        ('029c1f5a', 'YiXuan.Body.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('2a4f37a6', 'YiXuan.BodyA.Diffuse.2048')),
    ],
    '2a4f37a6': [
        (log,                           ('2.0: YiXuan BodyA Diffuse 2048p Hash',)),
        (add_section_if_missing,        ('029c1f5a', 'YiXuan.Body.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('d7db2bc6', 'YiXuan.BodyA.Diffuse.1024')),
    ],
    '96f754a7': [
        (log,                           ('2.0: YiXuan BodyA LightMap 1024p Hash',)),
        (add_section_if_missing,        ('029c1f5a', 'YiXuan.Body.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('5a291e85', 'YiXuan.BodyA.LightMap.2048')),
    ],
    '5a291e85': [
        (log,                           ('2.0: YiXuan BodyA LightMap 2048p Hash',)),
        (add_section_if_missing,        ('029c1f5a', 'YiXuan.Body.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('96f754a7', 'YiXuan.BodyA.LightMap.1024')),
    ],
    'aa1056a5': [
        (log,                           ('2.0: YiXuan BodyA MaterialMap 1024p Hash',)),
        (add_section_if_missing,        ('029c1f5a', 'YiXuan.Body.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('d28370ec', 'YiXuan.BodyA.MaterialMap.2048')),
    ],
    'd28370ec': [
        (log,                           ('2.0: YiXuan BodyA MaterialMap 2048p Hash',)),
        (add_section_if_missing,        ('029c1f5a', 'YiXuan.Body.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('aa1056a5', 'YiXuan.BodyA.MaterialMap.1024')),
    ],

    #Coat
    '1fcedcc3': [
        (log,                           ('2.0: YiXuan CoatA Diffuse 1024p Hash',)),
        (add_section_if_missing,        ('8c2fc05e', 'YiXuan.Coat.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('e6dca725', 'YiXuan.CoatA.Diffuse.2048')),
    ],
    'e6dca725': [
        (log,                           ('2.0: YiXuan CoatA Diffuse 2048p Hash',)),
        (add_section_if_missing,        ('8c2fc05e', 'YiXuan.Coat.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('1fcedcc3', 'YiXuan.CoatA.Diffuse.1024')),
    ],
    'c4d167c3': [
        (log,                           ('2.0: YiXuan CoatA LightMap 1024p Hash',)),
        (add_section_if_missing,        ('8c2fc05e', 'YiXuan.Coat.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('59b2daf9', 'YiXuan.CoatA.LightMap.2048')),
    ],
    '59b2daf9': [
        (log,                           ('2.0: YiXuan CoatA LightMap 2048p Hash',)),
        (add_section_if_missing,        ('8c2fc05e', 'YiXuan.Coat.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('c4d167c3', 'YiXuan.CoatA.LightMap.1024')),
    ],
    'fd56fa4b': [
        (log,                           ('2.0: YiXuan CoatA MaterialMap 1024p Hash',)),
        (add_section_if_missing,        ('8c2fc05e', 'YiXuan.Coat.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('bb581f1e', 'YiXuan.CoatA.MaterialMap.2048')),
    ],
    'bb581f1e': [
        (log,                           ('2.0: YiXuan CoatA MaterialMap 2048p Hash',)),
        (add_section_if_missing,        ('8c2fc05e', 'YiXuan.Coat.IB', 'match_priority = 0\n')),
        (multiply_section_if_missing,   ('fd56fa4b', 'YiXuan.CoatA.MaterialMap.1024')),
    ],
}


# MARK: Regex
# Using VERBOSE flag to ignore whitespace
# https://docs.python.org/3/library/re.html#re.VERBOSE
def get_section_hash_pattern(hash) -> re.Pattern:
    return re.compile(
        r'''
            ^(
                [ \t]*?\[(?:Texture|Shader)Override.*\][ \t]*
                (?:\n
                    (?![ \t]*?(?:\[|hash\s*=))
                    .*$
                )*?
                (?:\n\s*hash\s*=\s*{}[ \t]*)
                (?:
                    (?:\n(?![ \t]*?\[).*$)*
                    (?:\n[\t ]*?[\$\w].*$)
                )?
            )\s*
        '''.format(hash),
        flags=re.VERBOSE|re.IGNORECASE|re.MULTILINE
    )


def get_section_title_pattern(title) -> re.Pattern:
    return re.compile(
        r'''
            ^(
                [ \t]*?\[{}\]
                (?:
                    (?:\n(?![ \t]*?\[).*$)*
                    (?:\n[\t ]*?[\$\w].*$)
                )?
            )\s*
        '''.format(title),
        flags=re.VERBOSE|re.IGNORECASE|re.MULTILINE
    )



# MARK: RUN
if __name__ == '__main__':
    try: main()
    except Exception as x:
        print('\nError Occurred: {}\n'.format(x))
        print(traceback.format_exc())
    finally:
        input('\nPress "Enter" to quit...\n')
