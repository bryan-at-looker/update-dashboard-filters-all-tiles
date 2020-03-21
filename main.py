import looker_sdk
import os
# from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# load_dotenv()
filter_field = os.environ['LOOKER_FILTERED_FIELD']

def create_query_request(q, filters):
  return looker_sdk.models.WriteQuery(
    model=q.model,
    view=q.view,
    fields=q.fields,
    pivots=q.pivots,
    fill_fields=q.fill_fields,
    filters={**q.filters, **filters},
    sorts=q.sorts,
    limit=q.limit,
    column_limit=q.column_limit,
    total=q.total,
    row_total=q.row_total,
    subtotals=q.subtotals,
    dynamic_fields=q.dynamic_fields,
    query_timezone=q.query_timezone,
    vis_config={**q.vis_config, 'show_comparison': False}
  )

def update(event, context):
  days_in_year = int(os.environ['DEFAULT_DAYS_IN_YEAR']) if os.environ['DEFAULT_DAYS_IN_YEAR'] else 365
  days = int(os.environ['DEFAULT_DAYS']) if os.environ['DEFAULT_DAYS'] else 7
  if 'queryStringParameters' in event.keys():
    if event['queryStringParameters'] and 'days' in event['queryStringParameters'].keys():
      days = int(event['queryStringParameters']['days'])
  
  new_filter = {}
  new_filter[filter_field] = "%s days ago for 7 days, %s days ago for 7 days" % (days, days+days_in_year)

  sdk = looker_sdk.init31()

  dashboard = sdk.dashboard(os.environ['LOOKER_DASHBOARD_ID'])
  els = dashboard.dashboard_elements
  for el in els:
    query = el.query
    if filter_field in query.filters.keys():
      new_query_request = create_query_request(query, new_filter)
      new_query = sdk.create_query(new_query_request)
      sdk.update_dashboard_element(
        el.id,
        looker_sdk.models.WriteDashboardElement(query_id=new_query.id)
      )

  return  {
    "statusCode": 200,
    "body": json.dumps(event)
  }