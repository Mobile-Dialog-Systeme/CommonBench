#!/usr/bin/env python3
"""
Download audio files from a CSV list of files organized by language.
Much more efficient than parsing the original comparison file each time.
"""

import csv
import os
import time
from pathlib import Path
from datasets import load_dataset
from collections import defaultdict
import argparse
import requests
import tempfile
import zipfile
import shutil

def download_comparison_files(url, temp_dir=None):
    """Download and extract comparison files from the provided URL."""
    
    print(f"Downloading comparison files from: {url}")
    
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="comparison_files_")
    
    try:
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Determine file type from content-type or URL
        content_type = response.headers.get('content-type', '').lower()
        
        if 'zip' in content_type or url.endswith('.zip'):
            # Handle ZIP file
            zip_path = Path(temp_dir) / "comparison_files.zip"
            
            print("Downloading ZIP file...")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("Extracting files...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the CSV file in extracted contents
            csv_files = list(Path(temp_dir).glob("**/*.csv"))
            if not csv_files:
                raise FileNotFoundError("No CSV files found in downloaded archive")
            
            # Use the first CSV file found (assuming it's the comparison file)
            comparison_csv = csv_files[0]
            
        elif 'csv' in content_type or url.endswith('.csv'):
            # Handle direct CSV file
            csv_path = Path(temp_dir) / "comparison_files.csv"
            
            print("Downloading CSV file...")
            with open(csv_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            comparison_csv = csv_path
            
        else:
            # Default to CSV download for unknown content types
            csv_path = Path(temp_dir) / "comparison_files.csv"
            
            print("Downloading as CSV file (default)...")
            with open(csv_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            comparison_csv = csv_path
        
        print(f"Found comparison file: {comparison_csv}")
        return str(comparison_csv), temp_dir
        
    except Exception as e:
        # Clean up on error
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        raise e

def load_files_to_download(csv_file, target_language=None):
    """Load the list of files to download from CSV, optionally filtered by language."""
    
    print(f"Loading file list from: {csv_file}")
    
    files_by_language = defaultdict(set)
    total_files = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            language = row['language']
            filename = row['filename']
            
            # Filter by language if specified
            if target_language and language != target_language:
                continue
                
            files_by_language[language].add(filename)
            total_files += 1
    
    if target_language:
        print(f"Loaded {total_files:,} files for language: {target_language}")
    else:
        print(f"Loaded {total_files:,} files across {len(files_by_language)} languages")
        for lang in sorted(files_by_language.keys())[:10]:  # Show first 10 languages
            print(f"   {lang}: {len(files_by_language[lang]):,} files")
        if len(files_by_language) > 10:
            print(f"   ... and {len(files_by_language) - 10} more languages")
    
    return dict(files_by_language)

def download_files_for_language(language, target_files, base_dir, dataset_version="17_0", use_streaming=True):
    """Download specific files for a given language."""
    
    # Skip languages with poor download results or known issues
    skip_languages = {"be", "en", "zh-CN", "zh-HK", "zh-TW", "zu", "zza"}
    if language in skip_languages:
        print(f"\nSkipping {language} (excluded due to poor download results or missing in HF database)")
        return 0, len(target_files), list(target_files)
    
    print(f"\nDownloading {len(target_files):,} files for {language} using CV {dataset_version}")
    print(f"Mode: {'Streaming' if use_streaming else 'Full dataset download'}")
    
    # Create output directory
    output_dir = Path(base_dir) / language / "clips"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Dataset name based on version
    dataset_name = f"mozilla-foundation/common_voice_{dataset_version}"
    
    try:
        print(f"Dataset preparation for {language}")
        
        downloaded_count = 0
        processed_count = 0
        start_time = time.time()
        found_files = set()
        
        # Determine splits based on version
        if dataset_version in ["17_0"]:
            splits_to_check = ["validated", "train", "test", "other", "invalidated"]
        elif dataset_version in ["16_1", "16_0"]:
            splits_to_check = ["validation", "train", "test", "other", "invalidated"]
        else:
            # Default splits, will try both
            splits_to_check = ["validated", "validation", "train", "test", "other", "invalidated"]
        
        if use_streaming:
            return download_streaming_mode(language, target_files, output_dir, dataset_name, splits_to_check, start_time)
        else:
            return download_full_dataset_mode(language, target_files, output_dir, dataset_name, splits_to_check, start_time)
            
    except Exception as e:
        print(f"Error downloading files for {language}: {e}")
        import traceback
        traceback.print_exc()
        return 0, len(target_files), list(target_files)

def download_streaming_mode(language, target_files, output_dir, dataset_name, splits_to_check, start_time):
    """Download files using streaming mode - processes samples one by one."""
    
    downloaded_count = 0
    processed_count = 0
    found_files = set()
    
    for split_name in splits_to_check:
        if downloaded_count >= len(target_files):
            break
            
        missing_files = target_files - found_files
        if not missing_files:
            break
            
        print(f"Checking '{split_name}' split for {len(missing_files)} remaining files...")
        
        try:
            dataset = load_dataset(
                dataset_name,
                name=language,
                split=split_name,
                streaming=True,
                trust_remote_code=True,
                verification_mode="no_checks"
            )
            
            for raw_sample in dataset._ex_iterable:
                processed_count += 1
                
                # Show progress
                if processed_count % 500 == 0:
                    elapsed_time = time.time() - start_time
                    elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
                    rate = processed_count / elapsed_time if elapsed_time > 0 else 0
                    print(f"\rDownloading {language}...: {downloaded_count}/{len(target_files)} [{elapsed_str}, {rate:.0f}it/s]", end='', flush=True)
                
                # Parse raw sample
                if isinstance(raw_sample, tuple) and len(raw_sample) == 2:
                    file_path, data_dict = raw_sample
                    
                    sample_path = data_dict.get('path', '')
                    
                    # Extract filename from path
                    if sample_path and '/' in sample_path:
                        filename = Path(sample_path).name
                        
                        # Check if this is a file we need
                        if filename in missing_files:
                            # Get audio data
                            audio_data = data_dict.get('audio', {})
                            if audio_data and 'bytes' in audio_data:
                                
                                # Write audio file
                                output_file = output_dir / filename
                                try:
                                    with open(output_file, 'wb') as f:
                                        f.write(audio_data['bytes'])
                                    
                                    downloaded_count += 1
                                    found_files.add(filename)
                                    missing_files.remove(filename)
                                    
                                except Exception as e:
                                    print(f"\nFailed to write {filename}: {e}")
                            else:
                                print(f"\nNo audio data for {filename}")
                
                # Stop if we've found all remaining files
                if not missing_files:
                    break
                    
        except Exception as e:
            print(f"\nCould not access '{split_name}' split for {language}: {e}")
            continue
    
    # Final progress update
    elapsed_time = time.time() - start_time
    elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
    rate = processed_count / elapsed_time if elapsed_time > 0 else 0
    print(f"\rDownloading {language}...: {downloaded_count}/{len(target_files)} [{elapsed_str}, {rate:.0f}it/s]")
    
    success_rate = (downloaded_count / len(target_files)) * 100 if target_files else 0
    print(f"Downloaded {downloaded_count:,}/{len(target_files):,} files ({success_rate:.1f}%)")
    
    missing_files = target_files - found_files
    if missing_files:
        missing_count = len(missing_files)
        print(f"Missing {missing_count:,} files")
    
    return downloaded_count, len(target_files), list(missing_files)

def download_full_dataset_mode(language, target_files, output_dir, dataset_name, splits_to_check, start_time):
    """Download entire dataset first, then filter and save only needed files."""
    
    print(f"Loading full dataset for {language} (this may take longer initially)...")
    
    downloaded_count = 0
    processed_count = 0
    found_files = set()
    all_samples = {}
    
    # First pass: Load all data and find matching files
    for split_name in splits_to_check:
        print(f"Loading '{split_name}' split...")
        
        try:
            dataset = load_dataset(
                dataset_name,
                name=language,
                split=split_name,
                trust_remote_code=True,
                verification_mode="no_checks"
            )
            
            print(f"  Loaded {len(dataset):,} samples from {split_name}")
            
            # Check each sample for matches
            for i, sample in enumerate(dataset):
                processed_count += 1
                
                if processed_count % 1000 == 0:
                    elapsed_time = time.time() - start_time
                    print(f"  Analyzing samples: {processed_count:,} processed")
                
                sample_path = sample.get('path', '')
                if sample_path and '/' in sample_path:
                    filename = Path(sample_path).name
                    
                    # Check if this is a file we need
                    if filename in target_files:
                        all_samples[filename] = sample
                        found_files.add(filename)
                        
        except Exception as e:
            print(f"  Could not load '{split_name}' split for {language}: {e}")
            continue
    
    print(f"\nFound {len(found_files):,} matching files out of {len(target_files):,} needed")
    
    # Second pass: Download only the files we need
    for filename, sample in all_samples.items():
        audio_data = sample.get('audio', {})
        if audio_data and 'bytes' in audio_data:
            output_file = output_dir / filename
            try:
                with open(output_file, 'wb') as f:
                    f.write(audio_data['bytes'])
                downloaded_count += 1
                
                if downloaded_count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
                    print(f"  Saving files: {downloaded_count:,}/{len(all_samples):,} [{elapsed_str}]")
                    
            except Exception as e:
                print(f"\nFailed to write {filename}: {e}")
    
    # Final progress update
    elapsed_time = time.time() - start_time
    elapsed_str = f"{int(elapsed_time//60):02d}:{int(elapsed_time%60):02d}"
    print(f"\rDownloading {language}...: {downloaded_count}/{len(target_files)} [{elapsed_str}]")
    
    success_rate = (downloaded_count / len(target_files)) * 100 if target_files else 0
    print(f"Downloaded {downloaded_count:,}/{len(target_files):,} files ({success_rate:.1f}%)")
    
    missing_files = target_files - found_files
    if missing_files:
        missing_count = len(missing_files)
        print(f"Missing {missing_count:,} files")
    
    return downloaded_count, len(target_files), list(missing_files)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Download audio files from extracted comparison file list')
    parser.add_argument('--files-csv', '-f', type=str, default='comparison_files.csv',
                       help='CSV file with language,filename pairs (or auto-download if not found)')
    parser.add_argument('--comparison-url', type=str, 
                       default='https://cloud.ovgu.de/s/4Fi4KF9T47G3P9G/download',
                       help='URL to download comparison files if local file not found')
    parser.add_argument('--output-dir', '-o', type=str, default='comparison_audio',
                       help='Output directory for downloaded files')
    parser.add_argument('--language', '-l', type=str,
                       help='Download files for specific language only')
    parser.add_argument('--max-languages', '-m', type=int,
                       help='Maximum number of languages to process (for testing)')
    parser.add_argument('--version', '-v', type=str, default='17_0',
                       choices=['16_0', '16_1', '17_0'],
                       help='Common Voice version to use (default: 17_0)')
    parser.add_argument('--no-streaming', action='store_true', default=False,
                       help='Use full dataset download mode instead of streaming (default: streaming mode)')
    
    args = parser.parse_args()
    
    # Handle comparison file - download if not found locally
    comparison_csv_path = args.files_csv
    temp_dir_to_cleanup = None
    
    if not Path(comparison_csv_path).exists():
        print(f"Local comparison file not found: {comparison_csv_path}")
        print(f"Downloading from: {args.comparison_url}")
        try:
            comparison_csv_path, temp_dir_to_cleanup = download_comparison_files(args.comparison_url)
        except Exception as e:
            print(f"Error downloading comparison files: {e}")
            return
    
    try:
        # Load files to download
        files_by_language = load_files_to_download(comparison_csv_path, args.language)
        
        if not files_by_language:
            print("No files found to download")
            return
        
        # Limit languages if specified (useful for testing)
        if args.max_languages and not args.language:
            languages_to_process = list(files_by_language.keys())[:args.max_languages]
            files_by_language = {lang: files_by_language[lang] for lang in languages_to_process}
            print(f"Limited to first {args.max_languages} languages")
        
        # Download files for each language
        total_downloaded = 0
        total_target = 0
        successful_languages = []
        failed_languages = []
        skipped_languages = []
        all_missing_files = {}
        language_stats = []
        
        start_time = time.time()
    
        for i, (language, target_files) in enumerate(files_by_language.items(), 1):
            print(f"\nProcessing {i}/{len(files_by_language)}: {language}")
            print("-" * 50)
            
            lang_start_time = time.time()
            
            try:
                downloaded, target, missing_files = download_files_for_language(
                    language, target_files, args.output_dir, args.version, not args.no_streaming
                )
            
                lang_elapsed = time.time() - lang_start_time
                success_rate = (downloaded / target) * 100 if target > 0 else 0
                
                # Store language statistics
                lang_stats = {
                    'language': language,
                    'target_files': target,
                    'downloaded_files': downloaded,
                    'missing_files': len(missing_files),
                    'success_rate': success_rate,
                    'time_seconds': lang_elapsed
                }
                language_stats.append(lang_stats)
                
                total_downloaded += downloaded
                total_target += target
                
                if missing_files:
                    all_missing_files[language] = missing_files
                
                # Skip languages are handled in the function
                if language in {"be", "en", "zh-CN", "zh-HK", "zh-TW", "zu", "zza"}:
                    skipped_languages.append(language)
                elif downloaded > 0:
                    successful_languages.append(language)
                else:
                    failed_languages.append(language)
                    
                print(f"Language {language} completed in {lang_elapsed/60:.1f} minutes")
                    
            except Exception as e:
                print(f"Error processing {language}: {e}")
                failed_languages.append(language)
    
        # Final summary with disk usage
        elapsed_time = time.time() - start_time
        
        # Calculate disk usage
        try:
            import subprocess
            result = subprocess.run(['du', '-sh', args.output_dir], capture_output=True, text=True)
            disk_usage = result.stdout.split()[0] if result.returncode == 0 else "Unknown"
        except:
            disk_usage = "Unknown"
        
        total_missing = sum(len(missing) for missing in all_missing_files.values())
    
        print(f"\n" + "=" * 70)
        print(f"FINAL DOWNLOAD SUMMARY")
        print(f"=" * 70)
        print(f"   Dataset version: Common Voice {args.version}")
        print(f"   Download mode: {'Streaming' if not args.no_streaming else 'Full dataset'}")
        print(f"   Total languages in comparison data: {len(files_by_language)}")
        print(f"   Successful languages: {len(successful_languages)}")
        print(f"   Failed languages: {len(failed_languages)}")
        print(f"   Skipped languages (missing in HF): {len(skipped_languages)}")
        print(f"   Total files downloaded: {total_downloaded:,}")
        print(f"   Total files needed: {total_target:,}")
        print(f"   Total missing files: {total_missing:,}")
        print(f"   Overall success rate: {(total_downloaded/total_target)*100:.1f}%")
        print(f"   Total time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
        print(f"   Disk space used: {disk_usage}")
        
        # Top performing languages
        if language_stats:
            print(f"\nTop 10 languages by files downloaded:")
            sorted_by_downloaded = sorted(language_stats, key=lambda x: x['downloaded_files'], reverse=True)
            for i, stats in enumerate(sorted_by_downloaded[:10], 1):
                print(f"   {i:2d}. {stats['language']:>8}: {stats['downloaded_files']:>6,} files ({stats['success_rate']:>5.1f}%)")
            
            print(f"\nTop 10 languages by success rate (min 100 files):")
            high_volume = [s for s in language_stats if s['target_files'] >= 100]
            sorted_by_rate = sorted(high_volume, key=lambda x: x['success_rate'], reverse=True)
            for i, stats in enumerate(sorted_by_rate[:10], 1):
                print(f"   {i:2d}. {stats['language']:>8}: {stats['success_rate']:>5.1f}% ({stats['downloaded_files']:,}/{stats['target_files']:,})")
    
        if skipped_languages:
            print(f"\nSkipped languages (missing in HuggingFace):")
            for lang in skipped_languages:
                print(f"   - {lang}")
        
        if successful_languages:
            print(f"\nSuccessful languages:")
            for lang in successful_languages[:15]:  # Show first 15
                print(f"   - {lang}")
            if len(successful_languages) > 15:
                print(f"   ... and {len(successful_languages) - 15} more")
        
        if failed_languages:
            print(f"\nFailed languages:")
            for lang in failed_languages:
                print(f"   - {lang}")
    
        # Save detailed missing files report
        if all_missing_files:
            missing_report_file = Path(args.output_dir) / "missing_files_report.txt"
            print(f"\nSaving detailed missing files report to: {missing_report_file}")
            
            with open(missing_report_file, 'w') as f:
                f.write(f"Missing Files Report - Common Voice 17.0\\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
                f.write(f"Total missing files: {total_missing:,}\\n\\n")
                
                for language, missing_files in all_missing_files.items():
                    if missing_files:
                        f.write(f"\\n{language}: {len(missing_files):,} missing files\\n")
                        f.write("-" * 40 + "\\n")
                        for filename in sorted(missing_files)[:50]:  # First 50 per language
                            f.write(f"{filename}\\n")
                        if len(missing_files) > 50:
                            f.write(f"... and {len(missing_files) - 50} more\\n")
    
        # Save language statistics
        stats_file = Path(args.output_dir) / "download_statistics.json"
        print(f"Saving download statistics to: {stats_file}")
        
        import json
        final_stats = {
            'download_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'dataset_version': f'mozilla-foundation/common_voice_{args.version}',
            'download_mode': 'streaming' if not args.no_streaming else 'full_dataset',
            'total_time_minutes': elapsed_time / 60,
            'total_languages': len(files_by_language),
            'successful_languages': len(successful_languages),
            'failed_languages': len(failed_languages),
            'skipped_languages': len(skipped_languages),
            'total_files_downloaded': total_downloaded,
            'total_files_needed': total_target,
            'total_missing_files': total_missing,
            'overall_success_rate': (total_downloaded/total_target)*100 if total_target > 0 else 0,
            'disk_space_used': disk_usage,
            'language_statistics': language_stats
        }
        
        with open(stats_file, 'w') as f:
            json.dump(final_stats, f, indent=2)
        
        print(f"\\nFiles saved to: {args.output_dir}/")
        print(f"Process completed in {elapsed_time/60:.1f} minutes!")
    
    finally:
        # Clean up temporary directory if we downloaded comparison files
        if temp_dir_to_cleanup and Path(temp_dir_to_cleanup).exists():
            print(f"Cleaning up temporary files...")
            shutil.rmtree(temp_dir_to_cleanup)

if __name__ == "__main__":
    main()