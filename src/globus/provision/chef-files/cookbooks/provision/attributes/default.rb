# -------------------------------------------------------------------------- #
# Copyright 2010-2011, University of Chicago                                 #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #

# Default attributes.
# For now, only directories where software is going to be installed.

gp_domain = node[:topology][:domains][node[:domain_id]]
softdir   = gp_domain[:filesystem][:dir_software]

default[:galaxy][:dir] = "#{softdir}/galaxy"
default[:blast][:dir] = "#{softdir}/blast"
default[:globus][:simpleCA] = "/var/lib/globus/simple_ca"
