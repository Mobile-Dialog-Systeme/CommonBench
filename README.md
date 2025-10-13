# CommonBench

This is a Benmark Dataset based on  Mozilla Common Voice (MCV)
This directory contains utilities for downloading audio files from Mozilla Common Voice datasets for the CommonBench speaker verification benchmark.

## Quick Start

### Prerequisites

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

The main download script automatically downloads comparison files and audio data:

```bash
# Download audio files for all languages (automatically downloads comparison files)
python download_from_csv.py

# Download for specific language only
python download_from_csv.py --language en --output-dir english_audio

# Use different Common Voice version
python download_from_csv.py --version 16_1

# Use local comparison file instead of auto-download
python download_from_csv.py --files-csv local_comparison_files.csv
```

## Download Scripts

### `download_from_csv.py` - Main Download Script

**Features:**
- **Automatic comparison file download**: Downloads comparison data automatically if not found locally
- **Multi-version support**: Compatible with Common Voice 16.0, 16.1, and 17.0
- **Streaming and full dataset modes**: Choose between efficient streaming or full dataset download
- **Language filtering**: Download specific languages or limit number of languages for testing
- **Comprehensive reporting**: Detailed statistics, missing files reports, and progress tracking
- **Smart exclusions**: Automatically skips languages with known poor results

**Arguments:**
- `--files-csv, -f`: CSV file with language,filename pairs (auto-downloads if missing)
- `--comparison-url`: Custom URL for comparison files (default: official CommonBench URL)
- `--output-dir, -o`: Output directory for downloaded files (default: comparison_audio)
- `--language, -l`: Download files for specific language only
- `--max-languages, -m`: Maximum number of languages to process (for testing)
- `--version, -v`: Common Voice version [16_0, 16_1, 17_0] (default: 17_0)
- `--no-streaming`: Use full dataset download mode instead of streaming


**Output Structure:**
```
output_dir/
├── language1/
│   └── clips/
│       ├── audio_file1.mp3
│       └── audio_file2.mp3
├── language2/
│   └── clips/
│       └── ...
├── download_statistics.json
└── missing_files_report.txt
```

### Language Support and Limitations

**Automatically Supported Languages:**
The script supports most languages in CommonBench comparison data, with automatic exclusion of problematic languages:

**Excluded Languages (require manual download):**
- `be` (Belarusian)
- `en` (English) 
- `zh-CN` (Chinese Simplified)
- `zh-HK` (Chinese Hong Kong)
- `zh-TW` (Chinese Traditional)
- `zu` (Zulu)
- `zza` (Zazaki)

These languages had poor download success rates and must be downloaded manually using traditional methods.


## Manual Download for Excluded Languages

For languages that are excluded from automatic download (`be`, `en`, `zh-CN`, `zh-HK`, `zh-TW`, `zu`, `zza`), you need to use the traditional Mozilla Common Voice download process:

1. Visit [Mozilla Common Voice Downloads](https://commonvoice.mozilla.org/datasets)
2. Select your desired language and version
3. Provide email and agree to terms and conditions
4. Download individual language packs
5. Extract and organize files manually

## System Requirements

**Disk Space:** Plan for substantial storage requirements:
- Common Voice 16.1 complete: ~725GB uncompressed
- Individual languages: 100MB - 50GB depending on language size
- CommonBench subset: Varies by selected languages

## List of Comparisons

The list of comparisons can be found [here](https://cloud.ovgu.de/s/MGXi8ijXHSpsjEc).
We update the list, if a donor request the deletion of their data.

## List of Speakers

The list of speaker IDs, corresponding languages and pirmary languages (language with most donations) can be found [here](https://cloud.ovgu.de/s/MGXi8ijXHSpsjEc).
We update the list, if a donor request the deletion of their data.

## General Information
Composition:
- 11,793 unique speakers, 
- 4.7 million samples, 
- 101 languages.

Gender distribution: 
- 43.2% male, 
- 14% female, 
- 0.8% other, 
- 38% undisclosed.

<img width="348" alt="image" src="https://github.com/user-attachments/assets/7a40771a-fd88-4ad3-9935-8fc4b2eb1b60">

## Citation

Please cite the paper below if you make use of the Benchmark or refined Dataset:

```bibtex

@inproceedings{hintz24_spsc,
  title     = {CommonBench: A larger Scale Speaker Verification Benchmark},
  author    = {Jan Hintz and Ingo Siegert},
  year      = {2024},
  booktitle = {4th Symposium on Security and Privacy in Speech Communication},
  pages     = {17--20},
  doi       = {10.21437/SPSC.2024-3},
}

```







