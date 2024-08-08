import shutil
import urllib.request
import logging
import shutil
from pathlib import Path


URLS_FULL = {
    "Abkhaz":  ,
    "Afrikaans":  ,
    "Albanian":  ,
    "Amharic":  ,
    "Arabic":  ,
    "Armenian":  ,
    "Assamese":  ,
    "Azerbajan":  ,
    "Asturian":  ,
    "Basaa":  ,
    "Bashkir":  ,
    "Basque":  ,
    "Belarusian":  ,
    "Bengali":  ,
    "Breton": ,
    "Bulgarian":  ,
    "Cantonese":  ,
    "Catalan":  ,
    "Central_Kurdish":  ,
    "Chinese_CN":  ,
    "Chinese_HK":  ,
    "Chinese_TW":  ,
    "Chuvash":  ,
    "Czech":  ,
    "Danish":  ,
    "Dhivehi":  ,
    "Dioula":  ,
    "Dutch":  ,
    "English":  ,
    "Erzya":  ,
    "Esperanto":  ,
    "Estonian":  ,
    "Finnish":  ,
    "French":  ,
    "Frisian":  ,
    "Galician":  ,
    "Georgian":  ,
    "German":  ,
    "Greek":  ,
    "Guarani":  ,
    "Haka_Chin":  ,
    "Hausa":  ,
    "Hebrew":  ,
    "Hill_Mari":  ,
    "Hindi":  ,
    "Hungarian":  ,
    "Icelandic":  ,
    "Igbo":  ,
    "Indonesian":  ,
    "Interlingua":  ,
    "Irish":  ,
    "Italian":  ,
    "Japanese":  ,
    "Kabyle":  ,
    "Kazakh":  ,
    "Kinyarwanda":  ,
    "Korean":  ,
    "Kurmanji_Kurdish":  ,
    "Kyrgiz":  ,
    "Lao":  ,
    "Latgalian":  ,
    "Latvian":  ,
    "Ligurian":  ,
    "Lithuanian":  ,
    "Luganda":  ,
    "Macedonian":  ,
    "Malayalam":  ,
    "Maltese":  ,
    "Marathi":  ,
    "Maedow_Mari":  ,
    "Moksha":  ,
    "Mongolian":  ,
    "Nepali":  ,
    "Norwegian_Nyrosk":  ,
    "Occitan":  ,
    "Odia":  ,
    "Ossetian":  ,
    "Pashto":  ,
    "Persian":  ,
    "Polish":  ,
    "Portugese":  ,
    "Punjabi":  ,
    "Quechua_Chanka":  ,
    "Romanian":  ,
    "Romansh_Sulvian":  ,
    "Romansh_Valladsh":  ,
    "Russian":  ,
    "Sakha":  ,
    "Santali_O":  ,
    "Saraiki": ,
    "Sardinian":  ,
    "Serbian":  ,
    "Slovak":  ,
    "Slovenian":  ,
    "Sorbian_upper":  ,
    "Spanish":  ,
    "Swahili":  ,
    "Swedish":  ,
    "Taiwanese":  ,
    "Tamazight":  ,
    "Tamil":  ,
    "Tatar":  ,
    "Telugu":  ,
    "Thai":  ,
    "Tigre":  ,
    "Tigrinya":  ,
    "Tokipona":  ,
    "Turkish":  ,
    "Turkmen":  ,
    "Twi":  ,
    "Ukranian":  ,
    "Urdu":  ,
    "Uygur":  ,
    "Uzbek":  ,
    "Vietnamese":  ,
    "Votic":  ,
    "Welsh":  ,
    "Puebla_Nahuatl":  ,
    "Yiddish":  ,
    "Yoruba":  ,
}

def __maybe_download_file(source_url, destination_path):
    if not destination_path.exists():
        logging.info(f"Downloading data: {source_url} --> {destination_path}")
        tmp_file_path = destination_path.with_suffix(".tmp")
        urllib.request.urlretrieve(source_url, filename=tmp_file_path)
        tmp_file_path.rename(destination_path)
    else:
        logging.info(f"Skipped downloading data because it exists: {destination_path}")


def __maybe_extract_file(filepath, data_dir):
    logging.info(f"Unzipping data: {filepath} --> {data_dir}")
    shutil.unpack_archive(filepath, data_dir)
    logging.info(f"Unzipping data is complete: {filepath}.")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    dataset_root = Path("path/to/dataset/root")
    data_source = URLS_FULL_2

    # download and unzip dataset stats

    for _, data_url in data_source.items():
        __maybe_download_file(data_url, dataset_root / Path(data_url).name.split("?")[0])
    for _, data_url in data_source.items():
        __maybe_extract_file(dataset_root / Path(data_url).name.split("?")[0], dataset_root)