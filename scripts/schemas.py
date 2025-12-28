from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class PageMetadata(BaseModel):
    status_code: int
    response_time_ms: float
    content_size_bytes: int
    scraped_at: str

class ImageData(BaseModel):
    url: str
    alt: Optional[str] = None

class ExtractedData(BaseModel):
    headings: List[str]
    links: List[str]
    internal_links: List[str]
    images: List[Dict[str, Optional[str]]]
    detected_tech: List[str]
    content_summary: str

class PageCrawl(BaseModel):
    metadata: PageMetadata
    extracted_data: ExtractedData

class CrawlResults(BaseModel):
    crawl_results: List[PageCrawl]

# Dashboard Output Schemas
class Metrics(BaseModel):
    total_pages: int
    avg_response_time: float
    alt_text_coverage: float
    internal_links: int
    external_links: int

class ChartData(BaseModel):
    labels: List[str]
    values: List[Any]

class TableData(BaseModel):
    headers: List[str]
    rows: List[List[Any]]

class TimelineData(BaseModel):
    events: List[Dict[str, Any]]

class AnalyticsOutput(BaseModel):
    metrics: Metrics
    charts: Dict[str, ChartData]
    tables: Dict[str, Any]
    timelines: Dict[str, Any]
