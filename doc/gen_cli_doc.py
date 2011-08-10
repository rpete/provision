import demogrid.cli.api as api
import demogrid.cli.ec2 as ec2
import demogrid.cli.globusonline as globusonline
from docutils.core import publish_string
import re
import textwrap
import operator

OPTION_LEN=50
DESCRIPTION_LEN=100

commands = [api.demogrid_create, api.demogrid_start, api.demogrid_describe_instance,
            api.demogrid_update_topology, api.demogrid_stop, api.demogrid_terminate,
            api.demogrid_add_host, api.demogrid_add_user, api.demogrid_remove_hosts,
            api.demogrid_remove_users, api.demogrid_list_instances,
            
            ec2.demogrid_ec2_create_ami, ec2.demogrid_ec2_update_ami,
            
            globusonline.demogrid_go_register_endpoint
            ]

def print_section(title, marker):
    print title
    print marker * len(title)

print_section("Command-line Interface", "*")
commands.sort(key=operator.attrgetter("name"))
for command in commands:
    c = command([])
    print 
    print_section("``%s``" % command.name, "=")
    print
    doc = command.__doc__
    if doc != None:
        doc = textwrap.dedent(doc).strip()
    else:
        doc = "TODO"
    print doc
    print

    opts = c.optparser.option_list
    c.optparser.formatter.store_option_strings(c.optparser)
    
    print "+-" + ("-"*OPTION_LEN)            + "-+-" + ("-"*DESCRIPTION_LEN)                + "-+"
    print "| " + "Option".ljust(OPTION_LEN)  + " | " + "Description".ljust(DESCRIPTION_LEN) + " |"
    print "+=" + ("="*OPTION_LEN)            + "=+=" + ("="*DESCRIPTION_LEN)                + "=+"
    for opt in opts:
        if opt.action != "help":
            opt_string = "``%s``" % c.optparser.formatter.option_strings[opt]            
            opt_help = textwrap.dedent(opt.help).strip()
            
            opt_help_lines = opt_help.split("\n")
            
            # First line
            print "| " + opt_string.ljust(OPTION_LEN)  + " | " + opt_help_lines[0].ljust(DESCRIPTION_LEN) + " |"
            
            for l in opt_help_lines[1:]:
                print "| " + (" "*OPTION_LEN)  + " | " + l.ljust(DESCRIPTION_LEN) + " |"
            
            print "+-" + ("-"*OPTION_LEN)  + "-+-" + ("-"*DESCRIPTION_LEN)                + "-+"

    print
        