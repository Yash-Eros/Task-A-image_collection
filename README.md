The # Indian Cultural Dataset - Comprehensive Image Collection & Processing Pipeline

## 🎯 Project Overview

This project is a **large-scale automated image scraping, processing, and validation pipeline** designed to build a curated dataset of Indian cultural imagery. The system collects high-quality images from multiple global sources, validates them for quality (resolution, watermarks, blur detection), and organizes them into 12 culturally-themed categories.

### Key Features
- 🔄 Multi-source scraping from 8+ image APIs and repositories
- 🎨 12 Indian cultural category buckets with curated search queries
- ✅ Intelligent validation (watermark detection, resolution classification, blur detection)
- 📊 Duplicate detection and dataset statistics tracking
- ⚡ Async/concurrent downloading with rate limiting
- 🔐 Checkpoint-based resume capability for fault tolerance
- 📁 Organized output by resolution tiers (256px, 512px, 1024px, 2048px+)

---

## 📂 Project Structure

```
indian_cultural_dataset/
├── config.py                 # Configuration, API keys, bucket queries
├── scrape.py                 # Main scraper orchestration
├── requirements.txt          # Python dependencies
├── sources.md                # Documentation of image sources
├── collection_stats.csv      # Statistics on collected images
├── hashes.json               # Hash tracking for deduplication
├── .gitignore                # Git ignore rules
│
├── data/
│   ├── indian_cultural_sorted/    # Output images organized by bucket & resolution
│   │   ├── 01_people_portraits/
│   │   ├── 02_clothing_textiles/
│   │   ├── 03_architecture/
│   │   ├── ... (12 categories total)
│   │   └── 12_abstract_texture/
│   ├── rejected/              # Images that failed validation
│   │   ├── watermarked/       # Images with detected watermarks
│   │   └── blurry/            # Images that failed quality checks
│   ├── temp/                  # Temporary download storage
│   └── download_log.json      # Detailed download history
│
├── checkpoint/                # Resume checkpoints for each bucket
│   ├── 01_people_portraits.json
│   ├── 02_clothing_textiles.json
│   └── ... (one per bucket)
│
├── logs/                      # Detailed JSON logs of progress
│   ├── 1.json through 100.json
│   └── ...
│
├── src/
│   ├── scraper/              # Core scraping logic
│   ├── sources/              # Source API integrations
│   ├── utils/                # Utility functions
│   └── validation/           # Image validation modules
│
├── wmdetection/              # Watermark detection module
│   ├── models/               # ML model weights
│   ├── pipelines/            # Detection pipeline
│   └── dataset/              # Training data
│
└── tests/                     # Test suite
```

---

## 🎨 Dataset Categories (12 Buckets)

The dataset is organized into 12 culturally-specific categories:

1. **01_people_portraits** - Portrait photography of Indian people
2. **02_clothing_textiles** - Traditional dress, sarees, fabrics, embroidery
3. **03_architecture** - Temples, monuments, traditional buildings
4. **04_landscape_nature** - Natural landscapes, geographical features
5. **05_urban_street** - Urban street scenes, city life
6. **06_rural_village** - Village life and rural imagery
7. **07_food_drink** - Indian cuisine and traditional beverages
8. **08_festivals_rituals** - Ceremonies, festivals, cultural events
9. **09_objects_artifacts** - Artifacts, craftwork, traditional objects
10. **10_animals_wildlife** - Wildlife and animals
11. **11_art_design** - Traditional art forms and design
12. **12_abstract_texture** - Textures and abstract cultural patterns

---

## 🔧 Configuration & Setup

### Prerequisites
- Python 3.8+
- API keys for image sources (see `sources.md`)
- Environment variables configured in `.env` file

### API Keys Required

Configure these in your `.env` file:
```
PEXELS_API_KEY=<your-key>
PIXABAY_API_KEY=<your-key>
UNSPLASH_ACCESS_KEY=<your-key>
NYPL_API_KEY=<your-key>
EUROPEANA_API_KEY=<your-key>
SMITHSONIAN_API_KEY=<your-key>
FLICKR_API_KEY=<your-key>
```

### Installation

```bash
pip install -r requirements.txt
python download_weights.py  # Download watermark detection model
```

### Configuration (config.py)

