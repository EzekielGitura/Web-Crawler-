# Web Crawler Documentation

## 🌐 Overview

This Web Crawler is a sophisticated, multi-threaded web exploration tool designed for comprehensive and efficient website analysis. It goes beyond basic crawling by providing robust features, error handling, and persistent storage.

## 🚀 Key Features

1. **Multi-Threaded Crawling**
   - Concurrent URL processing
   - Configurable thread count
   - Intelligent link management

2. **Intelligent URL Handling**
   - URL validation
   - Link normalization
   - Domain-specific crawling

3. **Persistent Storage**
   - SQLite database integration
   - Automatic result recording
   - Easy data retrieval

4. **Advanced Error Management**
   - Comprehensive exception handling
   - Detailed logging
   - Crawler resilience

5. **Performance Monitoring**
   - Crawl depth tracking
   - Execution time measurement
   - Comprehensive reporting

## 📦 Dependencies

Install required libraries:
```bash
pip install requests beautifulsoup4
```

## 🛠 Usage

```bash
python web_crawler.py https://example.com
```

### Configuration Parameters
- `base_url`: Starting website URL
- `max_depth`: Maximum link traversal depth (default: 3)
- `max_pages`: Maximum pages to crawl (default: 100)
- `num_threads`: Concurrent crawling threads (default: 5)

## 📊 Output

The crawler generates a JSON report with:
- Total pages crawled
- Maximum depth reached
- Execution time
- Error count
- Visited URLs

## 🔒 Best Practices

1. Respect `robots.txt`
2. Add delays between requests
3. Use appropriate user agents
4. Obtain website owner's permission
