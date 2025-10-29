# Page Selectors Configuration

## Overview

The Drupal News Aggregator allows you to configure custom CSS selectors for scraping web pages. This gives you precise control over which HTML elements to extract data from.

## Basic Concepts

### Two Configuration Formats

The `sources.pages` array in `config.json` supports two formats:

1. **Simple URL String** (backward compatible)
   ```json
   "pages": [
     "https://www.drupal.org/news"
   ]
   ```

2. **Object with Selectors** (advanced control)
   ```json
   "pages": [
     {
       "url": "https://www.drupal.org/news",
       "selectors": {
         "container": "article",
         "title": "h2",
         "link": "h2 a",
         "description": ".field--name-body",
         "date": "time"
       }
     }
   ]
   ```

## Selector Configuration

### Required Fields

- **`url`** - The page URL to scrape
- **`selectors.container`** - CSS selector for the container element that wraps each item
- **`selectors.title`** - CSS selector for the title element

### Optional Fields

- **`name`** - Human-readable name for this source (for logging)
- **`base_url`** - Base URL for converting relative links to absolute (default: `https://www.drupal.org`)
- **`selectors.link`** - CSS selector for the link element (defaults to `title` selector if not provided)
- **`selectors.description`** - CSS selector for the description/content element
- **`selectors.date`** - CSS selector for the date element

## CSS Selector Syntax

All selectors use standard CSS selector syntax supported by BeautifulSoup's `select()` and `select_one()` methods.

### Common Selector Patterns

#### Tag Selectors
```json
"container": "article"        // All <article> elements
"title": "h2"                 // All <h2> elements
"date": "time"                // All <time> elements
```

#### Class Selectors
```json
"container": ".news-item"     // Elements with class="news-item"
"title": ".article-title"     // Elements with class="article-title"
"description": ".summary"     // Elements with class="summary"
```

#### ID Selectors
```json
"container": "#main-content"  // Element with id="main-content"
```

#### Descendant Selectors
```json
"container": "div.content article"     // <article> inside <div class="content">
"title": "article h2"                  // <h2> inside <article>
"link": "h2 a"                         // <a> inside <h2>
```

#### Direct Child Selector
```json
"container": "div > article"           // <article> that is direct child of <div>
"description": "article > .body"       // .body that is direct child of <article>
```

#### Attribute Selectors
```json
"container": "article[data-type='news']"  // <article> with data-type="news"
"date": "time[datetime]"                  // <time> with datetime attribute
```

#### Pseudo-selectors
```json
"description": "article p:first-of-type"  // First <p> in <article>
"link": "article a:not(.external)"        // <a> without class="external"
```

#### Multiple Selectors (OR)
```json
"title": "h2, h3"                      // <h2> OR <h3>
"date": "time, .date, span.published"  // Multiple options
```

## Complete Examples

### Example 1: Drupal News Page

```json
{
  "url": "https://www.drupal.org/news",
  "name": "Drupal Official News",
  "base_url": "https://www.drupal.org",
  "selectors": {
    "container": "article.node--type-blog-post",
    "title": "h2.node__title",
    "link": "h2.node__title a",
    "description": ".field--name-body",
    "date": "time"
  }
}
```

### Example 2: Custom Blog with Specific Structure

```json
{
  "url": "https://example.com/drupal-updates",
  "name": "Example Drupal Blog",
  "base_url": "https://example.com",
  "selectors": {
    "container": "#blog-posts .post-item",
    "title": ".post-title h3",
    "link": ".post-title a",
    "description": ".post-excerpt",
    "date": ".post-meta time"
  }
}
```

### Example 3: Complex Nested Structure

```json
{
  "url": "https://www.drupal.org/planet",
  "name": "Drupal Planet",
  "selectors": {
    "container": "div.view-content > article",
    "title": "h2 a",
    "link": "h2 a",
    "description": "div.content p:first-of-type",
    "date": "footer time[datetime]"
  }
}
```

### Example 4: Using Data Attributes

```json
{
  "url": "https://events.drupal.org/",
  "name": "Drupal Events",
  "selectors": {
    "container": "article[data-type='event']",
    "title": ".event-title",
    "link": ".event-title a",
    "description": ".event-description",
    "date": "time[data-start-date]"
  }
}
```

