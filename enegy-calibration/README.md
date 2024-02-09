# Usage
- Create an experimentant on FIT IoT-Lab.
- Run script-6lowpan.py from the ssh server of IoT-Lab. 

## KPIs
- The results (packet delivery and latency) will be displayed on the terminal.

## RSSI and nodes positions
- Get log.txt from the ssh server of IoT-Lab.
- Parse RSSI from the log file using "grep -e 'rssi' -e 'source address'".
- Get nodes positions using: "python3 parse.py" by instantiating the list of used nodes (and apply the get_position() function).

## Energy
- Get OML files from experiments using ssh, and move them to oml_plot_tools folder.
- Run simulation on ns-3 with the gathered RSSI and nodes positions.
- Get simulation log as energy-states.txt.
- Parse the simulation log for a specific node using "grep '2 LrWpanRadio' > energy-stated-parsed.txt" for the node 2 for instance. Note that the node id must be > 2 (to avoid the gateway and the probing node).
- Generate data for the regression using: "python3 main.py".
- Apply the linear regression and non-negative least squares on the generated data using: "python3 regressor.py".