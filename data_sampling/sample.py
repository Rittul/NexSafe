import pandas as pd
import os
from pathlib import Path

# Configuration - Now points to current directory's extracted folder
SAMPLING_RATE = 10  
BASE_DIR = Path(__file__).parent / "extracted"  # ⭐ This fixes the path
OUTPUT_FILE = Path(__file__).parent / "final_training_data.csv"

def check_csv_files(day_path):
    """Check which CSV files exist in a day folder"""
    files = {}
    csv_files = list(day_path.glob("*.csv"))
    
    for csv_file in csv_files:
        name_lower = csv_file.name.lower()
        
        if 'accel' in name_lower:
            files['accelerometer'] = csv_file
        elif 'gyro' in name_lower:
            files['gyroscope'] = csv_file
        elif 'gps' in name_lower or 'location' in name_lower:
            files['gps'] = csv_file
        elif 'prox' in name_lower:
            files['proximity'] = csv_file
    
    return files

def sample_csv(file_path, sampling_rate):
    """Read and sample a CSV file"""
    try:
        df = pd.read_csv(file_path)
        sampled_df = df.iloc[::sampling_rate].reset_index(drop=True)
        print(f"  Sampled {file_path.name}: {len(df)} -> {len(sampled_df)} rows")
        return sampled_df
    except Exception as e:
        print(f"  Error reading {file_path.name}: {e}")
        return None

def process_day(day_path, behavior_label, sampling_rate):
    """Process a single day's data"""
    print(f"\nProcessing: {day_path.name}")
    
    csv_files = check_csv_files(day_path)
    
    if not csv_files:
        print(f"  ⚠️  No CSV files found, skipping")
        return None
    
    if 'accelerometer' not in csv_files or 'gyroscope' not in csv_files:
        print(f"  ⚠️  Missing required sensors (Accel or Gyro), skipping")
        return None
    
    print(f"  ✓ Found sensors: {list(csv_files.keys())}")
    
    sensor_data = {}
    
    # Sample Accelerometer
    accel_df = sample_csv(csv_files['accelerometer'], sampling_rate)
    if accel_df is None:
        return None
    sensor_data['accel'] = accel_df
    
    # Sample Gyroscope
    gyro_df = sample_csv(csv_files['gyroscope'], sampling_rate)
    if gyro_df is None:
        return None
    sensor_data['gyro'] = gyro_df
    
    # Get minimum rows
    min_rows = min(len(sensor_data['accel']), len(sensor_data['gyro']))
    sensor_data['accel'] = sensor_data['accel'].iloc[:min_rows]
    sensor_data['gyro'] = sensor_data['gyro'].iloc[:min_rows]
    
    # Sample GPS if present
    if 'gps' in csv_files:
        gps_df = sample_csv(csv_files['gps'], sampling_rate)
        if gps_df is not None:
            sensor_data['gps'] = gps_df.iloc[:min_rows]
    
    # Sample Proximity if present
    if 'proximity' in csv_files:
        prox_df = sample_csv(csv_files['proximity'], sampling_rate)
        if prox_df is not None:
            sensor_data['proximity'] = prox_df.iloc[:min_rows]
    
    # Merge all sensors
    merged_df = pd.DataFrame()
    
    # Add accelerometer
    accel_cols = sensor_data['accel'].columns.tolist()
    for i, col in enumerate(accel_cols):
        merged_df[f'accel_{i}'] = sensor_data['accel'][col]
    
    # Add gyroscope
    gyro_cols = sensor_data['gyro'].columns.tolist()
    for i, col in enumerate(gyro_cols):
        merged_df[f'gyro_{i}'] = sensor_data['gyro'][col]
    
    # Add GPS or zeros
    if 'gps' in sensor_data:
        gps_cols = sensor_data['gps'].columns.tolist()
        for i, col in enumerate(gps_cols):
            merged_df[f'gps_{i}'] = sensor_data['gps'][col]
    else:
        merged_df['gps_0'] = 0
        merged_df['gps_1'] = 0
        merged_df['gps_2'] = 0
    
    # Add Proximity or zero
    if 'proximity' in sensor_data:
        merged_df['proximity'] = sensor_data['proximity'].iloc[:, 0]
    else:
        merged_df['proximity'] = 0
    
    # Add labels
    merged_df['behavior'] = behavior_label
    merged_df['day'] = day_path.name
    
    print(f"  ✓ Merged data shape: {merged_df.shape}")
    return merged_df

def main():
    print("=" * 60)
    print("Starting Driver Behavior Data Sampling")
    print(f"Base directory: {BASE_DIR}")
    print("=" * 60)
    
    all_data = []
    
    # Process RISKY
    print("\n📊 Processing RISKY days...")
    risky_path = BASE_DIR / "risky"
    
    if risky_path.exists():
        risky_days = sorted([d for d in risky_path.iterdir() if d.is_dir()])
        print(f"Found {len(risky_days)} risky day folders")
        
        for day_folder in risky_days:
            day_data = process_day(day_folder, behavior_label=1, sampling_rate=SAMPLING_RATE)
            if day_data is not None:
                all_data.append(day_data)
    else:
        print(f"⚠️  Risky folder not found at: {risky_path}")
    
    # Process SAFE
    print("\n📊 Processing SAFE days...")
    safe_path = BASE_DIR / "safe"
    
    if safe_path.exists():
        safe_days = sorted([d for d in safe_path.iterdir() if d.is_dir()])
        print(f"Found {len(safe_days)} safe day folders")
        
        for day_folder in safe_days:
            day_data = process_day(day_folder, behavior_label=0, sampling_rate=SAMPLING_RATE)
            if day_data is not None:
                all_data.append(day_data)
    else:
        print(f"⚠️  Safe folder not found at: {safe_path}")
    
    if not all_data:
        print("\n❌ No data was processed!")
        return
    
    print("\n" + "=" * 60)
    print("Combining all data...")
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    final_df.to_csv(OUTPUT_FILE, index=False)
    
    print("\n✅ SUCCESS!")
    print("=" * 60)
    print(f"Final dataset shape: {final_df.shape}")
    print(f"Total rows: {len(final_df)}")
    print(f"\nBehavior distribution:")
    print(final_df['behavior'].value_counts())
    print(f"\nSaved to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / (1024*1024):.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    main()
