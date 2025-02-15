### This is the repo of the work of hydrogen pipeline planning and hydrogen energy dispatch.  
Pls refer to the paper for the detailed info.  
### :open_file_folder: The file structure and introduction:
Pipeline-and-grid-dispatch/  

├── analysis.ipynb - Analysis of the planning result  
├── consumption_potential.ipynb - Assess hydrogen demand potential of all provinces  
├── cost_matrix.ipynb - Establish pipeline construction cost factor matrix  
├── dispatch_cable.py - Main mathematical programming code  
├── existing_pipelines.ipynb - Data cleaning and statistical analysis of existing pipelines  
├── function.py - Store commonly used functions  
├── geodata_process.ipynb - Process geodata  
├── geodata_lambert.ipynb - Convert geodata to Lambert projection for display in QGIS  
├── loss_cable.ipynb - Calculate power grid's electricity loss between arbitrary two provinces  
├── optimal_path.py - call modified A* algorithm to get optimal path between arbitrary two provinces  
├── production_potential.ipynb - Renewable power generation potential minus electricity consumption potential to get hydrogen production potential  
├── renewable_potential.ipynb - Assess mainstream renewable power generation potential in all provinces  
├── mesh/  
│   └── mesh.py - cut mesh with certain range  
├── planner/  
│   └── Astar.py  - modified A* algorithm    
└── src/  
    ├── calculate_distance.py  calculate the spherical distance between two sites， given the longitude and latitude.
    └── const.py - parameters used in the programming model  

### :mag_right: Data can be accessed via google drive:https://drive.google.com/drive/folders/1ROALcJucUvuub-WgnjqzpnBvDpQ61TZy?usp=sharing
