import os
import sys
import time

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
sys.path.insert(0, r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO")

from ml.src.pipeline.extract_wesad import extract_wesad_dataset
from ml.src.pipeline.extract_physionet import extract_physionet_dataset
from ml.src.pipeline.extract_catsa import extract_catsa_dataset
from ml.src.pipeline.build_partitions import build_partitions

def main():
    start_time = time.time()
    print("==================================================", flush=True)
    print("SEPTERIA: RUNNING FEATURE EXTRACTION PIPELINE (STRICT ZERO IMPUTATION)", flush=True)
    print("==================================================\n", flush=True)
    
    dataset_root = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\Dataset"
    processed_dir = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"
    
    physionet_csv = os.path.join(processed_dir, "physionet_features.csv")
    catsa_csv = os.path.join(processed_dir, "catsa_features.csv")
    
    # 1. WESAD
    print("[Step 1/4] Extracting WESAD (15 subjects, 60s windows, Wrist + Chest Multimodal)...", flush=True)
    extract_wesad_dataset(dataset_root, processed_dir)
    
    # 2. PhysioNet
    print("\n[Step 2/4] Extracting PhysioNet Wearable (36 subjects, Stress + Aerobic + Anaerobic)...", flush=True)
    extract_physionet_dataset(dataset_root, physionet_csv)
    
    # 3. CATSA
    print("\n[Step 3/4] Extracting CATSA (50 subjects, 5 tasks)...", flush=True)
    extract_catsa_dataset(dataset_root, catsa_csv)
    
    # 4. Partitioning & Leakage Audit
    print("\n[Step 4/4] Generating Subject-Wise Partitions and Validation Audit...", flush=True)
    build_partitions()
    
    total_time = time.time() - start_time
    print(f"Pipeline Finished in {total_time:.1f} seconds.", flush=True)
    print("All processed feature tables and validation manifests generated.", flush=True)

if __name__ == "__main__":
    main()
