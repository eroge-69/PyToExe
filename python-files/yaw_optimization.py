#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import yaml
from floris import ParFlorisModel
from floris.optimization.yaw_optimization.yaw_optimizer_sr import YawOptimizationSR
from joblib import Parallel, delayed
import time
import os
import psutil
from pprint import pprint


# In[2]:


# Print FLORIS version
import floris
print(f"FLORIS version: {floris.__version__}")


# In[3]:


# Load YAML and inspect
yaml_file_path = "C:/Users/TRIANTAFILLOS/Desktop/floris/input_full.yaml"
try:
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    print("Original YAML loaded successfully")
    config['farm']['layout_x'] = [0, 850, 1700, 850, 1700]
    config['farm']['layout_y'] = [1700, 850, 0, 1700, 850]
    config['farm']['turbine_type'] = ['iea_15MW'] * 5
    config.setdefault('flow_field', {})['reference_wind_height'] = 150
    config.setdefault('wake', {})['velocity_model'] = 'empirical_gauss'
    config['wake']['deflection_model'] = 'gauss'
    config['wake']['turbulence_model'] = 'none'
    # Remove any invalid keys
    if 'model' in config.get('wake', {}):
        del config['wake']['model']
    if 'parameters' in config.get('wake', {}):
        del config['wake']['parameters']
    print("Modified YAML configuration:")
    print("Farm layout_x:", config.get('farm', {}).get('layout_x', 'Not found'))
    print("Farm layout_y:", config.get('farm', {}).get('layout_y', 'Not found'))
    print("Turbine type:", config.get('farm', {}).get('turbine_type', 'Not found'))
    print("Wake velocity model:", config.get('wake', {}).get('velocity_model', 'Not found'))
    print("Wake deflection model:", config.get('wake', {}).get('deflection_model', 'Not found'))
    print("Wake turbulence model:", config.get('wake', {}).get('turbulence_model', 'Not found'))
    print("Reference wind height:", config.get('flow_field', {}).get('reference_wind_height', 'Not found'))
    with open("C:/Users/TRIANTAFILLOS/Desktop/floris/modified_input_full.yaml", 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False)
    print("Modified YAML saved to C:/Users/TRIANTAFILLOS/Desktop/floris/modified_input_full.yaml")
except Exception as e:
    print(f"Failed to load or modify YAML: {str(e)}")
    exit()


# In[4]:


# Initialize ParFlorisModel
try:
    FModel = ParFlorisModel(config, max_workers=8, n_wind_condition_splits=8)
except Exception as e:
    print(f"Failed to initialize ParFlorisModel: {str(e)}")
    exit()


# In[5]:


# Print turbine layout
x, y = FModel.get_turbine_layout()
print("x", x, "y", y)


# In[6]:


# Load and preprocess data
data = pd.read_excel('C:/Users/TRIANTAFILLOS/Desktop/floris/data1.xlsx')
data = data[['time', 'wind_speeds', 'wind_directions', 'turbulence_intensities']]
data = data.round({'wind_directions': 0,'wind_speeds':1})
data['turbulence_intensities'] = 0.1
data['wind_speeds'] = np.where((data['wind_speeds'] >= 0) & (data['wind_speeds'] < 2.9), 2.9, data['wind_speeds'])
#data['wind_speeds'] = np.where(data['wind_speeds'] <= 0, 0.1, data['wind_speeds'])
#data=data[4500:4600]  # Limit to 100 rows
# Drop NaN values
data = data.dropna(subset=['wind_speeds', 'wind_directions'])
print(f"Initial rows: {len(data)}")


# In[7]:


# Calculate unique conditions
unique_wind_conditions = data[['wind_speeds', 'wind_directions', 'turbulence_intensities']].drop_duplicates()
#unique_wind_conditions = unique_wind_conditions.head(100)  # Limit to 62 unique conditions
n_conditions = len(unique_wind_conditions)
print(f"Number of unique conditions: {n_conditions}")
print("First 5 rows of unique_wind_conditions:")
print(unique_wind_conditions.head())


# In[8]:


