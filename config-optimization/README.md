# COSIMIA
The first thing to do is to build the ns-3 environments. To do so, go inside the `NS3-6LOWPAN/`, `NS3-5G/` and `NS3-802.11ah/` folders, and run the following commands (make sure that log-macros-enabled/disabled.h are included in src/core/model):
```
./waf configure --disable-werror
./waf build
``` 
Then, run this command to install required packages (for Linux systems):
``` 
sudo apt-get install python3-tk 
``` 

(optinal if error, depending on the host version) Add this line in `src/core/helper/csv-reader.cc` header:
``` 
#include <limits> 
``` 
- The Offline COSIMIA script (using heuristics) can be found in the `methodology.py`.

- The Online COSIMIA script for the online optimization using BO with gaussian processes can be found in `main.py`. 

