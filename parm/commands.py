from __future__ import print_function, absolute_import, unicode_literals
from ._compat import input, with_metaclass, string_types
##################################################################
# This module is desired by Django
##################################################################
import sys, os
from optparse import make_option, OptionParser, IndentedHelpFormatter
import logging
import inspect

log = logging

def handle_default_options(options):
    """
    Include any default options that all commands should accept here
    so that ManagementUtility can handle them before searching for
    user commands.

    """
    pass

class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.

    """
    pass

def get_answer(message, answers='Yn', default='Y', quit=''):
    """
    Get an answer from stdin, the answers should be 'Y/n' etc.
    If you don't want the user can quit in the loop, then quit should be None.
    """
    if quit and quit not in answers:
        answers = answers + quit
        
    message = message + '(' + '/'.join(answers) + ')[' + default + ']:'
    ans = input(message).strip().upper()
    if default and not ans:
        ans = default.upper()
    while ans not in answers.upper():
        ans = input(message).strip().upper()
    if quit and ans == quit.upper():
        print("Command be cancelled!")
        sys.exit(1)
    return ans

def get_input(prompt, default=None, choices=None, option_value=None):
    """
    If option_value is not None, then return it. Otherwise get the result from 
    input.
    """
    if option_value is not None:
        return option_value
    
    choices = choices or []
    while 1:
        r = input(prompt+' ').strip()
        if not r and default is not None:
            return default
        if choices:
            if r not in choices:
                r = None
            else:
                break
        else:
            break
    return r

__commands__ = {}

def get_commands(modules):
    global __commands__
    
    def check(c):
        return (inspect.isclass(c) and 
            issubclass(c, Command) and c is not Command and c is not CommandManager)
    
    def find_mod_commands(mod):
        for name in dir(mod):
            c = getattr(mod, name)
            if check(c):
                register_command(c)
        
    def collect_commands():
        for m in modules:
            try:
                mod = __import__(m, fromlist=['*'])
            except ImportError as e:
                if not str(e).startswith('No module named'):
                    import traceback
                    traceback.print_exc()
                continue
            
            find_mod_commands(mod)

    collect_commands()
    return __commands__
    
def register_command(kclass):
    global __commands__
    __commands__[kclass.name] = kclass

def call(prog_name, version, modules=None, args=None):
    from .commands import execute_command_line
    
    modules = modules or []
    
    if isinstance(args, string_types):
        import shlex
        args = shlex.split(args)
    
    execute_command_line(args or sys.argv, get_commands(modules), prog_name, version)

class CommandMetaclass(type):
    def __init__(cls, name, bases, dct):
        option_list = list(dct.get('option_list', []))
        for c in bases:
            if hasattr(c, 'option_list') and isinstance(c.option_list, list):
                option_list.extend(c.option_list)
        cls.option_list = option_list
        
class Command(with_metaclass(CommandMetaclass)):
    option_list = ()
    help = ''
    args = ''
    has_options = False

    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.
    
        """
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            version='',
                            add_help_option = False,
                            option_list=self.option_list)
    def get_version(self):
        return "%s version is %s" % (self.prog_name, self.version)

    def usage(self, subcommand):
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.
    
        """
        if self.has_options:
            usage = '%%prog %s [options] %s' % (subcommand, self.args)
        else:
            usage = '%%prog %s %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage
    
    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
    
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()
        
    def run_from_argv(self, prog, subcommand, global_options, argv):
        """
        Set up any environment changes requested, then run this command.
    
        """
        self.prog_name = prog
        parser = self.create_parser(prog, subcommand)
        options, args = parser.parse_args(argv)
        self.execute(args, options, global_options)
        
    def execute(self, args, options, global_options):
        try:
            self.handle(options, global_options, *args)
        except CommandError as e:
            log.exception(e)
            sys.exit(1)

    def handle(self, options, global_options, *args):
        """
        The actual logic of the command. Subclasses must implement
        this method.
    
        """
        raise NotImplementedError()
    
class NewFormatter(IndentedHelpFormatter):
    def format_heading(self, heading):
        return "%*s%s:\n" % (self.current_indent, "", 'Global Options')

class NewOptionParser(OptionParser):
    def _process_args(self, largs, rargs, values):
        while rargs:
            arg = rargs[0]
            longarg = False
            try:
                if arg[0:2] == "--" and len(arg) > 2:
                    # process a single long option (possibly with value(s))
                    # the superclass code pops the arg off rargs
                    longarg = True
                    self._process_long_opt(rargs, values)
                elif arg[:1] == "-" and len(arg) > 1:
                    # process a cluster of short options (possibly with
                    # value(s) for the last one only)
                    # the superclass code pops the arg off rargs
                    self._process_short_opts(rargs, values)
                else:
                    # it's either a non-default option or an arg
                    # either way, add it to the args list so we can keep
                    # dealing with options
                    del rargs[0]
                    raise Exception
            except:
                if longarg:
                    if '=' in arg:
                        del rargs[0]
                largs.append(arg)
                
class CommandManager(Command):
    usage_info = "%prog [global_options] [subcommand [options] [args]]"
    
    def __init__(self, argv=None, commands=None, prog_name=None, global_options=None, version=None):
        self.argv = argv
        self.version = version
        self.prog_name = prog_name or os.path.basename(self.argv[0])
        self.commands = commands
        self.global_options = global_options
    
    def get_commands(self):
        if callable(self.commands):
            commands = self.commands()
        else:
            commands = self.commands
        return commands
    
    def print_help_info(self, global_options):
        """
        Returns the script's main help text, as a string.
        """
        usage = ['',"Type '%s help <subcommand>' for help on a specific subcommand." % self.prog_name,'']
        usage.append('Available subcommands:')
        commands = list(self.get_commands().keys())
        commands.sort()
        for cmd in commands:
            usage.append('  %s' % cmd)
        return '\n'.join(usage)
    
    def fetch_command(self, global_options, subcommand):
        """
        Tries to fetch the given subcommand, printing a message with the
        appropriate command called from the command line (usually
        "uliweb") if it can't be found.
        """
        commands = self.get_commands()
        try:
            klass = commands[subcommand]
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" % \
                (subcommand, self.prog_name))
            sys.exit(1)
        return klass
    
    def execute(self):
        """
        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = NewOptionParser(prog=self.prog_name,
                             usage=self.usage_info,
#                             version=self.get_version(),
                             formatter = NewFormatter(),
                             add_help_option = False,
                             option_list=self.option_list)
        
        if not self.global_options:
            global_options, args = parser.parse_args(self.argv)
            handle_default_options(global_options)
            args = args[1:]
        else:
            global_options = self.global_options
            args = self.argv
    
        def print_help(global_options):
            parser.print_help()
            sys.stderr.write(self.print_help_info(global_options) + '\n')
            sys.exit(1)
            
        if len(args) == 0:
            if global_options.version:
                print(self.get_version())
                sys.exit(1)
            else:
                print_help(global_options)
                sys.ext(1)
    
        try:
            subcommand = args[0]
        except IndexError:
            subcommand = 'help' # Display help if no arguments were given.
    
        if subcommand == 'help':
            if len(args) > 1:
                command = self.fetch_command(global_options, args[1])
                if issubclass(command, CommandManager):
                    cmd = command(['help'], None, '%s %s' % (self.prog_name, args[1]), global_options=global_options)
                    cmd.execute()
                else:
                    command().print_help(self.prog_name, args[1])
                sys.exit(1)
            else:
                print_help(global_options)
        if global_options.help:
            print_help(global_options)
        else:
            command = self.fetch_command(global_options, subcommand)
            if issubclass(command, CommandManager):
                cmd = command(args[1:], None, '%s %s' % (self.prog_name, subcommand), global_options=global_options)
                cmd.execute()
            else:
                cmd = command()
                cmd.run_from_argv(self.prog_name, subcommand, global_options, args[1:])
    
class ApplicationCommandManager(CommandManager):
    option_list = (
        make_option('--help', action='store_true', dest='help',
            help='show this help message and exit.'),
        make_option('-v', '--verbose', action='store_true', 
            help='Output the result in verbose mode.'),
        make_option('--version', action='store_true', dest='version',
            help="show program's version number and exit."),
    )
    help = ''
    args = ''
    
def execute_command_line(argv=None, commands=None, prog_name=None, version=None):
    m = ApplicationCommandManager(argv, commands, prog_name, version=version)
    m.execute()
    
if __name__ == '__main__':
    execute_command_line(sys.argv)