def optimize_yaw_for_condition(ws, wd, ti, FModel):
    try:
        print(f"Starting optimization for ws={ws}, wd={wd}, ti={ti}")
        ws_array = np.array([float(ws)], dtype=np.float64)
        wd_array = np.array([float(wd)], dtype=np.float64)
        ti_array = np.array([float(ti)], dtype=np.float64)

        print("Setting wind conditions...")
        FModel.set(
            wind_directions=wd_array,
            wind_speeds=ws_array,
            turbulence_intensities=ti_array
        )

        print("Initializing YawOptimizationSR...")
        yaw_opt = YawOptimizationSR(
            fmodel=FModel,
            minimum_yaw_angle=-30.0,  # Reduced range
            maximum_yaw_angle=30.0    # Reduced range
        )

        print("Running optimization...")
        result_df = yaw_opt.optimize()
        print(f"Yaw optimization result: {result_df}")
        print(f"Result shape: {result_df.shape}, type: {type(result_df)}")
        if not isinstance(result_df, pd.DataFrame):
            print(f"Unexpected result type: {type(result_df)}")
            return None
        print(f"DataFrame columns: {result_df.columns}")

        # Extract yaw angles
        if 'yaw_angles_opt' not in result_df.columns:
            print("yaw_angles_opt column missing")
            return None
        yaw_angles = result_df['yaw_angles_opt'].iloc[0]
        print(f"Raw yaw_angles_opt: {yaw_angles}")
        yaw_angles = np.array(yaw_angles, dtype=np.float64)
        print(f"Converted yaw angles: {yaw_angles}, shape: {yaw_angles.shape}")
        if len(yaw_angles) != 5:
            print(f"Invalid yaw angles length: {len(yaw_angles)}")
            return None
        if np.any(np.isnan(yaw_angles)):
            print(f"Optimization returned NaN yaw angles: {yaw_angles}")
            return None

        # Extract optimized power
        if 'farm_power_opt' not in result_df.columns:
            print("farm_power_opt column missing")
            return None
        power = float(result_df['farm_power_opt'].iloc[0])
        if np.isnan(power):
            print(f"Power calculation returned NaN for ws={ws}, wd={wd}, ti={ti}")
            return None
        print(f"Power: {power}")

        return {
            'yaw_angles': yaw_angles,
            'power': power
        }
    except Exception as e:
        print(f"Yaw optimization failed for ws={ws}, wd={wd}, ti={ti}: {str(e)}")
        return None


# In[9]:


def process_condition(row, idx, total, FModel, checkpoint_file):
    try:
        start_time = time.time()
        ws = float(row['wind_speeds'])
        wd = float(row['wind_directions'])
        ti = float(row['turbulence_intensities'])
        
        if ws < 0 or wd < 0 or wd > 360 or ti < 0:
            print(f"Invalid condition: ws={ws}, wd={wd}, ti={ti}")
            return None

        print(f"Processing condition {idx+1}/{total}: ws={ws}, wd={wd}, ti={ti}")
        result = optimize_yaw_for_condition(ws, wd, ti, FModel)
        if result is None:
            return None
        
        elapsed = time.time() - start_time
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{total} conditions ({(idx + 1)/total*100:.1f}%), {elapsed:.2f}s/condition, CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%")
        
        output = {
            'wind_speeds': ws,
            'wind_directions': wd,
            'turbulence_intensities': ti,
            **{f'Yaw_T{i+1}_opt': result['yaw_angles'][i] for i in range(5)},
            'Total_Power_opt': result['power']
        }
        
        if (idx + 1) % 100 == 0:
            temp_df = pd.DataFrame([output])
            if os.path.exists(checkpoint_file):
                temp_df.to_excel(checkpoint_file, mode='a', header=False, index=False)
            else:
                temp_df.to_excel(checkpoint_file, index=False)
        
        return output
    except Exception as e:
        print(f"Failed for ws={row['wind_speeds']}, wd={row['wind_directions']}, ti={row['turbulence_intensities']}: {str(e)}")
        return None


# In[10]:


'''
# Test single condition
print("Testing single condition...")
test_row = unique_wind_conditions.iloc[0]
test_result = optimize_yaw_for_condition(
    ws=float(test_row['wind_speeds']),
    wd=float(test_row['wind_directions']),
    ti=float(test_row['turbulence_intensities']),
    FModel=FModel
)
print(f"Test result: {test_result}")
'''


# In[11]:


'''
# Test first 5 conditions sequentially
print("Testing first 5 conditions sequentially...")
sequential_results = []
checkpoint_file = "C:/Users/TRIANTAFILLOS/Desktop/floris/partial_results_temp.xlsx"
for idx, (_, row) in enumerate(unique_wind_conditions.head(5).iterrows()):
    result = process_condition(row, idx, 5, FModel, checkpoint_file)
    sequential_results.append(result)
sequential_results = [r for r in sequential_results if r is not None]
print(f"Sequential results: {len(sequential_results)} successful out of 5")
'''


