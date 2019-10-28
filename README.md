# SiteLang

Uses BeautifulSoup to parse webpages and get language attribute from <html> tag if present. Also uses TextBlob to detect page language.

```
Expects .csv with hostnames in first column.
Outputs .csv with columns:
    header_lang, TextBlob_lang, guess1_lang, guess2_lang, error_T/F, site
'guess1_lang' uses 'header_lang' if exists, else 'TextBlob_lang'.
'guess2_lang' uses 'TextBlob_lang' if exists, else 'header_lang'.
```
