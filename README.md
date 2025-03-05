# Company Researcher Agent

Company Researcher Agent searches the web for information about a user-supplied company and returns it in a structured format defined by user-supplied JSON schema.

## Overview

This tool helps automate company research by scraping and analyzing web data about target companies. It returns the information in a structured JSON format that matches your specified schema.

## Features

- Web-based company research automation
- Customizable JSON output schema
- Multiple data source support
- Structured data extraction

## How to run

```bash
git clone https://github.com/langchain-ai/company-researcher.git
cd company-researcher
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

## What you will need

* API key from OpenAI (or a provider of your choice)
* API key from [Firecrawl](https://www.firecrawl.dev/)

## Two Modes

### Pricing Researcher

This mode allows you to search multiple pricing pages and created combined JSON that you can then use to do further analysis

### Company Researcher

This mode allows you to do research on any website and create a structured output.