Key settings:
- **REQUEST_DELAY** = 1.2 seconds (respect API rate limits)
- **MAX_WORKERS** = 6 (concurrent download threads)
- **WATERMARK_THRESHOLD** = 0.5 (sensitivity for watermark detection)
- **BUCKET_QUERIES** = Custom search queries per category

---

## 🚀 Usage

### Running the Scraper

```bash
# Scrape a specific bucket with target image count
python scrape.py --bucket "01_people_portraits" --target 500

# Resume from checkpoint
python scrape.py --bucket "02_clothing_textiles" --target 300
```

### How It Works

1. **Query Generation**: For each bucket, 10+ curated search queries target specific aspects (e.g., "Indian woman portrait", "Rajasthani people")
2. **Multi-Source Scraping**: Queries are distributed across 8 sources:
   - Pexels, Pixabay, Unsplash
   - NYPL Digital Collections, Europeana
   - Smithsonian Open Access, Flickr, Wikimedia Commons
3. **Download & Validation**:
   - Images are downloaded with retry logic
   - Checked for watermarks (ConvNeXt-Tiny model)
   - Analyzed for blur and resolution
4. **Organization**: Images sorted into folders by bucket → resolution tier
5. **Deduplication**: Duplicate detection using perceptual hashing
6. **Checkpointing**: Progress saved per bucket for resume capability

---

## 📊 Image Organization

Images are organized by **resolution tiers**:

```
01_people_portraits/
├── 256/      # Images 256x256 to 511x511
├── 512/      # Images 512x512 to 1023x1023
├── 1024/     # Images 1024x1024 to 2047x2047
└── 2048/     # Images 2048x2048 and larger
```

---

## ✅ Quality Control Pipeline

### 1. Watermark Detection
- Uses ConvNeXt-Tiny architecture (from boomb0om/watermark-detection)
- Confidence threshold: 0.5
- Failed images → `data/rejected/watermarked/`

### 2. Resolution Classification
- Automatically sorts by resolution tier for balanced dataset
- Target: At least 20% per resolution tier

### 3. Blur Detection
- Identifies and rejects blurry images
- Failed images → `data/rejected/blurry/`

### 4. Duplicate Detection
- Uses perceptual hashing to identify duplicates
- Prevents redundant images across sources

---

## 📈 Collection Statistics

The `collection_stats.csv` tracks:
- **Bucket**: Cultural category
- **Source**: Which API provided the image
- **count_256/512/1024/2048**: Images per resolution tier
- **total**: Total images from this source-bucket pair

Example stats:
```
01_people_portraits,pexels,0,0,2,75,77
03_architecture,pexels,0,0,9,225,234
02_clothing_textiles,pixabay,0,62,1,0,63
```

---

## 🔍 Core Components

### ImageScraper (`scrape.py`)
Main orchestration class that:
- Manages bucket-specific scraping
- Coordinates downloads and validation
- Tracks progress via checkpoints
- Logs statistics

### Image Sources (`src/sources/`)
API integrations for each image source with:
- Rate limiting respect
- Query formatting
- Response parsing
- Error handling

### Validation Modules (`src/validation/`)
- **WatermarkValidator**: ConvNeXt-Tiny watermark detection
- **ResolutionSorter**: Classifies and organizes by resolution
- **BlurDetector**: Identifies low-quality blurry images
- **Deduplicator**: Perceptual hash-based duplicate detection

### Progress Tracking
- **CheckpointManager**: Saves/restores per-bucket state
- **ProgressLogger**: Real-time scraping progress
- **DownloadLogger**: Detailed download history in JSON
- **StatsManager**: Aggregates collection statistics

---

## 📝 Image Sources Documentation

Refer to `sources.md` for detailed information on each source:
- API endpoints and authentication
- Rate limits and usage policies
- License information
- Access methods (API vs. scraping)

Key sources:
- **Pexels**: 200 req/hour, free commercial license
- **Pixabay**: 5000 req/hour, Pixabay License
- **Unsplash**: 50 req/hour, Unsplash License
- **Smithsonian**: CC0 public domain
- **NYPL**: Public domain collections
- **Europeana**: CC0 and open licenses
- **Wikimedia Commons**: Various open licenses

---

## 🛡️ Watermark Detection Model

The boomb0om/watermark-detection repository was used for model architecture (ConvNeXt-Tiny).
However, pretrained weights were not publicly available. Therefore, the architecture
was integrated into the pipeline and used for watermark detection logic.