## How It Works

### Parsing Flow

1. **Fetch HTML**: The aggregator downloads the HTML from the specified URL
2. **Find Containers**: Searches for all elements matching the `container` selector
3. **Extract From Each Container**:
   - Find title using `title` selector
   - Find link using `link` selector (or fallback to `title` if not specified)
   - Find description using `description` selector (optional)
   - Find date using `date` selector (optional)
4. **Normalize Data**:
   - Clean and truncate text
   - Convert relative URLs to absolute
   - Parse dates to ISO format
   - Filter items by date range

### Link Extraction

The aggregator is smart about extracting links:

- If `link` selector points to an `<a>` tag, it extracts the `href` attribute
- If `link` selector points to another element, it finds the first `<a>` inside
- If no link is found, it uses the source URL as fallback
- Relative URLs (starting with `/`) are converted to absolute using `base_url`

### Date Parsing

For date elements:

- First tries to extract `datetime` attribute (ISO format)
- Falls back to element text content
- Parses multiple date formats
- Filters items outside the configured timeframe

## Testing Selectors

### Browser Developer Tools

1. Open the target page in Chrome/Firefox
2. Press F12 to open Developer Tools
3. Use "Select Element" tool (Ctrl+Shift+C)
4. Click on the element you want to select
5. Right-click the element in the Elements panel → Copy → Copy selector

### Testing with Python

```python
from bs4 import BeautifulSoup
import httpx

# Fetch page
url = "https://www.drupal.org/news"
response = httpx.get(url)
soup = BeautifulSoup(response.text, "lxml")

# Test container selector
containers = soup.select("article")
print(f"Found {len(containers)} containers")

# Test title selector on first container
if containers:
    title = containers[0].select_one("h2")
    print(f"Title: {title.get_text() if title else 'Not found'}")
```

## Troubleshooting

### No Items Found

**Problem**: Aggregator returns 0 items for a page

**Solutions**:
- Verify `container` selector matches elements on the page
- Check browser console: some pages load content dynamically (JavaScript)
- Try broader selectors: `article` instead of `article.specific-class`

### Wrong Content Extracted

**Problem**: Extracted content doesn't match expected data

**Solutions**:
- Use more specific selectors with classes/IDs
- Use descendant selectors: `article > h2` instead of `article h2`
- Check the HTML structure in browser developer tools

### Relative Links Not Working

**Problem**: Links are broken or point to wrong URLs

**Solutions**:
- Set correct `base_url` for the domain
- Check if links start with `/`, `http://`, or `https://`

### Date Filtering Not Working

**Problem**: Items outside date range are included

**Solutions**:
- Verify `date` selector points to element with date info
- Check if date has `datetime` attribute
- Date parsing may fail on non-standard formats

## Best Practices

1. **Start Broad, Then Narrow**: Begin with simple selectors like `article`, then add classes as needed
2. **Use Semantic HTML**: Prefer tags like `<article>`, `<time>`, `<h2>` over generic `<div>`
3. **Test in Browser First**: Use browser dev tools to verify selectors work
4. **Provide Fallbacks**: If a selector might not match, provide alternatives: `"time, .date"`
5. **Keep It Simple**: Avoid overly complex selectors that might break with minor HTML changes
6. **Document Sources**: Use the `name` field to document what each source is

## Migration from Old Format

If you have old simple URL configurations:

```json
"pages": [
  "https://www.drupal.org/news",
  "https://www.drupal.org/planet"
]
```

They still work! The system automatically detects and handles both formats. Upgrade to selector-based config only when you need precise control.

## Advanced Features

### Multiple Container Types

Some pages have different container types. Use CSS OR selector:

```json
"container": "article, div.news-item, section.post"
```

### Conditional Selectors

Extract different descriptions based on what's available:

```json
"description": ".field--name-body, .summary, .excerpt, p:first-of-type"
```

### Excluding Elements

Skip certain containers:

```json
"container": "article:not(.sponsored):not(.advertisement)"
```

## See Also

- [BeautifulSoup CSS Selector Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors)
- [MDN CSS Selectors Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- `config.example.json` - Example configuration file
