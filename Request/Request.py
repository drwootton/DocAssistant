# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

# Generic base class for background requests
class Request():
    
    def __init__(self):
        pass
    
    def processRequest(self):
        print("Subclass is missing processRequest Function")