# In[13]:


# Calculate baseline power
try:
    FModel.set(
        wind_directions=data['wind_directions'].values,
        wind_speeds=data['wind_speeds'].values,
        turbulence_intensities=data['turbulence_intensities'].values
    )
    FModel.run()
    turbine_powers = FModel.get_turbine_powers() / 1000000.0
    farm_power_baseline = np.sum(turbine_powers)
    print(f"Baseline farm power: {farm_power_baseline} MW")
except Exception as e:
    print(f"Failed to calculate baseline power: {str(e)}")
    farm_power_baseline = 0


# In[14]:


# Run sequential optimization
chunk_size = 8760
results = []
output_path = "C:/Users/TRIANTAFILLOS/Desktop/floris/optimal_yaw_angles.h5"
full_results_output_path = "C:/Users/TRIANTAFILLOS/Desktop/floris/hourly_optimal_yaws.h5"
checkpoint_file = "C:/Users/TRIANTAFILLOS/Desktop/floris/partial_results.h5"


# In[ ]:


start_total = time.time()
for chunk_idx, start_idx in enumerate(range(0, len(data), chunk_size)):
    chunk = data.iloc[start_idx:start_idx + chunk_size]
    unique_chunk_conditions = chunk[['wind_speeds', 'wind_directions', 'turbulence_intensities']].drop_duplicates()
    n_chunk_conditions = len(unique_chunk_conditions)
    print(f"Processing chunk {chunk_idx + 1}, rows {start_idx} to {start_idx + len(chunk) - 1}, unique conditions: {n_chunk_conditions}")

    chunk_results = []
    try:
        for idx, (_, row) in enumerate(unique_chunk_conditions.iterrows()):
            result = process_condition(row, idx, n_chunk_conditions, FModel, checkpoint_file)
            if result is not None:
                chunk_results.append(result)
        results.extend(chunk_results)
        print(f"Chunk {chunk_idx + 1} completed, {len(chunk_results)} successful results")
        
        # Save chunk results to HDF5
        if chunk_results:
            pd.DataFrame(chunk_results).to_hdf(output_path, key='data', mode='a', append=True)
        # Save cache
        with open(cache_file, 'wb') as f:
            pickle.dump(condition_cache, f)
    except KeyboardInterrupt:
        print("Script interrupted by user. Saving partial results...")
        break
    except Exception as e:
        print(f"Chunk {chunk_idx + 1} failed: {str(e)}")
        logging.error(f"Chunk {chunk_idx + 1} failed: {str(e)}")
    
    gc.collect()

print(f"Optimization completed in {(time.time() - start_total)/60:.2f} minutes")
print(f"Number of successful results: {len(results)}")


# In[ ]:


# Save final results
if results:
    pd.DataFrame(results).to_hdf(output_path, key='data', mode='w')
    print(f"Results saved to {output_path}")
else:
    print("No results to save due to empty results list")

# Merge with original data
if results:
    full_results = pd.merge(
        data,
        pd.DataFrame(results),
        on=['wind_speeds', 'wind_directions', 'turbulence_intensities'],
        how='left'
    )
    full_results['Total_Power_opt'] = full_results['Total_Power_opt'] / 1000000.0
    full_results['Total_Power_baseline'] = full_results['Total_Power_baseline'] / 1000000.0
    full_results.to_hdf(full_results_output_path, key='data', mode='w')
    print(f"Full results saved to {full_results_output_path}")

    farm_power_opt_total = full_results['Total_Power_opt'].sum()
    farm_power_baseline_total = full_results['Total_Power_baseline'].sum()
    yaw_opt_dif = (farm_power_opt_total - farm_power_baseline_total) / farm_power_baseline_total * 100 if farm_power_baseline_total > 0 else 0
    print(f"Power difference with yaw optimization: {yaw_opt_dif:.2f}%")
    print(full_results.head())
    print(f"Total optimized power: {farm_power_opt_total:.2f} MW")
    print(f"Total baseline power: {farm_power_baseline_total:.2f} MW")
else:
    print("Skipping merge and power difference calculation due to empty results")


# In[ ]:


if os.path.exists(checkpoint_file):
    os.remove(checkpoint_file)
    print(f"Checkpoint file {checkpoint_file} removed")


# In[ ]:




