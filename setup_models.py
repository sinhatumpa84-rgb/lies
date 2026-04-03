#!/usr/bin/env python3
"""
TruthLens AI - Model Training Quick Setup
Automates the model training process
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(num, text):
    """Print step indicator"""
    print(f"  [{num}] {text}")

def run_command(cmd, description):
    """Run shell command and report status"""
    try:
        print_step("→", description)
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode == 0:
            print(f"      ✓ Success\n")
            return True
        else:
            print(f"      ✗ Failed (exit code: {result.returncode})\n")
            return False
    except Exception as e:
        print(f"      ✗ Error: {e}\n")
        return False

def check_file_exists(filepath, description):
    """Check if file exists"""
    if Path(filepath).exists():
        print_step("✓", f"{description} found")
        return True
    else:
        print_step("✗", f"{description} NOT FOUND")
        return False

def main():
    print_header("TRUTHLENS AI - MODEL TRAINING SETUP")
    
    # Get backend directory
    backend_dir = Path(__file__).parent
    assets_dir = backend_dir.parent / "assets"
    data_file = assets_dir / "dailydialog.csv"
    
    print("Checking prerequisites...\n")
    
    # Step 1: Check data file
    if not check_file_exists(data_file, "Dataset (dailydialog.csv)"):
        print("\n⚠️  ERROR: dailydialog.csv not found!")
        print(f"Expected location: {data_file}\n")
        sys.exit(1)
    
    # Step 2: Check Python version
    if sys.version_info >= (3, 8):
        print_step("✓", f"Python version: {sys.version.split()[0]}")
    else:
        print_step("✗", f"Python 3.8+ required (found {sys.version.split()[0]})")
        sys.exit(1)
    
    # Step 3: Install dependencies
    print_header("INSTALLING DEPENDENCIES")
    
    print_step("1", "Upgrading pip")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Installing pip")
    
    print_step("2", "Installing Python packages")
    if not run_command(
        f"{sys.executable} -m pip install -r {backend_dir.parent}/requirements.txt",
        "Installing packages from requirements.txt"
    ):
        print("⚠️  Some packages may have failed to install.")
        print("This might be okay - continue with caution.\n")
    
    print_step("3", "Downloading spaCy model")
    run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading en_core_web_sm"
    )
    
    # Step 4: Train models
    print_header("TRAINING MODELS")
    
    print("This step trains ML models using your dataset.")
    print("It may take 5-15 minutes depending on your computer.\n")
    
    train_script = backend_dir / "train_sentiment_model.py"
    
    if not run_command(
        f"cd {backend_dir} && {sys.executable} train_sentiment_model.py",
        "Running training script (this may take a few minutes)"
    ):
        print("⚠️  Training failed. Check error messages above.")
        sys.exit(1)
    
    # Step 5: Verify output
    print_header("VERIFYING MODELS")
    
    model_dir = backend_dir / "app" / "models" / "trained"
    model_files = [
        ("tfidf_random_forest.pkl", "TF-IDF Random Forest Model"),
        ("tfidf_lightgbm.pkl", "TF-IDF LightGBM Model"),
        ("ensemble_model.pkl", "Ensemble Model"),
    ]
    
    vectorizer_dir = backend_dir / "app" / "vectorizers"
    vectorizer_files = [
        ("tfidf_vectorizer.pkl", "TF-IDF Vectorizer"),
    ]
    
    models_okay = True
    for filename, description in model_files:
        filepath = model_dir / filename
        if check_file_exists(filepath, f"  {description}"):
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"      Size: {size_mb:.2f} MB\n")
        else:
            models_okay = False
    
    for filename, description in vectorizer_files:
        filepath = vectorizer_dir / filename
        if not check_file_exists(filepath, f"  {description}"):
            models_okay = False
    
    if not models_okay:
        print("\n⚠️  Some model files are missing!")
        sys.exit(1)
    
    # Success!
    print_header("✓ SETUP COMPLETE!")
    
    print("Your models are ready to use. Next steps:\n")
    print("  1. Start the API server:")
    print(f"     cd {backend_dir}")
    print(f"     python -m uvicorn app.main:app --reload\n")
    
    print("  2. Test sentiment prediction:")
    print("     from app.models.inference import predict_sentiment")
    print("     result = predict_sentiment('I am very happy!')")
    print("     print(result)\n")
    
    print("  3. Integration:")
    print("     Models are automatically loaded in API endpoints\n")
    
    print("For more details, see:")
    print(f"  - {backend_dir.parent}/docs/MODEL_TRAINING_GUIDE.md\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}\n")
        sys.exit(1)
