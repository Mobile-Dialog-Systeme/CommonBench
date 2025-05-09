# CommonBench

This is a Benmark Dataset based on  Mozilla Common Voice (MCV)

## Download
To download the MCV-Dataset you can use the download_data.py script. While it makes the process easier, currently there is no way to directly download the entire dataset at once. For every Language there is a separate download link you can only access when providing your e-mail and agreeing to the terms and conditions.
You can copy these individual links into the download script. Which downloads the splits in sequence and unpacks them afterwards. 

Make sure you have enough disk-space on your device. The entire unzipped 16.1 set comprises about 725Gb

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







