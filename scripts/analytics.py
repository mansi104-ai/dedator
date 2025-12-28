import pandas as pd
import numpy as np
from typing import List, Dict, Any
from schemas import CrawlResults, AnalyticsOutput, Metrics, ChartData, TableData, TimelineData

def process_analytics(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates crawl results and computes comprehensive analytics.
    """
    crawl_results = CrawlResults(**raw_data)
    pages = crawl_results.crawl_results
    
    if not pages:
        return {}

    # Convert to DataFrame for easier processing
    df_meta = pd.DataFrame([p.metadata.model_dump() for p in pages])
    df_data = pd.DataFrame([p.extracted_data.model_dump() for p in pages])
    
    # 1. Basic Metrics
    total_pages = len(pages)
    avg_resp_time = df_meta['response_time_ms'].mean()
    min_resp_time = df_meta['response_time_ms'].min()
    max_resp_time = df_meta['response_time_ms'].max()
    
    # 2. Links Analysis
    internal_links_total = df_data['internal_links'].apply(len).sum()
    external_links_total = df_data['links'].apply(len).sum() - internal_links_total
    
    # 3. Heading Distribution
    all_headings = [h for sublist in df_data['headings'] for h in sublist]
    # Simple heuristic: filter by tag if provided, otherwise assume mixed list
    # For this implementation, we'll just count total and distribution if tags were present
    # Since the input is just "list of strings", we'll simulate distribution for demo
    heading_dist = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}
    for h in all_headings:
        # Placeholder logic: in real world, scraper would provide tag
        heading_dist["h1"] += 1 

    # 4. Image Alt-Text Coverage
    all_images = [img for sublist in df_data['images'] for img in sublist]
    images_with_alt = [img for img in all_images if img.get('alt')]
    alt_coverage = (len(images_with_alt) / len(all_images) * 100) if all_images else 0
    
    # 5. Technology Frequency
    all_tech = [t for sublist in df_data['detected_tech'] for t in sublist]
    tech_freq = pd.Series(all_tech).value_counts().to_dict()
    
    # 6. Error Breakdown
    error_counts = df_meta[df_meta['status_code'] >= 400]['status_code'].value_counts().to_dict()

    # Construct Dashboard-friendly JSON
    output = {
        "metrics": {
            "total_pages": total_pages,
            "avg_response_time": float(avg_resp_time),
            "alt_text_coverage": float(alt_coverage),
            "internal_links": int(internal_links_total),
            "external_links": int(external_links_total)
        },
        "charts": {
            "response_time_distribution": {
                "labels": df_meta['scraped_at'].tolist(),
                "values": df_meta['response_time_ms'].tolist()
            },
            "tech_stack": {
                "labels": list(tech_freq.keys()),
                "values": list(tech_freq.values())
            }
        },
        "tables": {
            "slowest_pages": df_meta.sort_values('response_time_ms', ascending=False).head(5).to_dict('records'),
            "error_log": df_meta[df_meta['status_code'] >= 400].to_dict('records')
        },
        "timelines": {
            "crawl_history": df_meta[['scraped_at', 'status_code']].to_dict('records')
        }
    }
    
    return output
