# COSIMIA
The first thing to do is to build the ns-3 environments. To do so, go inside the `NS3-6LOWPAN/`, `NS3-5G/` and `NS3-802.11ah/` folders, and run the following commands:
```
./waf configure --disable-werror
./waf build
```
- The Offline COSIMIA script (using heuristics) can be found in the `methodology.py`.

- The Online COSIMIA script for the online optimization using BO with gaussian processes can be found in `main.py`. 

